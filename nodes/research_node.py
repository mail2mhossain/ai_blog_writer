# pip install tavily-python
# pip install -qU duckduckgo-search langchain-community



from langgraph.constants import Send
from langgraph.types import Command
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_core.documents import Document
from langchain_community.tools import DuckDuckGoSearchResults
from docling.document_converter import DocumentConverter
from concurrent.futures import ThreadPoolExecutor, as_completed
from nodes.constants import INTERNET_SEARCH
from .blog_state import BlogState, SearchState
from .llm_object_provider import get_llm


doc_converter = DocumentConverter()
search = DuckDuckGoSearchResults(output_format="list")

llm = get_llm()

def get_from_llm(query):
    print("Generating Content using LLM.")
    article_prompt = PromptTemplate(
        template="Write an article in markdown format on {query}", input_variables=["query"]
    )
    
    article_chain = article_prompt | llm | StrOutputParser()
    return article_chain.invoke({"query": query})


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


def search_on_web(state:SearchState) -> SearchState:    
    topic = state["topic"]
    print(f"------ RESEARCH ON {topic} [{state['search_count']}] ------")

    search_results = search.invoke(topic)
    search_urls = [results['link'] for results in search_results]

    compressed_docs = []
    # Define a function that loads a URL and compresses its content
    def process_url(url):
        docs = docling_url_loader(url)
        compressed = compress_context(docs, topic)
        return compressed

    # Use ThreadPoolExecutor to process URLs in parallel
    with ThreadPoolExecutor() as executor:
        # Create a future for each URL processing task
        future_to_url = {executor.submit(process_url, url): url for url in search_urls}
        
        # Collect results as they complete
        for future in as_completed(future_to_url):
            result = future.result()
            
            if result and hasattr(result, 'page_content') and result.page_content.strip():
                compressed_docs.append(result)

    final_content = None
    if compressed_docs:
        final_content = compress_context(compressed_docs, topic)
        final_content = final_content.page_content

    if not final_content or (hasattr(final_content, 'page_content') and not final_content.page_content.strip()):
        final_content = get_from_llm(topic)

    return Command(
        update={
            "web_sources": [f"{topic}: {final_content}"],
        },
    )


def continue_to_search(state: BlogState):
    print("---CONTINUING TO SEARCH---")
    search_queries = state.get("cluster_queries")
    
    print(f"-------Total Search Queries: {len(search_queries)} -> {str(search_queries)}------")
    research_tasks = []
    i = 1
    
    for key_search in search_queries:
        research_tasks.append(
            Send(
                INTERNET_SEARCH, 
                {
                    "topic": key_search,
                    "search_count": i   
                }
            )
        )
        i += 1
    
    return Command(
        goto = research_tasks
    )