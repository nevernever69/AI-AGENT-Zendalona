from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import StrOutputParser
from config import settings
from utils.chroma_utils import get_chroma_db

def get_llm():
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", temperature=0.7, google_api_key=settings.gemini_api_key)

def get_rag_chain():
    db = get_chroma_db()
    retriever = db.as_retriever()
    
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
    db = get_chroma_db()
    retriever = db.as_retriever()
    
    template = """
You are a helpful assistant for Zendalona, a company providing accessibility solutions. Answer the question based only on the following context: {context} and your general knowledge
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
    # Check if Gemini calls are disabled
    from config import settings
    if settings.disable_gemini_call:
        return []
    
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
