from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from config import settings
from utils.chroma_utils import get_chroma_db

def get_rag_chain():
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=settings.gemini_api_key,
        temperature=0.2
    )
    
    prompt_template = """You are a helpful assistant for Zendalona, providing accurate answers about Zendalona products and general queries. If the question is related to Zendalona and the provided context is relevant, use the context to answer accurately. For questions unrelated to Zendalona or when the context is insufficient, provide a clear and accurate answer based on your general knowledge without mentioning the lack of context. Always be polite and accessible.

    Context: {context}
    Question: {question}
    Answer: """
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    db = get_chroma_db(collection_name="zendalona")
    retriever = db.as_retriever(search_kwargs={"k": 5})
    
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    
    return chain

def process_query(chain, query: str):
    result = chain({"query": query})
    response = result["result"]
    sources = [doc.metadata.get("source", "") for doc in result["source_documents"] if doc.metadata.get("source")]
    return response, sources