from datetime import datetime
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.types import Command
from .blog_state import BlogState
from .constants import CRITIQUE_PROMPT, REVISION,DRAFT_ARTICLE_APPROVAL, FINALIZATION_AND_PROOFREADING
from .llm_object_provider import get_llm


def critique_article(state:BlogState) -> Command:
    print(f"---CRITIQUE_ARTICLE---")
    iter = state.get("iteration", 0)

    critique_prompt = PromptTemplate(
        template=CRITIQUE_PROMPT,
        input_variables=["article"]
    )
    chain = critique_prompt | get_llm() | StrOutputParser()

    critique_response = chain.invoke({"article": state["article"]})

    if (critique_response is None or 
        (isinstance(critique_response, str) and critique_response.strip() == "None") or 
        iter >= 3):

        return Command(
            update={
                "critique": None,
            },
            goto=DRAFT_ARTICLE_APPROVAL
        )
    else:
        # print(f"CRITIQUE: {critique_response}\n")
        return Command(
            update={
                "critique": critique_response,
                "message": None,
            },
            goto=REVISION
        )

