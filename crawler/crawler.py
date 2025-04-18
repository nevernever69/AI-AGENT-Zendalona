import logging
from crawl4ai import AsyncWebCrawler
from langchain.schema import Document
from config import settings
from utils.chroma_utils import index_documents_to_chroma
from bs4 import BeautifulSoup
import re

# Setup logging
logging.basicConfig(filename=settings.log_path, level=logging.INFO)
logger = logging.getLogger(__name__)

async def crawl_website(url: str, max_pages: int, depth: int) -> list[Document]:
    try:
        async with AsyncWebCrawler() as crawler:
            # Crawl the main URL
            result = await crawler.arun(
                url=url,
                max_depth=depth,
                max_pages=max_pages,
                extract_blocks=True,
                bypass_cache=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
                js=False
            )
            
            if not result.success or not result.html:
                logger.error(f"Failed to crawl {url}: {result.status}")
                return []
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else "No title found"
            
            # Remove navigation menus and irrelevant elements
            for nav in soup.find_all(['nav', 'header', 'footer']):
                nav.decompose()
            
            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile('content|main'))
            if not main_content:
                main_content = soup.body
            
            content = []
            for element in main_content.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'li']):
                text = element.get_text(strip=True)
                if text and not text.startswith(('Select Page', 'Home')):
                    content.append(text)
            
            content_text = "\n".join(content) or "No content available"
            
            documents = [
                Document(
                    page_content=f"Title: {title}\n{content_text}",
                    metadata={"source": url, "title": title}
                )
            ]
            
            # Crawl project pages (e.g., those containing "accessible-")
            project_links = set()
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'accessible-' in href.lower() and href.startswith('https://zendalona.com'):
                    project_links.add(href)
            
            for project_url in project_links:
                if len(documents) >= max_pages:
                    break
                project_result = await crawler.arun(
                    url=project_url,
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
                    js=False
                )
                if project_result.success and project_result.html:
                    project_soup = BeautifulSoup(project_result.html, 'html.parser')
                    project_title = project_soup.title.string if project_soup.title else "No title found"
                    for nav in project_soup.find_all(['nav', 'header', 'footer']):
                        nav.decompose()
                    project_main = project_soup.find('main') or project_soup.find('article') or project_soup.find('div', class_=re.compile('content|main')) or project_soup.body
                    project_content = []
                    for element in project_main.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'li']):
                        text = element.get_text(strip=True)
                        if text and not text.startswith(('Select Page', 'Home')):
                            project_content.append(text)
                    project_content_text = "\n".join(project_content) or "No content available"
                    documents.append(
                        Document(
                            page_content=f"Title: {project_title}\n{project_content_text}",
                            metadata={"source": project_url, "title": project_title}
                        )
                    )
                    logger.info(f"Successfully crawled project page {project_url}")
            
            logger.info(f"Crawled {len(documents)} pages from {url}")
            return documents
    except Exception as e:
        logger.error(f"Error crawling {url}: {str(e)}")
        return []

async def process_and_index_url(url: str, max_pages: int, depth: int) -> int:
    documents = await crawl_website(url, max_pages, depth)
    return index_documents_to_chroma(documents, collection_name="zendalona")