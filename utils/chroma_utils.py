import logging
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema import Document
from config import settings
from PyPDF2 import PdfReader
from io import BytesIO

# Setup logging
logging.basicConfig(filename=settings.log_path, level=logging.INFO)

def get_chroma_db(collection_name: str = "zendalona"):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=settings.gemini_api_key
    )
    return Chroma(
        collection_name=collection_name,
        persist_directory=settings.chroma_db_path,
        embedding_function=embeddings
    )

def index_documents_to_chroma(documents: list[Document], collection_name: str = "zendalona") -> int:
    try:
        db = get_chroma_db(collection_name)
        
        # Get existing document URLs/sources to avoid duplicates
        existing_docs = db.get(include=["metadatas"])
        existing_sources = {doc["source"] for doc in existing_docs["metadatas"] if "source" in doc}
        
        # Filter out documents whose sources are already indexed
        new_documents = [doc for doc in documents if doc.metadata.get("source") not in existing_sources]
        
        if not new_documents:
            logging.info("No new documents to index; all sources already exist in ChromaDB")
            return 0
        
        # Add new documents to ChromaDB
        db.add_documents(new_documents)
        logging.info(f"Indexed {len(new_documents)} new documents to ChromaDB collection '{collection_name}'")
        return len(new_documents)
    except Exception as e:
        logging.error(f"Error indexing documents: {str(e)}")
        raise

def process_pdf(file: BytesIO, filename: str) -> list[Document]:
    try:
        # Read PDF content
        pdf_reader = PdfReader(file)
        documents = []
        
        # Extract text from each page
        for page_num, page in enumerate(pdf_reader.pages, 1):
            text = page.extract_text() or ""
            if text.strip():
                doc = Document(
                    page_content=text,
                    metadata={
                        "source": filename,
                        "page": page_num,
                        "type": "pdf"
                    }
                )
                documents.append(doc)
        
        if not documents:
            logging.warning(f"No text extracted from PDF: {filename}")
            return []
        
        logging.info(f"Extracted {len(documents)} pages from PDF: {filename}")
        return documents
    except Exception as e:
        logging.error(f"Error processing PDF {filename}: {str(e)}")
        return []