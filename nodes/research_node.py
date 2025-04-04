# pip install tavily-python
# pip install -qU duckduckgo-search langchain-community



from langgraph.constants import Send
from langgraph.types import Command
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_core.documents import Document
from tavily import TavilyClient
from concurrent.futures import ThreadPoolExecutor, as_completed
from nodes.constants import INTERNET_SEARCH
from .blog_state import BlogState, SearchState
from .llm_object_provider import get_llm
from decouple import config

TAVILY_API_KEY = config("TAVILY_API_KEY")

search_client = TavilyClient(api_key=TAVILY_API_KEY)

llm = get_llm()

def get_from_llm(query):
    print("Generating Content using LLM.")
    article_prompt = PromptTemplate(
        template="Write an article in markdown format on {query}", input_variables=["query"]
    )
    
    article_chain = article_prompt | llm | StrOutputParser()
    return article_chain.invoke({"query": query})


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

    results = search_client.search(
        query=topic,
        topic="general",
        max_results=3,
        search_depth="advanced",
        include_raw_content=True,
        include_answer=True
    )

    urls=[]
    raw_content = []
    for result in results["results"]:
        if result['url'] not in urls:
            if result['raw_content']:
                urls.append(result["url"])
                # print(f"Raw Content:\n{result['raw_content']}\n")
                dox = Document(
                    page_content=result['raw_content'],
                    metadata={"url": result["url"]}
                )
                raw_content.append(dox)
    # print(f"Answer:\n{result['answer']}\n")
    
    compressed_docs = []
    # Define a function that loads a URL and compresses its content
    def process_url(dox):
        compressed = compress_context(dox, topic)
        return compressed

    # Use ThreadPoolExecutor to process URLs in parallel
    with ThreadPoolExecutor() as executor:
        # Create a future for each URL processing task
        future_to_url = {executor.submit(process_url, dox): dox for dox in raw_content}
        
        # Collect results as they complete
        for future in as_completed(future_to_url):
            result = future.result()
            
            if result and hasattr(result, 'page_content') and result.page_content.strip():
                compressed_docs.append(result)

    final_content = None
    for doc in compressed_docs:
        if not final_content:
            final_content = doc.page_content + "\n Source: " + doc.metadata["url"]
        else:
            final_content += "\n\n" + doc.page_content + "\n Source: " + doc.metadata["url"]

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