from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import StrOutputParser
from config import settings
from utils.chroma_utils import get_chroma_db

def get_llm():
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", temperature=0.3, google_api_key=settings.gemini_api_key)

def get_rag_chain():
    from config import settings
    db = get_chroma_db()
    # Retrieve more documents initially and filter by similarity threshold
    retriever = db.as_retriever(search_kwargs={"k": settings.retrieval_k})
    
    template = """
You are a helpful assistant for Zendalona, a company providing accessibility solutions.
Answer the question based only on the following context:
{context}

Question: {question}

Instructions:
- If the question is a simple greeting (like "hi", "hello", "hey") with no other content, respond ONLY with: "Hello! How can I help you with Zendalona today?"
- If the question is asking for specific information, answer ONLY that information directly without any greeting
- If asked about Zendalona in general, provide a concise 1-2 sentence definition
- If asked about specific products, list them with brief descriptions using bullet points
- Use simple bullet points with "* " at the start of each item
- Put product names in CAPITAL LETTERS
- Put a colon and space after product names
- Each bullet point should be on its own line
- Do not use markdown formatting like **bold**
- Write "Zendalona" correctly - never "Z endalona" or similar
- Keep responses focused and under 5 sentences unless specifically asked for details
- If the question is very short but asking for specific information, provide that information
- NEVER start with "Hello! Zendalona provides accessibility solutions"
- Be concise and get straight to the point
"""
    
    prompt = PromptTemplate.from_template(template)
    
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | get_llm()
        | StrOutputParser()
    )
    
    return chain

def get_streaming_chain():
    from config import settings
    db = get_chroma_db()
    # Retrieve more documents initially and filter by similarity threshold
    retriever = db.as_retriever(search_kwargs={"k": settings.retrieval_k})
    
    template = """
You are a helpful assistant for Zendalona, a company providing accessibility solutions.
Answer the question based only on the following context:
{context}

Question: {question}

Instructions:
- If the question is a simple greeting (like "hi", "hello", "hey") with no other content, respond ONLY with: "Hello! How can I help you with Zendalona today?"
- If the question is asking for specific information, answer ONLY that information directly without any greeting
- If asked about Zendalona in general, provide a concise 1-2 sentence definition
- If asked about specific products, list them with brief descriptions using bullet points
- Use simple bullet points with "* " at the start of each item
- Put product names in CAPITAL LETTERS
- Put a colon and space after product names
- Each bullet point should be on its own line
- Do not use markdown formatting like bold
- Write "Zendalona" correctly - never "Z endalona" or similar
- Keep responses focused and under 5 sentences unless specifically asked for details
- If the question is very short but asking for specific information, provide that information
- NEVER start with "Hello! Zendalona provides accessibility solutions"
- Be concise and get straight to the point
"""
    
    prompt = PromptTemplate.from_template(template)
    
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | get_llm()
        | StrOutputParser()
    )
    
    return chain

def process_query(chain, query):
    # Collect sources using the same filtering approach as streaming
    from utils.chroma_utils import get_chroma_db
    from config import settings
    
    # Get all results with scores
    all_docs_with_scores = get_chroma_db().similarity_search_with_score(query, k=settings.retrieval_k)
    # Filter by similarity threshold (higher score = less similar)
    filtered_docs = [doc for doc, score in all_docs_with_scores if score <= settings.retrieval_threshold]
    # Limit to maximum number of context documents
    docs = filtered_docs[:settings.max_context_docs] if filtered_docs else []
    sources = [doc.metadata.get("source", "") for doc in docs if doc.metadata.get("source")]
    
    response = chain.invoke(query)
    return response, sources
