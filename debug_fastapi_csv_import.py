import asyncio
import logging
from io import BytesIO
from fastapi import UploadFile
from routers.cache import import_cache_from_csv

# Configure logging to see detailed output
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_csv_import_via_fastapi():
    try:
        # Read the CSV file as bytes (simulating how FastAPI would receive it)
        with open('ABK_Revised_QA.csv', 'rb') as f:
            file_content = f.read()
        
        print(f"File size: {len(file_content)} bytes")
        
        # Create an UploadFile object similar to what FastAPI would create
        upload_file = UploadFile(
            filename="ABK_Revised_QA.csv",
            file=BytesIO(file_content),
            headers={}
        )
        
        # Call the FastAPI endpoint function directly
        print("Calling import_cache_from_csv function...")
        result = await import_cache_from_csv(upload_file)
        print(f"Import result: {result}")
        
    except Exception as e:
        print(f"Failed to import CSV: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_csv_import_via_fastapi())