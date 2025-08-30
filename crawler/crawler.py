import logging
from crawl4ai import AsyncWebCrawler
from langchain.schema import Document
from config import settings
from utils.chroma_utils import index_documents_to_chroma
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

# Setup logging
logging.basicConfig(filename=settings.log_path, level=logging.INFO)
logger = logging.getLogger(__name__)

async def crawl_website(url: str, max_pages: int, depth: int) -> list[Document]:
    logger.info(f"Starting crawl of {url} with max_pages={max_pages}, depth={depth}")
    try:
        async with AsyncWebCrawler() as crawler:
            # Crawl the main URL
            logger.info("Starting initial crawl")
            result = await crawler.arun(
                url=url,
                max_depth=depth,
                max_pages=max_pages,
                extract_blocks=True,
                bypass_cache=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
                js=False
            )
            logger.info("Initial crawl completed")
            
            if not result.success or not result.html:
                logger.error(f"Failed to crawl {url}: {result.status}")
                return []
            
            # Parse HTML with BeautifulSoup
            logger.info("Parsing HTML with BeautifulSoup")
            soup = BeautifulSoup(result.html, 'html.parser')
            logger.info("HTML parsing completed")
            
            # Get the base domain for link filtering
            parsed_url = urlparse(url)
            base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            logger.info(f"Base domain: {base_domain}")
            
            # Log the length of HTML for debugging
            logger.info(f"HTML length: {len(result.html) if result.html else 0}")
            
            # Find internal links for crawling (DO THIS BEFORE removing navigation elements!)
            internal_links = set()
            
            # Log total links found for debugging
            all_links = soup.find_all('a', href=True)
            logger.info(f"Total links found on page: {len(all_links)}")
            
            # Log first few links for debugging
            if all_links:
                logger.info(f"First 5 links: {[link.get('href') for link in all_links[:5]]}")
            
            # Find internal links BEFORE removing navigation elements
            for link in all_links:
                href = link['href']
                original_href = href  # Keep original for logging
                
                # Normalize the URL
                try:
                    # Handle relative URLs
                    if href.startswith('/'):
                        href = urljoin(base_domain, href)
                    elif href.startswith('#'):
                        # Skip anchor links
                        continue
                    elif not href.startswith('http'):
                        # Handle relative URLs like "about.html" or "../page.html"
                        href = urljoin(url, href)
                    
                    # Check if it's an internal link (same domain)
                    parsed_href = urlparse(href)
                    href_domain = f"{parsed_href.scheme}://{parsed_href.netloc}"
                    
                    if href_domain == base_domain:
                        internal_links.add(href)
                        logger.debug(f"Added internal link: {href}")
                    else:
                        logger.debug(f"Skipped external link: {href}")
                except Exception as e:
                    logger.debug(f"Error processing link {original_href}: {str(e)}")
                    continue
            
            logger.info(f"Found {len(internal_links)} internal links to crawl")
            if internal_links:
                logger.info(f"First 10 internal links: {list(internal_links)[:10]}")
            
            # Extract title
            logger.info("Extracting title")
            title = soup.title.string if soup.title else "No title found"
            logger.info(f"Title extracted: {title}")
            
            # Remove navigation menus and irrelevant elements
            logger.info("Removing navigation elements")
            for nav in soup.find_all(['nav', 'header', 'footer']):
                nav.decompose()
            logger.info("Navigation elements removed")
            
            # Extract main content
            logger.info("Extracting main content")
            try:
                main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile('content|main'))
                if not main_content:
                    main_content = soup.body
                logger.info(f"Main content element found: {main_content is not None}")
                
                content = []
                if main_content:
                    for element in main_content.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'li']):
                        text = element.get_text(strip=True)
                        if text and not text.startswith(('Select Page', 'Home')):
                            content.append(text)
                
                content_text = "\n".join(content) or "No content available"
                logger.info("Main content extracted successfully")
            except Exception as e:
                logger.error(f"Error extracting content from main page: {str(e)}")
                content_text = "No content available"
            
            logger.info("Creating main document")
            documents = [
                Document(
                    page_content=f"Title: {title}\n{content_text}",
                    metadata={"source": url, "title": title}
                )
            ]
            logger.info("Main document created")
            
            # Crawl internal pages (limit to max_pages-1 since we already have the main page)
            remaining_pages = max_pages - 1
            logger.info(f"Starting internal page crawling, {remaining_pages} pages remaining")
            
            for internal_url in internal_links:
                if remaining_pages <= 0:
                    logger.info("Reached max pages limit, stopping crawl")
                    break
                    
                logger.info(f"Attempting to crawl internal page: {internal_url}")
                try:
                    internal_result = await crawler.arun(
                        url=internal_url,
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
                        js=False
                    )
                    if internal_result and internal_result.success and internal_result.html:
                        logger.info(f"Successfully fetched internal page: {internal_url}")
                        internal_soup = BeautifulSoup(internal_result.html, 'html.parser')
                        internal_title = internal_soup.title.string if internal_soup.title else "No title found"
                        logger.info(f"Internal page title: {internal_title}")
                        
                        # Clean up the internal page content
                        for nav in internal_soup.find_all(['nav', 'header', 'footer']):
                            nav.decompose()
                        
                        internal_main = internal_soup.find('main') or internal_soup.find('article') or internal_soup.find('div', class_=re.compile('content|main')) or internal_soup.body
                        logger.info(f"Internal page main content element found: {internal_main is not None}")
                        
                        internal_content = []
                        if internal_main:
                            for element in internal_main.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'li']):
                                text = element.get_text(strip=True)
                                if text and not text.startswith(('Select Page', 'Home')):
                                    internal_content.append(text)
                        
                        internal_content_text = "\n".join(internal_content) or "No content available"
                        documents.append(
                            Document(
                                page_content=f"Title: {internal_title}\n{internal_content_text}",
                                metadata={"source": internal_url, "title": internal_title}
                            )
                        )
                        remaining_pages -= 1
                        logger.info(f"Successfully crawled and added internal page {internal_url}")
                    else:
                        logger.error(f"Failed to crawl internal page {internal_url}: {internal_result.status if internal_result else 'No result'}")
                except Exception as e:
                    logger.error(f"Exception while crawling internal page {internal_url}: {str(e)}")
            
            logger.info(f"Crawled {len(documents)} pages from {url}")
            return documents
    except Exception as e:
        logger.error(f"Error crawling {url}: {str(e)}")
        return []

async def process_and_index_url(url: str, max_pages: int, depth: int) -> int:
    documents = await crawl_website(url, max_pages, depth)
    return index_documents_to_chroma(documents, collection_name="zendalona")