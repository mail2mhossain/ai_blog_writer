from decouple import config
from tavily import TavilyClient
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_core.documents import Document
from docling.document_converter import DocumentConverter
from concurrent.futures import ThreadPoolExecutor, as_completed
from nodes.llm_object_provider import get_llm


TAVILY_API_KEY = config("TAVILY_TIGER_API_KEY")

search_client = TavilyClient(api_key=TAVILY_API_KEY)
doc_converter = DocumentConverter()
llm = get_llm()

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


topic = "Stellar life cycle stages Main Sequence duration importance to understanding universe age composition evolution"

results = search_client.search(
        query=topic,
        topic="general",
        max_results=5,
        search_depth="advanced",
        include_raw_content=True,
        include_answer=True
    )

urls=[]
raw_content = []
for result in results["results"]:
    if result['url'] not in urls:
        urls.append(result["url"])
        print(f"URL: {result['url']}\n")
    # print(f"Keys:\n{result.keys()}\n")
    # print(f"type: {type(result)}")
    # print(f"Results:\n{result}\n")
        if result['raw_content']:
            # print(f"Raw Content:\n{result['raw_content']}\n")
            # raw_content.append(result['raw_content'])
            dox = Document(
                page_content=result['raw_content'],
            )
            raw_content.append(dox)
    # print(f"Answer:\n{result['answer']}\n")
    

print(f"Total Raw Content: {len(raw_content)}")
compressed_docs = []
# Define a function that loads a URL and compresses its content
def process_url(dox):
    compressed = compress_context(dox, topic)
    print(f"\nCompressed Content:\n{compressed}\n")
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
# sources[topic] = urls