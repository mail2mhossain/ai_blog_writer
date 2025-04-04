from decouple import config
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

OPENAI_API_KEY = config("OPENAI_API_KEY")
GPT_MODEL = config("GPT_MODEL")

llm = ChatOpenAI(model_name=GPT_MODEL, temperature=0, openai_api_key=OPENAI_API_KEY)
# llm = ChatOllama(
#     model="llama3.1",
#     temperature=0,
# )

def get_llm():
    return llm