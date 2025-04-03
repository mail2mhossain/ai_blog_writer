from datetime import datetime
from .blog_state import BlogState

def save_article(state: BlogState) -> BlogState:
    print("---SAVE ARTICLE---\n")
    title = state["title"]
    article = state["article"]
    references = state["references"]
    iteration = state["iteration"]

    file_name = title.replace('"', "")
    file_name = file_name.replace(":", "-")
    file_name = f"{file_name}.md"
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(f"{article}\n")
        file.write(f"{references}\n")

    return {"file_name": file_name}
