import uuid
from langgraph.types import Command
from graph_generator import generate_graph

graph = generate_graph()


# def execute_graph(thread_id, topic):
#     global chain, config
#     config = {
#         "configurable": {
#             "thread_id": thread_id,
#             "recursion_limit": 100,
#         }
#     }
    
#     inputs = {"topic": topic}
#     output = chain.invoke(inputs, config=config)
#     return output['article']

def generate_title(topic, thread_id):
    config = {
        "configurable": {
            "thread_id": thread_id,
            "recursion_limit": 100,
        }
    }
    inputs = {"topic": topic}
    output = graph.invoke(inputs, config=config)
    
    # Process the titles to ensure we return a proper Python list
    titles = output["titles"]
    print(f"\nGenerated Titles: {titles}\n")
    
    # If titles is a string that looks like a list, parse it
    if isinstance(titles, str):
        if titles.startswith("titles=['") and titles.endswith("']"):
            # Extract the content between titles=[' and ']
            content = titles[len("titles=['") : -len("']")]
            # Split by ', ' to get individual titles
            titles = [t.strip() for t in content.split("', '") if t.strip()]
        elif titles.startswith("[") and titles.endswith("]"):
            # Remove brackets and split by commas
            content = titles[1:-1]
            titles = [t.strip().strip('\'"') for t in content.split(",") if t.strip()]
        elif '\n' in titles:
            # Split by newlines
            titles = [t.strip() for t in titles.split('\n') if t.strip()]
        elif ',' in titles:
            # Split by commas
            titles = [t.strip() for t in titles.split(',') if t.strip()]
        else:
            # Single title
            titles = [titles]
    
    # Ensure we have at least one title
    if not titles:
        titles = ["Generated Title for " + topic]
        
    return titles

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

if __name__ == "__main__":
    thread_id = str(uuid.uuid4())
    topic = "Stellar Evolution - The life cycle of a star"

    # title = generate_title(topic, thread_id)

    # title = "Journey of the Stars: Unveiling the Life Cycle of Stellar Evolution"
    # outline = generate_outline(title, thread_id)

    # article = generate_article(outline, thread_id)

    # print(f"\nGenerated Article:\n{article}\n")
