import sqlite3
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
# from langgraph.checkpoint.sqlite import SqliteSaver
# from langgraph.checkpoint.postgres import PostgresSaver
from nodes.blog_state import BlogState
from nodes.title_generation_node import generate_title
from nodes.theme_decomposition_node import decompose_theme
from nodes.subtopic_analysis_node import analyze_core_themes, analyze_implied_topics
from nodes.outline_generation_node import generate_structured_outline
from nodes.search_query_generator_node import generate_search_query
from nodes.research_node import continue_to_search, search_on_web
from nodes.writer_node import write_article
from nodes.critique_node import critique_article
from nodes.revise_node import revise_article
from nodes.finalization_and_proofreading_node import finalize_article
from nodes.human_approval_node import title_approval, outline_approval
from nodes.constants import (
    TITLE_GENERATOR,
    THEME_DECOMPOSITION,
    ANALYZE_CORE_THEMES,
    ANALYZE_IMPLIED_TOPICS,
    OUTLINE_GENERATOR,
    SEARCH_QUERY_GENERATOR,
    INTERNET_SEARCH,
    CONTINUE_TO_SEARCH,
    DRAFT_WRITER,
    CRITIC_ARTICLE,
    REVISION,
    FINALIZATION_AND_PROOFREADING,
    TITLE_APPROVAL,
    OUTLINE_APPROVAL
)

# sqlite_conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
# DB_URI = "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable"
# postgres_saver = PostgresSaver.from_conn_string(DB_URI)
# sqlite_saver = SqliteSaver(sqlite_conn)
in_memory_saver = MemorySaver()

def generate_graph():
    workflow = StateGraph(BlogState)

    workflow.add_node(TITLE_GENERATOR, generate_title)
    workflow.add_node(TITLE_APPROVAL, title_approval)
    workflow.add_node(THEME_DECOMPOSITION, decompose_theme)
    workflow.add_node(ANALYZE_CORE_THEMES, analyze_core_themes)
    workflow.add_node(ANALYZE_IMPLIED_TOPICS, analyze_implied_topics)
    workflow.add_node(OUTLINE_GENERATOR, generate_structured_outline)
    workflow.add_node(OUTLINE_APPROVAL, outline_approval)
    workflow.add_node(SEARCH_QUERY_GENERATOR, generate_search_query)
    workflow.add_node(INTERNET_SEARCH, search_on_web)
    workflow.add_node(CONTINUE_TO_SEARCH, continue_to_search)
    workflow.add_node(DRAFT_WRITER, write_article)
    workflow.add_node(CRITIC_ARTICLE, critique_article)
    workflow.add_node(REVISION, revise_article)
    workflow.add_node(FINALIZATION_AND_PROOFREADING, finalize_article)

    workflow.set_entry_point(TITLE_GENERATOR)
    workflow.add_edge(INTERNET_SEARCH, DRAFT_WRITER)
    workflow.set_finish_point(FINALIZATION_AND_PROOFREADING)

    graph = workflow.compile(checkpointer=in_memory_saver)
    
    return graph
