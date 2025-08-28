from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import StrOutputParser
from config import settings
from utils.chroma_utils import get_chroma_db

def get_llm():
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", temperature=0.7, google_api_key=settings.gemini_api_key)

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
    
    Please provide a focused response that directly answers the question:
    - If asked about Zendalona in general, provide a concise definition
    - If asked about specific products, list those products with descriptions
    - Use simple bullet points with "* " at the start of each item when listing multiple items
    - Put product names in CAPITAL LETTERS when listing them
    - Put a colon and space after product names
    - Each bullet point should be on its own line
    - Do not use markdown formatting like **bold**
    - Write "Zendalona" correctly - never "Z endalona" or similar
    - Keep responses concise and relevant to the question
    - For simple greetings like "hi", "hello", "hey", etc., respond with a friendly greeting and a brief introduction to Zendalona
    - If the question is very short and doesn't relate to the context, provide a concise, helpful response
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

Please provide a focused response that directly answers the question:
- If asked about Zendalona in general, provide a concise definition.
- If asked about specific products, list those products with descriptions.
- Use simple bullet points with "* " at the start of each item when listing multiple items.
- Put product names in CAPITAL LETTERS when listing them.
- Put a colon and space after product names.
- Each bullet point should be on its own line.
- Do not use markdown formatting like bold.
- Write "Zendalona" correctly - never "Z endalona" or similar.
- Keep responses concise and relevant to the question.
- For simple greetings like "hi", "hello", "hey", etc., respond with a friendly greeting and a brief introduction to Zendalona.
- If the question is very short or unrelated to the context, provide a concise and helpful response connected to Zendalona (without mentioning missing context) and can do internet search too.
- donot say Hello ! Zendalona provides accessibility solutions again and again if not needed.
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
