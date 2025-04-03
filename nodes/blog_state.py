import operator
from typing import Annotated, List, Optional, Sequence, TypedDict
from pydantic import BaseModel, Field

class CoreTheme(BaseModel):
    """Represents a core theme with its description and related concepts."""
    theme: str = Field(..., description="Name of the theme")
    description: str = Field(..., description="Brief description of the theme")
    related_concepts: List[str] = Field(
        ...,
        description="List of concepts related to this theme",
    )

class ThemeDecomposition(BaseModel):
    """Represents the complete theme decomposition of a topic."""
    core_themes: List[CoreTheme] = Field(
        ...,
        description="List of core themes identified in the topic",
    )
    implied_topics: List[str] = Field(
        ...,
        description="List of implicit or underlying themes not directly stated",
    )
    scope_boundaries: List[str] = Field(
        ...,
        description="List of boundaries defining the scope of the content",
    )

class ThemeAnalysis(BaseModel):
    """Represents the 5W's + H analysis of a core theme."""
    theme_name: str = Field(..., description="Name of the theme being analyzed")
    who: List[str] = Field(..., description="Who-related aspects of the theme")
    what: List[str] = Field(..., description="What-related aspects of the theme")
    where: List[str] = Field(..., description="Where-related aspects of the theme")
    when: List[str] = Field(..., description="When-related aspects of the theme")
    why: List[str] = Field(..., description="Why-related aspects of the theme")
    how: List[str] = Field(..., description="How-related aspects of the theme")

class ThemeAnalyses(BaseModel):
    theme_analysis: List[ThemeAnalysis] = Field(
        ...,
        description="Analysis of each theme",
    )

class ImpliedTopicAnalysis(BaseModel):
    """Represents the analysis of an implied topic."""
    topic_name: str = Field(..., description="Name of the implied topic")
    relevance: List[str] = Field(..., description="How this topic relates to core themes")
    considerations: List[str] = Field(..., description="Key points to consider about this topic")
    impact: List[str] = Field(..., description="How this topic impacts the overall content")
    integration_points: List[str] = Field(..., description="Where this topic should be integrated into core themes")


class ImpliedTopicAnalyses(BaseModel):
    """Represents the analysis of an implied topic."""
    implied_topic_analysis: List[ImpliedTopicAnalysis]


class SectionResearch(BaseModel):
    """Represents research findings for a section of the blog outline."""
    section_title: str = Field(..., description="Title of the section being researched")
    key_points: List[str] = Field(..., description="Key points and findings from research")
    supporting_evidence: List[str] = Field(..., description="Supporting evidence, facts, or statistics")
    sources: List[str] = Field(..., description="Sources used for research")
    expert_opinions: List[str] = Field(..., description="Relevant expert opinions or quotes")

# class OutlineResearch(BaseModel):
#     """Collection of research for all sections."""
#     section_research: List[SectionResearch] = Field(..., description="Research for each section")

class SubSection(BaseModel):
    """Represents a subsection in the blog outline"""
    title: str = Field(description="Title of the subsection")
    key_points: List[str] = Field(description="List of key points to cover in this subsection")

class Section(BaseModel):
    """Represents a main section in the blog outline"""
    title: str = Field(description="Title of the main section")
    key_points: List[str] = Field(description="List of key points to cover in this section")
    subsections: Optional[List[SubSection]] = Field(
        default=None,
        description="List of subsections within this main section"
    )

class BlogOutline(BaseModel):
    """Represents the complete blog outline structure"""
    sections: List[Section] = Field(description="List of main sections in the blog outline")


class BlogState(TypedDict):
    topic: str
    titles: list[str]
    title: str
    decomposition: ThemeDecomposition
    theme_analysis: ThemeAnalyses
    implied_topic_analysis: ImpliedTopicAnalyses
    outline: BlogOutline
    cluster_queries: List[str]
    web_sources: list[str]
    sources: Annotated[list[SectionResearch], operator.add]
    web_sources: Annotated[list[str], operator.add]
    article: str
    iteration: int
    critique: Optional[str]
    message: Optional[str]
    



class ResearchState(TypedDict):
    section: str
    key_points: list[str]
    theme_analysis: dict
    implied_topic_analysis: dict

class SearchState(TypedDict):
    topic: str
    search_count: int

