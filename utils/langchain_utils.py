from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import StrOutputParser
from config import settings
from utils.chroma_utils import get_chroma_db

def get_llm():
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7, google_api_key=settings.gemini_api_key)

def get_rag_chain():
    db = get_chroma_db()
    retriever = db.as_retriever()
    
    template = """
    You are a helpful assistant for Zendalona, a company providing accessibility solutions.
    Answer the question based only on the following context:
    {context}
    
    Question: {question}
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
    db = get_chroma_db()
    retriever = db.as_retriever()
    
    template = """
    You are a helpful assistant for Zendalona, a company providing accessibility solutions.
    Answer the question based only on the following context:
    {context}
    
    Question: {question}
    """
    
    prompt = PromptTemplate.from_template(template)
    
    chain = (
        prompt
        | get_llm()
        | StrOutputParser()
    )
    
    return chain, retriever

def process_query(chain, query):
    response = chain.invoke(query)
    return response, []

async def generate_suggestions(query: str, answer: str):
    llm = get_llm()
    prompt = f"""
    Given the following question and answer, generate 3 relevant follow-up questions.
    Return the questions as a list of strings, separated by a pipe character (|).

    Question: {query}
    Answer: {answer}

    Follow-up Questions:
    """
    response = await llm.ainvoke(prompt)
    suggestions = response.content.strip().split('|')
    return [s.strip() for s in suggestions if s.strip()]
