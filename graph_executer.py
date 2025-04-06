import uuid
from langgraph.types import Command
from nodes.constants import DRAFT_ARTICLE_APPROVAL, FINAL_ARTICLE_APPROVAL
from graph_generator import generate_graph

graph = generate_graph()

def generate_title(topic, thread_id):
    print(f"Generating Title for ID: {thread_id}")
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
    # print(f"\nGenerated Titles: {titles}\n")
    
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
    print(f"Generating Outline for ID: {thread_id}")
    config = {
        "configurable": {
            "thread_id": thread_id,
            "recursion_limit": 100,
        }
    }
    output = graph.invoke(Command(resume=title), config=config)
    # print(f"New Title: {output['title']}\n")
    # print(f"Outline:\n{output['outline']}\n")
    return output["outline"]

def generate_article(outline, thread_id):
    print(f"Drafting Article for ID: {thread_id}")
    config = {
        "configurable": {
            "thread_id": thread_id,
            "recursion_limit": 100,
        }
    }
    output = graph.invoke(Command(resume=outline), config=config)
    # print(f"\nGenerated Article:\n{output['article']}\n")
    return output["article"]

def finalize_article(article, critique, thread_id):
    print(f"Finalizing Article for ID: {thread_id}")
    config = {
        "configurable": {
            "thread_id": thread_id,
            "recursion_limit": 100,
        }
    }
 
    update_state = {"article": article, "user_critique": critique}
    # graph.update_state(config, update_state, as_node=DRAFT_ARTICLE_APPROVAL)
    # print("State updated")
    output = graph.invoke(Command(update=update_state, resume=critique), config=config)
   
    # output = graph.invoke(None, config=config)
    # print(f"\nFinalized Article:\n{output['article']}\n")
    return output["article"]
    

