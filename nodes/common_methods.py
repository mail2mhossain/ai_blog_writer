from .blog_state import BlogOutline
from typing import List, Dict, Any


def escape_curly_braces(text: str) -> str:
    """
    Escape curly braces in text by doubling them.
    Args:
        text (str): Text that may contain curly braces
    Returns:
        str: Text with escaped curly braces
    """
    return text.replace("{", "{{").replace("}", "}}")

def escape_key_points(key_points: List[str]) -> List[str]:
    """
    Escape curly braces in a list of key points.
    Args:
        key_points (List[str]): List of key points that may contain curly braces
    Returns:
        List[str]: List of key points with escaped curly braces
    """
    return [escape_curly_braces(point) for point in key_points]

def extract_sections(outline: BlogOutline) -> List[Dict[str, Any]]:
    """
    Extract sections and their key points from the BlogOutline object.
    
    Args:
        outline (BlogOutline): The outline object containing sections and their details
        
    Returns:
        List[Dict[str, Any]]: List of sections with their titles and key points
    """
    sections = []
    
    for section in outline.sections:
        # Add main section with escaped curly braces
        section_data = {
            "title": escape_curly_braces(section.title),
            "key_points": escape_key_points(section.key_points)
        }
        sections.append(section_data)
        
        # Add subsections if they exist
        if section.subsections:
            for subsection in section.subsections:
                subsection_data = {
                    "title": escape_curly_braces(f"{section.title} - {subsection.title}"),  # Include parent section context
                    "key_points": escape_key_points(subsection.key_points)
                }
                sections.append(subsection_data)
    
    return sections


def extract_key_points(outline: BlogOutline) -> List[Dict[str, Any]]:
    key_points = []
    
    for section in outline.sections:
        if section.key_points:
            for points in section.key_points:
                key_points.append(f"{section.title}: {points}")  # Include parent section context in key points)
        
        # Add subsections if they exist
        if section.subsections:
            for subsection in section.subsections:
                if subsection.key_points:
                    for points in subsection.key_points:
                        key_points.append(f"{section.title} - {subsection.title}: {points}")  # Include parent section context in key points)
    
    return key_points