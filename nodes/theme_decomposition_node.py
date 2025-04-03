from langgraph.types import interrupt, Command
from langchain_core.prompts import PromptTemplate
from .constants import THEME_DECOMPOSITION_PROMPT, ANALYZE_CORE_THEMES, ANALYZE_IMPLIED_TOPICS
from .blog_state import BlogState, CoreTheme, ThemeDecomposition
from .llm_object_provider import get_llm
import warnings
import json
import re

warnings.filterwarnings("ignore")

def clean_json_response(response: str) -> str:
    """
    Clean the JSON response from markdown formatting and other artifacts.
    
    Args:
        response (str): Raw response from LLM
        
    Returns:
        str: Clean JSON string
    """
    # Remove markdown code blocks
    response = re.sub(r'```json\s*', '', response)
    response = re.sub(r'```\s*$', '', response)
    
    # Remove any leading/trailing whitespace
    response = response.strip()
    
    return response

def decompose_theme(state: BlogState) -> Command:
    """
    Decompose the blog title into themes and concepts.
    
    Args:
        state (BlogState): Current state of the blog writing process
        
    Returns:
        BlogState: Updated state with theme decomposition
    """
    print("---THEME DECOMPOSITION---")

    title = state["title"]

    decompose_prompt = PromptTemplate(
        template=THEME_DECOMPOSITION_PROMPT,
        input_variables=["topic"]
    )

    llm_with_structured_output = get_llm().with_structured_output(ThemeDecomposition)
    chain = (
        decompose_prompt 
        | llm_with_structured_output 
    )
    
    response = chain.invoke({"topic": title})
    
    # with open("decomposition.json", "w") as f:
    #     json.dump(response.dict(), f, indent=4)
        
    return Command(
        update={
            "decomposition": response,
        },
        goto=[ANALYZE_CORE_THEMES, ANALYZE_IMPLIED_TOPICS]
    )
