from datetime import datetime
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langgraph.types import Command
from .blog_state import BlogState
from .constants import CRITIC_ARTICLE, REVISION_PROMPT, FINALIZATION_AND_PROOFREADING
from .llm_object_provider import get_llm


class Article(BaseModel):
    """Article model"""
    article: str = Field(description="The whole article in markdown format")
    message: str = Field(description="message to the critique")

def revise_article(state:BlogState) -> Command:
    print(f"---REVISE_ARTICLE---")

    iter = state.get("iteration", 0)
    user_critique = state.get("user_critique", None)
    iter = iter + 3

    print(f"------Entering in REVISE_ARTICLE: - {iter} time (s)------\n")

    revision_prompt = PromptTemplate(
        template=REVISION_PROMPT,
        input_variables=["draft", "critique"]
    )

    llm_with_tool = get_llm().with_structured_output(Article)

    chain = revision_prompt | llm_with_tool

    if user_critique:
        # print("User critique found.")
        article = chain.invoke({"draft": state["article"], "critique": user_critique})
        # print(f"Article revised based on USER critique\n")
        return Command(
            update={
                "iteration": iter,
                "article": article.article,
                "message": article.message,
            },
            goto=FINALIZATION_AND_PROOFREADING
        )
    else:
        # print("No user critique found.")
        article = chain.invoke({"draft": state["article"], "critique": state["critique"]})
        # print(f"Article revised based on critique\n")
        # with open("revised.md", "w", encoding="utf-8") as file:
        #     file.write(f"{article.article}\n")
            
        return Command(
            update={
                "iteration": iter,
                "article": article.article,
                "message": article.message,
            },
            goto=CRITIC_ARTICLE
        )

