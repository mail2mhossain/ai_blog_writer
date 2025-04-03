from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_core.documents import Document
from langchain_community.tools import DuckDuckGoSearchResults
from docling.document_converter import DocumentConverter
from langchain.schema import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
import requests
import sys
from decouple import config 

OPENAI_API_KEY = config("OPENAI_API_KEY")
GPT_MODEL = config("GPT_MODEL")

# llm = ChatOpenAI(model_name=GPT_MODEL, temperature=0, openai_api_key=OPENAI_API_KEY)
llm = ChatOllama(
    model="phi3.5",
    temperature=0,
)

def get_from_llm(query):
    print("Generating Content using LLM.")
    article_prompt = PromptTemplate(
        template="Write an article in markdown format on {query}", input_variables=["query"]
    )
    
    article_chain = article_prompt | llm | StrOutputParser()
    return article_chain.invoke({"query": query})

doc_converter = DocumentConverter()
def docling_url_loader(url: str) -> Document:
    try:
        doc = doc_converter.convert(url)
        dox = Document(
            page_content=doc.document.export_to_markdown(),
        )

        return [dox]
    except requests.exceptions.HTTPError as e:
        return [Document(page_content="")]
    except Exception as e:
        return [Document(page_content="")]

def compress_context(doc, query):
    print(f"Entering in CONTEXT COMPRESSOR:\n")

    compressor = LLMChainExtractor.from_llm(llm=llm)
    
    # Check if doc is a list of Document objects or a single Document
    if isinstance(doc, list):
        # If it's already a list of Documents, use it directly
        docs_to_compress = doc
    elif hasattr(doc, 'page_content'):
        # If it's a single Document object
        docs_to_compress = [doc]
    else:
        # If it's a list of something else (like tuples or strings), convert to Documents
        docs_to_compress = [Document(page_content=str(item)) for item in doc if item]

    compressed_docs = compressor.compress_documents(docs_to_compress, query)

    if compressed_docs:
        return compressed_docs[0]
    else:
        return Document(page_content="")

print("Starting DuckDuckGo search...")
search = DuckDuckGoSearchResults(output_format="list")

query = "Stellar formation protostars gravity pressure stages observational techniques simulations"
# query = 'Molecular Cloud Collapse and Stellar Formation in Galaxies'

def search_on_web(topic) :    
    print(f"------ RESEARCH ON {topic} ------")

    search_results = search.invoke(topic)
    search_urls = [results['link'] for results in search_results]
    print(f"Search Results: {len(search_urls)}")
    compressed_docs = []

    # Define a function that loads a URL and compresses its content
    def process_url(url):
        docs = docling_url_loader(url)
        # print(f"\nWebsite Content: {type(docs)}\n{docs}")
        compressed = compress_context(docs, topic)
        # print(f"\nCompressed Content: {type(compressed)}\n{compressed}")
        return compressed

    # Use ThreadPoolExecutor to process URLs in parallel
    with ThreadPoolExecutor() as executor:
        # Create a future for each URL processing task
        future_to_url = {executor.submit(process_url, url): url for url in search_urls}
        
        # Collect results as they complete
        for future in as_completed(future_to_url):
            result = future.result()
            
            if result and hasattr(result, 'page_content') and result.page_content.strip():
                print(f"Results: {type(result)}")
                compressed_docs.append(result)

    final_content = None
    # print(compressed_docs)
    if compressed_docs:
        final_content = compress_context(compressed_docs, topic)
        final_content = final_content.page_content

    if not final_content or (hasattr(final_content, 'page_content') and not final_content.page_content.strip()):
        final_content = get_from_llm(topic)

    return final_content

final_content = search_on_web(query)
print(f"Final Content: {final_content}")