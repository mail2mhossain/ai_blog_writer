# python write_blog.py "LLM Prompt Techniques"
# python write_blog.py "AI Application in real life"
# python write_blog.py "Coding for kid"
# python write_blog.py "Stellar Evolution - The life cycle of a star"

import uuid
import argparse
from langgraph.types import interrupt, Command
from graph_generator import generate_graph
from concurrent.futures import ThreadPoolExecutor

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Write an article on a given topic.")
parser.add_argument("topic", type=str, help="The topic for the article.")
args = parser.parse_args()

topic = args.topic

graph = generate_graph()

def generate_title(topic, thread_id):
    config = {
        "configurable": {
            "thread_id": thread_id,
            "recursion_limit": 100,
        }
    }
    inputs = {"topic": topic}
    output = graph.invoke(inputs, config=config)
    print(f"\nGenerated Title: {output['title']}\n")
    return output["title"]

def generate_outline(title, thread_id):
    config = {
        "configurable": {
            "thread_id": thread_id,
            "recursion_limit": 100,
        }
    }
    output = graph.invoke(Command(resume=title), config=config)
    print(f"New Title: {output['title']}\n")
    print(f"Outline:\n{output['outline']}\n")
    return output["outline"]

def generate_article(outline, thread_id):
    config = {
        "configurable": {
            "thread_id": thread_id,
            "recursion_limit": 100,
        }
    }
    output = graph.invoke(Command(resume=outline), config=config)
    return output["article"]

thread_id = str(uuid.uuid4())


title = generate_title(topic, thread_id)

title = "Journey of the Stars: Unveiling the Life Cycle of Stellar Evolution"

outline = generate_outline(title, thread_id)

        