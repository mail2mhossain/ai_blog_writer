from datetime import datetime
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langgraph.types import Command
from langchain_core.output_parsers import StrOutputParser
from .blog_state import BlogState
from .constants import DRAFT_PROMPT, CRITIC_ARTICLE
from .llm_object_provider import get_llm


def write_article(state:BlogState) -> Command:
    print(f"---DRAFTING BLOG---")

    title = state["title"]
    outline = state["outline"]
    # sources = state["sources"]
    web_sources = state["web_sources"]
    # web_sources = list(set(web_sources))
    # print(f"------Web sources: {len(web_sources)}------\n")

    draft_prompt = PromptTemplate(
        template=DRAFT_PROMPT,
        input_variables=["title", "blog_outline", "web_sources"]
    )

    chain = draft_prompt | get_llm() | StrOutputParser()
    article = chain.invoke(
        {
            "title": title,
            "blog_outline": outline.model_dump_json(),
            "web_sources": str(web_sources)
        }
    )
    # print(f"Draft Article written.\n")
    # with open("draft.md", "w", encoding="utf-8") as file:
    #     file.write(f"{article}\n")

    return Command(
        update={
            "article": article,
        },
        goto=CRITIC_ARTICLE
    )
