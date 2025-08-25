import csv
import io
import logging
from utils.cache_utils import add_to_cache

# Configure logging to see detailed output
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_csv_import():
    try:
        # Read the CSV file
        with open('ABK_Revised_QA.csv', 'rb') as f:
            content = f.read()
        
        print(f"File size: {len(content)} bytes")
        
        # Try decoding with UTF-8 first
        try:
            content_decoded = content.decode('utf-8')
            print("Successfully decoded with UTF-8")
        except UnicodeDecodeError:
            # If UTF-8 fails, try latin-1 as a fallback
            content_decoded = content.decode('latin-1')
            print("Successfully decoded with latin-1")

        csv_reader = csv.reader(io.StringIO(content_decoded))
        header = next(csv_reader)  # Skip header
        print(f"Header: {header}")
        
        print("Starting CSV import...")
        
        for i, row in enumerate(csv_reader):
            if not row:  # Skip empty rows
                print(f"Skipping empty row at index {i}")
                continue
            try:
                print(f"Processing row {i+1}: {row}")
                # Assumes 'Sl, No.', 'QUESTION', 'ANSWER' format
                _, question, answer = row
                print(f"Row {i+1} - Question: {question[:50]}...")
                print(f"Row {i+1} - Answer: {answer[:50]}...")
                
                # Try to add to cache
                success = add_to_cache(question, answer, source="csv_import")
                if not success:
                    print(f"Failed to add row {i+1} to cache. Question: {question[:50]}...")
                else:
                    print(f"Successfully added row {i+1} to cache.")
                    
            except ValueError as e:
                # Log the problematic row and continue
                print(f"Skipping malformed row at index {i}: {row} - Error: {e}")
                continue
            except Exception as e:
                print(f"Error processing row {i+1}: {e}")
                raise
                
        print("CSV import finished.")
        
    except Exception as e:
        print(f"Failed to import CSV: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_csv_import()