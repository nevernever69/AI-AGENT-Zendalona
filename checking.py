import asyncio
from crawl4ai import AsyncWebCrawler
import logging

logging.basicConfig(level=logging.INFO)

async def test_crawl():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://zendalona.com",
            max_depth=2,
            max_pages=10,
            extract_blocks=True,
            bypass_cache=True
        )
        logging.info(f"Result: {result}")
        logging.info(f"Extracted content: {result.extracted_content}")

asyncio.run(test_crawl())
