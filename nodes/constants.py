TITLE_GENERATOR = "title_generator"
TOPIC_DECOMPOSITION = "topic_decomposition"
TOPIC_CONTEXT = "topic_context"
INTERNET_SEARCH = "search_internet"
WIKIPEDIA_SEARCH = "search_wikipedia"
OUTLINE_GENERATOR = "outline_generator"
CURATE_SOURCES = "curate_sources"
DRAFT_WRITER = "draft_writer"
DRAFT_ARTICLE_APPROVAL = "draft_article_approval"
CRITIC_ARTICLE = "critique_on_article"
REVISION = "revise_article"
DECIDE_TO_REVISE = "decide_to_revise"
SAVE = "save_article"
THEME_DECOMPOSITION = "theme_decomposition"
ANALYZE_CORE_THEMES = "analyze_core_themes"
ANALYZE_IMPLIED_TOPICS = "analyze_implied_topics"
SEARCH_QUERY_GENERATOR = "search_query_generator"
SECTION_RESEARCH = "section_research"
CONTINUE_TO_RESEARCH = "continue_to_research"
CONTINUE_TO_SEARCH = "continue_to_search"
FINALIZATION_AND_PROOFREADING = "finalization_and_proofreading"
TITLE_APPROVAL = "title_approval"
OUTLINE_APPROVAL = "outline_approval"
FINAL_ARTICLE_APPROVAL = "final_article_approval"


TITLE_PROMPT = """
    As an expert copywriter, craft a compelling, SEO-friendly blog title for the given topic.

    Topic: {topic}

    The title should:

    - Capture attention with strong, impactful words.
    - Convey expertise and authority on the subject.
    - Promise clear value to readers, making them eager to click.
    - Maintain professionalism while being engaging and persuasive.
    - Use power words strategically to maximize impact.
    - Include a relevant keyword naturally for SEO.
    - Avoid clickbait—it should honestly reflect the topic.
    - Consider the target audience's interests and needs for higher engagement.
    
    Generate 5 highly engaging and SEO-friendly blog titles that meet these criteria.
    
    Return the titles without quotes or additional text in comma separated list.
    """ 

OUTLINE_SYS_MSG = """
    You are an AI critical thinker research assistant.
    Your sole purpose is to write outline on given a topic using a list of articles
    """

OUTLINE_USER_MSG = """
    Based on the provided theme analyses and implied topic relationships, create a comprehensive blog outline that incorporates the following elements:

    Core Theme Analysis:
    {theme_analysis}

    Implied Topic Analysis:
    {implied_topic_analysis}

    Please organize these elements into a structured outline following these guidelines:

    1. Create a hierarchical structure that:
       - Uses the most significant themes as main sections
       - Develops logical subsections from related subtopics
       - Incorporates implied topics where they naturally connect to main themes
       - Maintains proper flow between related concepts

    2. For each main section, consider:
       - The WHO (relevant audiences and experts)
       - The WHAT (key concepts and processes)
       - The WHERE (relevant contexts and locations)
       - The WHEN (temporal aspects and historical significance)
       - The WHY (importance and implications)
       - The HOW (methods and implementations)

    3. Ensure the outline:
       - Progresses logically from foundational to advanced concepts
       - Creates smooth transitions between related themes
       - Balances coverage across all identified themes
       - Clearly shows relationships between interconnected topics
       - Integrates implied topics at appropriate points

    Please output a detailed outline with:
    - Clear hierarchical structure (using proper numbering and indentation)
    - Main sections and subsections
    - Supporting points and key details
    - Integration points for implied topics
    """

CURATE_SYS_MSG = """"You are a personal blog writer. Your sole purpose is to choose {num_of_article} most relevant url.\n """

CURATE_USER_MSG = """
    Your task is to return the {num_of_article} most relevant urls from source urls delimited by triple # 
    that cover the following topics delimited by angle brackets < >:
    <Topics: {topics}>
    ###
    Source Urls:
    {sources}
    ###
    Please make sure that your selected URLs should present in above sources.
    """


WRITER_SYS_MSG = """
    You are an AI critical thinker research assistant.
    Your sole purpose is to write well written, critically acclaimed, objective and structured blog on given a topic using a list of articles.
    Always write a blog with a clear and concise structure, and make sure to not deter to general and meaningless conclusions.
    Also use plain and simple English to write the blog.
    """

WRITER_USER_MSG = """
    Your task is to write a critically acclaimed article on topic {topic} with title {title} 
    based on the following sources delimited by ###:

    ###
    {sources}
    ###
    
    You MUST determine your own concrete and valid opinion based on the given information. Do NOT deter to general and meaningless conclusions.
    Write all used source urls at the end of the report, and make sure to not add duplicated sources, but only one reference for each.
    Instruction to write the article is as follows:
    1. Write article based on the following outline: {outline}  
    2. Add references at the end of the article.
    3. use plain and simple English to write the blog.
    4. You must write the article with markdown syntax
    5. Artcle should be based on sources provided.
    """

CRITIQUE_SYS_MSG = """
    You are a blog writing critique. Your sole purpose is to provide short feedback on a written article so the writer will know what to fix.\n "
    """

CRITIQUE_PROMPT = """
    As an expert reviewer, provide a **constructive critique** of the following draft. Focus primarily on **content, clarity, and structure**, rather than minor grammar or typos.  

    ### **Key Review Criteria:**  
    1. **Engagement & Clarity:**  
    - Does the **introduction grab attention** and set clear expectations?  
    - Are the **ideas well-supported** and logically presented?  
    - Are there any **gaps** where the reader might feel confused or need more information?  

    2. **Structure & Flow:**  
    - Is the **order of information logical**, or does it need reorganization?  
    - Are transitions smooth, guiding the reader from one idea to the next?  

    3. **Relevance & Depth:**  
    - Does each section **deliver valuable insights** without unnecessary repetition?  
    - Are there parts that **stray off-topic** and should be trimmed or refined?  

    4. **Consistency & Tone:**  
    - Is the **tone appropriate** for the intended audience?  
    - Are there shifts in tone (e.g., too formal or informal) that need adjustment?  

    ### **Actionable Feedback Format:**  
    - Highlight **what works well** and why.  
    - Identify **what needs improvement** with specific suggestions.  
    - If possible, propose **alternative phrasing** or structural improvements.  

    If the critique suggests major content gaps or reordering, provide a **brief outline** of how the information could be better structured.  

    ### **Draft for Review:**  
    {article}

    Provide a **detailed, constructive critique** following the above criteria. 
"""

REVISOR_SYS_MSG = """
    You are a article editor. Your sole purpose is to edit a well-written article about a topic based on given critique.
    use plain and simple English to write the blog.
    """

REVISION_PROMPT = """
    I need to **revise and improve** a blog post based on critique notes. Revision is where the writing takes shape, so focus on **clarity, structure, flow, and content improvements** rather than just minor edits.  

    ### **Provided Materials:**  
    - **Draft to Revise:** {draft}  
    - **Critique Notes:** {critique}  

    ### **Revision Guidelines:**  

    #### **1. Address Major Issues First (Content & Structure):**  
    - Clarify explanations where needed.  
    - Reorganize paragraphs for better **flow and logical progression**.  
    - Add missing details or supporting information.  
    - Remove **unnecessary fluff** or off-topic content.  
    - Ensure each section stays **focused** on its purpose and contributes to the main point.  

    #### **2. Refine Writing & Transitions:**  
    - Strengthen the **introduction** to clearly set expectations for the reader.  
    - Ensure **smooth transitions** between sections and ideas.  
    - Improve **wording and sentence structure** for clarity and engagement.  
    - Strengthen the **conclusion** so it ties everything together and provides a sense of closure.  

    #### **3. Fact-Checking & Accuracy:**  
    - Verify that all facts, quotes, and references are **accurate and correctly attributed**.  
    - Ensure no **errors were introduced** while editing.  

    #### **4. Revision Rounds:**  
    Revise in **rounds**, tackling:  
    1. **Major content and structural changes** first.  
    2. **Refining language, style, and transitions** next.  
    3. **Final polish**, ensuring the post is clear, concise, and engaging.  

    ### **Final Instructions:**  
    - Revise the provided draft **while addressing the critique notes**.  
    - Ensure the final version **clearly communicates the intended message**.  
    - The revised blog should feel **cohesive, well-structured, and engaging**.  

    Now, generate the **revised blog post** based on these guidelines.
    """

TOPIC_DECOMPOSITION_PROMPT = """You are a helpful assistant that generates multiple sub-questions related to an input topic. \n
    The goal is to break down the topic into a set of sub-problems / sub-questions that can be answers in isolation. \n
    Generate multiple search queries related to: {topic} \n
    Output (5 queries):
    """

TOPIC_CONTEXT = """
    I want to write an article on topic {topic}. What should I cover in this article. 
    List only the title of the different context that I should cover.
    """

THEME_DECOMPOSITION_PROMPT = """
    You are an expert content analyst and thematic researcher. Your task is to analyze and break down the given topic into a structured theme decomposition that will guide blog content creation.

    Topic for analysis: {topic}

    Requirements:

    1. Core Themes (3-5 themes required):
    - Each theme must have:
        * A clear, concise name
        * A brief description explaining its relevance
        * 1-3 related concepts that support or expand the theme
    - Themes should be distinct but interconnected
    - Cover the essential aspects of the topic

    2. Implied Topics (at least 1):
    - List underlying themes not explicitly stated in the topic
    - Include relevant contextual or background topics
    - Consider potential implications or future developments

    3. Scope Boundaries (at least 1):
    - Define clear limits for the content
    - Specify what aspects should be included or excluded
    - Help maintain focus and prevent topic drift

    Return ONLY a valid JSON object with no additional text or formatting. The JSON must follow this structure:
    {{
        "core_themes": [
            {{
                "theme": "string",
                "description": "string",
                "related_concepts": ["string", "string", "string"]
            }}
        ],
        "implied_topics": ["string"],
        "scope_boundaries": ["string"]
    }}

    Your response must:
    - Contain only the JSON object, no markdown formatting or other text
    - Have exactly the structure shown above
    - Include the required number of items for each section
    - Use clear, specific language
    - Be suitable for blog content creation
"""

THEME_ANALYSIS_PROMPT = """
    Analyze the following core themes using the 5W's + H framework to generate comprehensive subtopics. For each theme, consider:

    WHO:
    - Who is affected by this theme?
    - Who are the key stakeholders?
    - Who has expertise in this area?

    WHAT:
    - What are the core components?
    - What are the key challenges or opportunities?
    - What are the main processes or activities involved?

    WHERE:
    - Where is this theme most relevant?
    - Where are the geographical or contextual implications?
    - Where can this be applied or implemented?

    WHEN:
    - When did this become important?
    - When are the critical timeframes or deadlines?
    - When should different aspects be considered?

    WHY:
    - Why is this theme significant?
    - Why should readers care about this?
    - Why does this matter in the current context?

    HOW:
    - How does this work in practice?
    - How can this be implemented or achieved?
    - How does this impact different stakeholders?

    Keep in mind these scope boundaries while analyzing:
    {scope_boundaries}

    Core Themes to Analyze:
    {themes}

    Return the analysis in the following JSON format:
    {{
        "theme_analysis": [
            {{
                "theme_name": "Theme Name",
                "who": ["point 1", "point 2", "point 3"],
                "what": ["point 1", "point 2", "point 3"],
                "where": ["point 1", "point 2", "point 3"],
                "when": ["point 1", "point 2", "point 3"],
                "why": ["point 1", "point 2", "point 3"],
                "how": ["point 1", "point 2", "point 3"]
            }}
        ]
    }}

    Focus on generating specific, actionable, and relevant subtopics that will provide value to the readers while staying within the defined scope boundaries.
"""

IMPLIED_TOPIC_ANALYSIS_PROMPT = """
    Analyze the following implied topics in the context of the core themes. For each implied topic, determine:

    1. Relevance:
    - How does this topic relate to each core theme?
    - What makes this topic important to the overall discussion?

    2. Key Considerations:
    - What are the critical aspects to consider?
    - What potential challenges or opportunities exist?
    - What nuances need to be addressed?

    3. Impact Analysis:
    - How does this topic affect the main themes?
    - What are the broader implications?
    - What potential future developments should be considered?

    4. Integration Points:
    - Where should this topic be discussed within the core themes?
    - How can it be seamlessly incorporated into the content?
    - What connections should be highlighted?

    Core Themes (for context):
    {themes}

    Implied Topics to Analyze:
    {implied_topics}

    Scope Boundaries to Consider:
    {scope_boundaries}

    Return the analysis in the following JSON format:
    {{
        "implied_topic_analysis": [
            {{
                "topic_name": "Topic Name",
                "relevance": ["point 1", "point 2", "point 3"],
                "considerations": ["point 1", "point 2", "point 3"],
                "impact": ["point 1", "point 2", "point 3"],
                "integration_points": ["point 1", "point 2", "point 3"]
            }}
        ]
    }}

    Focus on providing insights that will help integrate these topics meaningfully into the content while respecting the scope boundaries.
"""

SUBTOPIC_BRAINSTORM_PROMPT = """
    Given the following themes, implied topics, and scope boundaries from a blog topic, analyze each using the 5W's + H framework to generate comprehensive subtopics.

    For each theme and implied topic, consider:

    WHO:
    - Who is affected by this theme/topic?
    - Who are the key stakeholders?
    - Who has expertise in this area?

    WHAT:
    - What are the core components?
    - What are the key challenges or opportunities?
    - What are the main processes or activities involved?

    WHERE:
    - Where is this theme/topic most relevant?
    - Where are the geographical or contextual implications?
    - Where can this be applied or implemented?

    WHEN:
    - When did this become important?
    - When are the critical timeframes or deadlines?
    - When should different aspects be considered?

    WHY:
    - Why is this theme/topic significant?
    - Why should readers care about this?
    - Why does this matter in the current context?

    HOW:
    - How does this work in practice?
    - How can this be implemented or achieved?
    - How does this impact different stakeholders?

    Keep in mind the following scope boundaries while analyzing:
    {scope_boundaries}

    For the following themes and implied topics:

    Core Themes:
    {themes}

    Implied Topics:
    {implied_topics}

    Return the analysis in the following JSON format:
    {{
        "theme_analysis": [
            {{
                "theme_name": "Theme or Topic Name",
                "is_implied": false,
                "who": ["point 1", "point 2", "point 3"],
                "what": ["point 1", "point 2", "point 3"],
                "where": ["point 1", "point 2", "point 3"],
                "when": ["point 1", "point 2", "point 3"],
                "why": ["point 1", "point 2", "point 3"],
                "how": ["point 1", "point 2", "point 3"]
            }}
        ]
    }}

    Focus on generating specific, actionable, and relevant subtopics that will provide value to the readers while staying within the defined scope boundaries.
"""

SECTION_RESEARCH_PROMPT = """
    Research the following section of a blog outline, using the provided theme analysis and implied topic relationships:

    Section to Research:
    {section}

    Key points to cover:
    {key_points}
    
    Theme Analysis Context:
    {theme_analysis}

    Implied Topic Relationships:
    {implied_topic_analysis}

    Please provide comprehensive research findings in the following structure:

    1. Key Points:
       - Main arguments and concepts
       - Critical insights
       - Important definitions

    2. Supporting Evidence:
       - Relevant statistics
       - Research findings
       - Case studies
       - Examples

    3. Expert Opinions:
       - Quotes from authorities
       - Professional perspectives
       - Industry insights

    4. Sources:
       - Academic papers
       - Industry reports
       - Expert articles
       - Reliable websites

    Ensure the research:
    - Aligns with the themes and topics identified
    - Provides concrete evidence and examples
    - Includes diverse perspectives
    - Uses credible and recent sources
    - Maintains appropriate scope and depth
    """


DRAFT_PROMPT = """
    I need a **complete, well-structured, and engaging blog post** based on the following specifications:  

    ---

    ### **Title:**  
    {title}  

    ### **Blog Structure:**  
    {blog_outline}  

    ### **Available Sources and Key Points:**  
    {web_sources}  

    ---

    ### **Writing Guidelines:**  

    #### **1. Audience & Tone:**  
    - Write as if you're **speaking directly to the reader** to keep the tone **engaging, clear, and professional**.  
    - Ensure the **language is accessible**, resonating with the **target audience**.  
    - Use **strong, impactful words** to maintain authority and credibility.  

    #### **2. Structure & Flow:**  
    - Follow the **exact structure provided in the blog outline** to ensure clarity and logical flow.  
    - Use **natural transitions** between sections for a smooth reading experience.  
    - Maintain **logical progression**, ensuring ideas build upon each other cohesively.  
    - Use **proper paragraph breaks** to enhance readability.  

    #### **3. Content & Clarity:**  
    - Incorporate **relevant insights from the provided sources** to add depth and credibility.  
    - **Use concrete examples** to illustrate key points, making abstract ideas more relatable.  
    - Ensure **each section delivers valuable insights** while avoiding unnecessary repetition or off-topic details.  

    #### **4. Drafting Mindset:**  
    - **Focus on getting ideas down** without excessive self-editing—perfection comes later.  
    - If any section feels incomplete, **push forward** and refine in later drafts.  
    - Think of this draft as **building a strong foundation**—it’s okay if some parts need polishing.  

    #### **5. Formatting & Citations:**  
    - Write in **proper Markdown format** (`#` for the title, `##` for sections, `###` for subsections).  
    - **Cite sources in an academic style** where necessary.  
    - Ensure that **each section remains focused** while maintaining an **overall logical flow**.  

    ---

    ### **Final Instructions:**  
    Write a **fully developed blog post** in **Markdown format**, ensuring it is **engaging, well-researched, and structured** according to the provided outline.  

"""

FINALIZATION_AND_PROOFREADING_PROMPT = """ 
    You are an expert editor and content finalization assistant. Your task is to **thoroughly proofread and finalize** the given blog post to make it **publish-ready**. 
    
    {blog_post}

    Follow these steps:

    1. **Proofreading & Grammar Check:**  
    - Identify and correct **typos, spelling mistakes, and grammatical errors**.  
    - Ensure **sentence clarity and conciseness**, restructuring sentences if necessary for readability.  
    - Check for **punctuation consistency**, ensuring proper usage of commas, periods, and other punctuation marks.  

    2. **Formatting & Consistency:**  
    - Ensure **headings, subheadings, and bullet points** are consistently formatted.  
    - Confirm that **bold, italic, and other text styles** are used appropriately and consistently.  
    - Verify that paragraphs are **structured properly** for easy readability.  

    3. **Hyperlinks & Multimedia Verification:**  
    - Identify any **broken or misplaced links** and suggest corrections.  
    - Ensure all **images, charts, and multimedia elements** are correctly placed and relevant.  
    - Verify that **captions and alt text** for images are present and optimized for **SEO and accessibility**.  

    4. **SEO & Meta Description:**  
    - Ensure the **title and headings** are clear, engaging, and include relevant keywords naturally.  
    - If required, generate a **meta description** (1-2 sentence summary) optimized for **search engines (SEO)**.  

    5. **Final Readability Check:**  
    - Read the blog post as a whole and ensure it **flows smoothly** from start to finish.  
    - Ensure the **tone and style are consistent** throughout the piece.  
    - Break long paragraphs into smaller, more digestible chunks if necessary.  

    ### **Output Format:**  
    Provide the **fully proofread and finalized blog post**, incorporating all corrections and optimizations. 
"""