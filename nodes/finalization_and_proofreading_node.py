from langgraph.types import Command
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .llm_object_provider import get_llm
from .blog_state import BlogState
from .constants import FINALIZATION_AND_PROOFREADING_PROMPT


def finalize_article(state:BlogState) -> Command:
    print(f"---FINALIZE ARTICLE---")
    article = state["article"]

    # with open("draft_edited.md", "w") as f:
    #     f.write(article)
        
    finalize_prompt = PromptTemplate(
        template=FINALIZATION_AND_PROOFREADING_PROMPT,
        input_variables=["blog_post"]
    )

    chain = finalize_prompt | get_llm() | StrOutputParser()

    finalized_article = chain.invoke({
        "blog_post": article,
    })

    # with open("finalized_article.md", "w") as f:
    #     f.write(finalized_article)

        
    return Command(
        update={
            "article": finalized_article,
        },
    )