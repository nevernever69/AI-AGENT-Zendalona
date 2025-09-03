import asyncio
from crawler.crawler import crawl_website

async def test_generic_crawl():
    # Test with a generic website
    url = "https://httpbin.org/html"
    documents = await crawl_website(url, max_pages=5, depth=1)
    print(f"Found {len(documents)} documents")
    for i, doc in enumerate(documents):
        print(f"Document {i+1}:")
        print(f"  Source: {doc.metadata.get('source', 'N/A')}")
        print(f"  Title: {doc.metadata.get('title', 'N/A')}")
        print(f"  Content preview: {doc.page_content[:100]}...")
        print()

if __name__ == "__main__":
    asyncio.run(test_generic_crawl())