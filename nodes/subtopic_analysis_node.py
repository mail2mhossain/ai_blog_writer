from langchain_core.prompts import PromptTemplate
from langgraph.types import Command
from .llm_object_provider import get_llm
import warnings

from .blog_state import BlogState, ThemeAnalyses, ImpliedTopicAnalyses
from .constants import THEME_ANALYSIS_PROMPT, IMPLIED_TOPIC_ANALYSIS_PROMPT, OUTLINE_GENERATOR

warnings.filterwarnings("ignore")


def format_themes_for_prompt(state: BlogState) -> tuple[str, str]:
    """Format the themes and scope boundaries for the prompt input."""
    # Format core themes
    themes = state.get("decomposition").core_themes
    formatted_themes = []
    for theme in themes:
        formatted_themes.append(f"Theme: {theme.theme}\nDescription: {theme.description}")
    themes_text = "\n\n".join(formatted_themes)
    
    # Format scope boundaries
    scope_boundaries = state.get("decomposition").scope_boundaries
    scope_boundaries_text = "\n".join([f"- {boundary}" for boundary in scope_boundaries])
    
    return themes_text, scope_boundaries_text

def analyze_core_themes(state: BlogState) -> Command:
    """
    Analyze core themes using the 5W's + H framework.
    
    Args:
        state (BlogState): Current state of the blog writing process
        
    Returns:
        BlogState: Updated state with theme analysis
    """
    print("---CORE THEME ANALYSIS---")
    
    # Format content for the prompt
    themes_text, scope_boundaries_text = format_themes_for_prompt(state)
    
    # Create and run the prompt
    analyze_prompt = PromptTemplate(
        template=THEME_ANALYSIS_PROMPT,
        input_variables=["themes", "scope_boundaries"]
    )
    
    llm_with_structured_output = get_llm().with_structured_output(ThemeAnalyses)
    chain = analyze_prompt | llm_with_structured_output
    
    theme_analyses = chain.invoke({
            "themes": themes_text,
            "scope_boundaries": scope_boundaries_text
        })

    # with open("theme_analyses.json", "w") as f:
    #     json.dump(theme_analyses.dict(), f, indent=4)
        
    return Command(
        update={
            "theme_analysis": theme_analyses,
        },
        goto=OUTLINE_GENERATOR
    )

def analyze_implied_topics(state: BlogState) -> Command:
    """
    Analyze implied topics and their relationships to core themes.
    
    Args:
        state (BlogState): Current state of the blog writing process
        
    Returns:
        BlogState: Updated state with implied topic analysis
    """
    print("---IMPLIED TOPIC ANALYSIS---")
    
    # Format content for the prompt
    themes_text, scope_boundaries_text = format_themes_for_prompt(state)
    implied_topics = state.get("decomposition").implied_topics
    implied_topics_text = "\n".join([f"- {topic}" for topic in implied_topics])
    
    # Create and run the prompt
    analyze_prompt = PromptTemplate(
        template=IMPLIED_TOPIC_ANALYSIS_PROMPT,
        input_variables=["themes", "implied_topics", "scope_boundaries"]
    )
    
    llm_with_structured_output = get_llm().with_structured_output(ImpliedTopicAnalyses)
    chain = analyze_prompt | llm_with_structured_output
    
    implied_topic_analyses = chain.invoke({
            "themes": themes_text,
            "implied_topics": implied_topics_text,
            "scope_boundaries": scope_boundaries_text
        })

    # with open("implied_topic_analyses.json", "w") as f:
    #     json.dump(implied_topic_analyses.dict(), f, indent=4)
        
    return Command(
        update={
            "implied_topic_analysis": implied_topic_analyses,
        },
        goto=OUTLINE_GENERATOR
    )


