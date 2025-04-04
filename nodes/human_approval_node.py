from typing import Literal
from langgraph.types import interrupt, Command
from .constants import THEME_DECOMPOSITION, SEARCH_QUERY_GENERATOR, REVISION, FINALIZATION_AND_PROOFREADING
from nodes.blog_state import BlogState

def title_approval(state: BlogState) -> Command:
    print(f"---TITLE APPROVAL---")
    feedback = interrupt("Please provide feedback:")

    return Command(
        update={
            "title": feedback,
        },
        goto=THEME_DECOMPOSITION
    )

def outline_approval(state: BlogState) -> Command:
    print(f"---OUTLINE APPROVAL---")
    feedback = interrupt("Please provide feedback:")

    return Command(
        update={
            "outline": feedback,
        },
        goto=SEARCH_QUERY_GENERATOR
    )


def draft_article_approval(state: BlogState) -> Command:
    print(f"---DRAFT ARTICLE APPROVAL---")
    critique = interrupt("Please provide feedback:")

    if critique:
        # print("User critique found. go to revision step.")
        return Command(
            update={
                # "article": draft,
                "user_critique": critique,
            },
            goto=REVISION
        )
    else:
        # print("No user critique found. Go to Finalize step.")
        return Command(
            # update={
            #     "article": draft,
            # },
            goto=FINALIZATION_AND_PROOFREADING
        )

