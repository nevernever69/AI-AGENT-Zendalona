from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA, create_retrieval_chain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
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
def get_streaming_chain():
    """
    Create a streaming-compatible LangChain chain
    
    Returns:
        A tuple containing (streaming_chain, retriever)
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=settings.gemini_api_key,
        temperature=0.2,
        streaming=True
    )
    
    # Define a simple template
    template = """Role: You are Zendalona, an AI assistant specializing in Zendalona products and services.​
    Response Guidelines:
    Zendalona-Related Queries: Provide accurate and helpful answers using available context.
    Insufficient Context: If the query pertains to Zendalona but lacks context, request additional information.
    Unrelated Queries: Politely inform users that your expertise is limited to Zendalona-related topics.​
    Tone: Maintain a professional, courteous, and concise tone in all interactions.

    Context: {context}
    Question: {question}
    
    Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # Create a simple questioning chain
    chain = prompt | llm
    
    # Create a retriever
    db = get_chroma_db(collection_name="zendalona")
    retriever = db.as_retriever(search_kwargs={"k": 5})
    
    # Return the chain and retriever separately
    return chain, retriever

def process_query(chain, query: str):
    result = chain({"query": query})
    response = result["result"]
    sources = [doc.metadata.get("source", "") for doc in result["source_documents"] if doc.metadata.get("source")]
    return response, sources