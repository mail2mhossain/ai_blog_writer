from langchain_core.prompts import PromptTemplate
from langgraph.types import Command
from typing import List
from pydantic import BaseModel, Field
from .constants import TITLE_PROMPT, TITLE_APPROVAL
from .blog_state import BlogState
from .llm_object_provider import get_llm

class Title(BaseModel):
    """Represents the blog title"""
    titles: List[str] = Field(description="List of the blog titles")

def generate_title(state: BlogState) -> Command :
    print("---TITLE GENERATION---")
    topic = state["topic"]

    title_prompt = PromptTemplate(
        template=TITLE_PROMPT, input_variables=["topic"]
    )

    title_chain = title_prompt | get_llm().with_structured_output(Title)

    titles = title_chain.invoke({"topic": topic})

    return Command(
        update={
            "titles": titles.titles,
        },
        goto=TITLE_APPROVAL
    )
