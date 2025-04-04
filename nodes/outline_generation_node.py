from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.types import Command
from .llm_object_provider import get_llm
import warnings
from typing import List, Optional
from pydantic import BaseModel, Field

from .constants import OUTLINE_APPROVAL, OUTLINE_USER_MSG
from .blog_state import BlogState, BlogOutline

warnings.filterwarnings("ignore")


def generate_structured_outline(state: BlogState) -> Command:
    """
    Generate a structured outline based on theme analysis and implied topic analysis.
    
    Args:
        state (BlogState): Current state of the blog writing process containing theme and implied topic analyses
        
    Returns:
        Command: Command to update the blog state with the generated outline
    """
    print("---GENERATING STRUCTURED OUTLINE---")
    
    # Get theme and implied topic analyses from state
    theme_analysis = state.get("theme_analysis")
    implied_topic_analysis = state.get("implied_topic_analysis")
    
    # Define the output parser for structured output
    parser = PydanticOutputParser(pydantic_object=BlogOutline)
    
    # Create and run the prompt with structured output format
    outline_prompt = PromptTemplate(
        template=OUTLINE_USER_MSG + "\n\n{format_instructions}\n\nMake sure each section has clear key points and relevant subsections.",
        input_variables=["theme_analysis", "implied_topic_analysis"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = outline_prompt | get_llm().with_structured_output(BlogOutline)
    
    outline = chain.invoke({
        "theme_analysis": theme_analysis,
        "implied_topic_analysis": implied_topic_analysis
    })

    # print(f"Generated outline structure: {outline.model_dump()}")
    # with open("outline.md", "w") as f:
    #     f.write(outline.model_dump_json(indent=4))
        
    return Command(
        update = {
            "outline": outline

        },
        goto = OUTLINE_APPROVAL
    )

