from typing import Literal
from langgraph.types import interrupt, Command
from .constants import THEME_DECOMPOSITION, SEARCH_QUERY_GENERATOR
from nodes.blog_state import BlogState

def title_approval(state: BlogState) -> Command:
    feedback = interrupt("Please provide feedback:")

    return Command(
        update={
            "title": feedback,
        },
        goto=THEME_DECOMPOSITION
    )

def outline_approval(state: BlogState) -> Command:
    feedback = interrupt("Please provide feedback:")

    return Command(
        update={
            "outline": feedback,
        },
        goto=SEARCH_QUERY_GENERATOR
    )