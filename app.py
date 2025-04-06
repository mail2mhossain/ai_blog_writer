import os
import io
import re
import json
import uuid
import markdown
import zipfile
import asyncio
from pathlib import Path

# Fix for event loop error
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# Disable Streamlit's file watcher to prevent PyTorch conflicts
os.environ['STREAMLIT_SERVER_WATCH_DIRS'] = 'false'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'

import streamlit as st
from graph_executer import generate_title, generate_outline, generate_article, finalize_article
from nodes.blog_state import BlogOutline
from dotenv import load_dotenv, set_key
from decouple import config
from decouple import AutoConfig

load_dotenv()
config = AutoConfig()
data_directory = os.path.join(os.path.dirname(__file__), "data")


# Initialize session states
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = ''
if 'last_report' not in st.session_state:
    st.session_state['last_report'] = None
if 'topic' not in st.session_state:
    st.session_state['topic'] = ''
if 'selected_title' not in st.session_state:
    st.session_state['selected_title'] = ""
if 'edited_title' not in st.session_state:
    st.session_state['edited_title'] = ""
if 'tavily_api_key' not in st.session_state:
    st.session_state['tavily_api_key'] = config("TAVILY_API_KEY", default="")
if 'openai_api_key' not in st.session_state:
    st.session_state['openai_api_key'] = config("OPENAI_API_KEY", default="")
if 'gpt_model' not in st.session_state:
    st.session_state['gpt_model'] = config("GPT_MODEL", default="gpt-4o")

def update_env_variable(key, value):
    env_path = ".env"
    set_key(env_path, key, value)

def sanitize_filename(query):
    # Remove special characters and limit filename length
    sanitized = re.sub(r'[^a-zA-Z0-9_\- ]', '', query)  # Allow only alphanumeric, underscore, hyphen, and space
    sanitized = "_".join(sanitized.split())  # Replace spaces with underscores
    return sanitized[:50]  # Limit to 50 characters for readability

def download_png_files(png_paths):
    png_files = {}
    for path in png_paths:
        try:
            with open(path, 'rb') as f:
                png_files[Path(path).name] = f.read()
        except FileNotFoundError:
            st.warning(f"File {path} not found")
            
    return png_files

def download_reports(query, report):
    markdown_content = f"# Query: {query}\n\n{report}"
    markdown_file = io.StringIO(markdown_content)  # Use StringIO to create an in-memory file
    filename = sanitize_filename(query) + ".md"
    download_key = str(uuid.uuid4())
    st.download_button(
        label="Download Report as Markdown",
        data=markdown_file.getvalue(),
        file_name=filename,
        mime="text/markdown",
        key=download_key
    )

def download_reports_with_png(query, report):
    # Extract PNG file paths from the markdown report
    pattern = r'!\[.*?\]\((.*?\.png)\)'
    png_paths = re.findall(pattern, report)
    
    # Download or collect PNG files
    png_files = download_png_files(png_paths)

    # Create a ZIP file in-memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        # Add markdown report to the ZIP
        markdown_content = f"# Query: {query}\n\n{report}"
        markdown_filename = sanitize_filename(query) + ".md"
        zip_file.writestr(markdown_filename, markdown_content)

        # Add PNG files to the ZIP
        for file_name, content in png_files.items():
            zip_file.writestr(f"images/{file_name}", content)

    zip_buffer.seek(0)  # Move the buffer pointer to the start

    # Offer the ZIP file as a download
    zip_filename = sanitize_filename(query) + ".zip"
    download_key = str(uuid.uuid4())
    st.download_button(
        label="Download Report",
        data=zip_buffer,
        file_name=zip_filename,
        mime="application/zip",
        key=download_key
    )

def update_headings(text):
    # Replace headings in the order from largest to smallest to prevent conflicts
    text = re.sub(r'(?m)^###### ', '######## ', text)  # Handle heading 6, if any
    text = re.sub(r'(?m)^##### ', '####### ', text)
    text = re.sub(r'(?m)^#### ', '###### ', text)
    text = re.sub(r'(?m)^### ', '##### ', text)
    text = re.sub(r'(?m)^## ', '#### ', text)
    text = re.sub(r'(?m)^# ', '### ', text)
    return text

def display_reports(markdown_text):
    # Regex to find image references and capture captions and paths
    image_pattern = r'!\[(.*?)\]\((.*?)\)'

    # Split the markdown text into segments by images
    parts = re.split(image_pattern, markdown_text)

    # Find all image references to extract their captions and paths
    image_matches = re.findall(image_pattern, markdown_text)

    # Display the content and images alternately
    text_index = 0

    if len(image_matches) == 0:
        # No images found, display the full markdown text at once
        st.markdown(markdown_text)
    else:
        # Proceed with the original loop logic if there are images
        for i in range(len(parts)):
            if i % 3 == 0:
                st.markdown(parts[i])
            elif i % 3 == 1:
                if text_index < len(image_matches):
                    caption, path = image_matches[text_index]
                    if os.path.exists(path):
                        st.image(path.strip(), caption=caption)
                    text_index += 1

# Callback function to update session state when radio selection changes
def update_selected_title():
    if 'title_options' in st.session_state:
        st.session_state['selected_title'] = st.session_state['title_options']
        # Also update the edited_title to match the selected title
        st.session_state['edited_title'] = st.session_state['title_options']

def execute_generate_title():
    with st.spinner("Generating Title..."):
        st.session_state['topic'] = st.session_state['topic_input']
        thread_id = str(uuid.uuid4())
        st.session_state['thread_id'] = thread_id
        st.session_state['titles'] = generate_title(st.session_state['topic'], st.session_state['thread_id'])
        # Store the generated titles in session state for display after form submission


def outline_to_markdown(outline):
    """Convert BlogOutline object to markdown format for editing"""
    try:
        # Try to parse as JSON if it's a string
        if isinstance(outline, str):
            try:
                import json
                outline_dict = json.loads(outline)
            except:
                # If it's already in markdown format, return as is
                if '# ' in outline or '## ' in outline:
                    return outline
                return f"Error parsing outline: {outline}"
        elif hasattr(outline, 'model_dump'):
            # If it's a Pydantic model (BlogOutline)
            outline_dict = outline.model_dump()
        elif hasattr(outline, 'dict') and callable(getattr(outline, 'dict')):
            # If it's a Pydantic v1 model
            outline_dict = outline.dict()
        else:
            # If it's already a dict
            outline_dict = outline
        
        markdown = ""
        
        # Process sections
        sections = outline_dict.get('sections', [])
        if not sections and isinstance(outline_dict, list):
            # If outline_dict is already a list of sections
            sections = outline_dict
            
        for i, section in enumerate(sections):
            # Handle both dict and object access
            if hasattr(section, 'title'):
                section_title = section.title
            else:
                section_title = section.get('title', f"Section {i+1}")
                
            markdown += f"# {section_title}\n\n"
            
            # Add section key points
            if hasattr(section, 'key_points'):
                key_points = section.key_points
            else:
                key_points = section.get('key_points', [])
                
            if key_points:
                markdown += "**Key Points:**\n\n"
                for point in key_points:
                    markdown += f"- {point}\n"
                markdown += "\n"
            
            # Process subsections
            if hasattr(section, 'subsections'):
                subsections = section.subsections or []
            else:
                subsections = section.get('subsections', [])
                
            if subsections:
                for j, subsection in enumerate(subsections):
                    if hasattr(subsection, 'title'):
                        subsection_title = subsection.title
                    else:
                        subsection_title = subsection.get('title', f"Subsection {j+1}")
                        
                    markdown += f"## {subsection_title}\n\n"
                    
                    # Add subsection key points
                    if hasattr(subsection, 'key_points'):
                        sub_key_points = subsection.key_points
                    else:
                        sub_key_points = subsection.get('key_points', [])
                        
                    if sub_key_points:
                        markdown += "**Key Points:**\n\n"
                        for point in sub_key_points:
                            markdown += f"- {point}\n"
                        markdown += "\n"
        
        return markdown
    except Exception as e:
        import traceback
        return f"Error converting outline to markdown: {str(e)}\n\n{traceback.format_exc()}\n\nRaw outline: {outline}"

def markdown_to_outline(markdown_text):
    """Convert markdown format back to BlogOutline object"""
    try:
        sections = []
        current_section = None
        current_subsection = None
        section_key_points = []
        subsection_key_points = []
        collecting_section_points = False
        collecting_subsection_points = False
        
        lines = markdown_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Main section heading
            if line.startswith('# '):
                # Save previous section if exists
                if current_section:
                    if collecting_section_points:
                        current_section['key_points'] = section_key_points
                    sections.append(current_section)
                
                # Start new section
                section_title = line[2:].strip()
                current_section = {
                    'title': section_title,
                    'key_points': [],
                    'subsections': []
                }
                section_key_points = []
                collecting_section_points = False
                collecting_subsection_points = False
            
            # Subsection heading
            elif line.startswith('## '):
                # Save previous subsection if exists
                if current_subsection and current_section:
                    if collecting_subsection_points:
                        current_subsection['key_points'] = subsection_key_points
                    current_section['subsections'].append(current_subsection)
                
                # Start new subsection
                subsection_title = line[3:].strip()
                current_subsection = {
                    'title': subsection_title,
                    'key_points': []
                }
                subsection_key_points = []
                collecting_section_points = False
                collecting_subsection_points = False
            
            # Key points marker
            elif line.startswith('**Key Points:**'):
                if current_subsection:
                    collecting_subsection_points = True
                    collecting_section_points = False
                else:
                    collecting_section_points = True
                    collecting_subsection_points = False
            
            # Key point item
            elif line.startswith('- '):
                point = line[2:].strip()
                if collecting_subsection_points and current_subsection:
                    subsection_key_points.append(point)
                elif collecting_section_points and current_section:
                    section_key_points.append(point)
        
        # Add the last section and subsection
        if current_subsection and current_section:
            if collecting_subsection_points:
                current_subsection['key_points'] = subsection_key_points
            current_section['subsections'].append(current_subsection)
        
        if current_section:
            if collecting_section_points:
                current_section['key_points'] = section_key_points
            sections.append(current_section)
        
        return {'sections': sections}
    except Exception as e:
        st.error(f"Error converting markdown to outline: {str(e)}")
        return {'sections': []}

# Callback functions for section and subsection operations
def add_section():
    if 'outline_data' not in st.session_state:
        return
    
    # Get current outline data
    outline_data = st.session_state['outline_data']
    if 'sections' not in outline_data:
        outline_data['sections'] = []
    
    # Add new section
    new_section = {
        'title': "New Section",
        'key_points': ["Add key points here"],
        'subsections': []
    }
    outline_data['sections'].append(new_section)
    
    # Update session state
    st.session_state['outline_data'] = outline_data
    st.session_state['outline'] = json.dumps(outline_data, indent=4)

def delete_section(section_index):
    if 'outline_data' not in st.session_state:
        return
    
    # Get current outline data
    outline_data = st.session_state['outline_data']
    if 'sections' not in outline_data or section_index >= len(outline_data['sections']):
        return
    
    # Remove the section
    outline_data['sections'].pop(section_index)
    
    # Update session state
    st.session_state['outline_data'] = outline_data
    st.session_state['outline'] = json.dumps(outline_data, indent=4)

def add_subsection(section_index):
    if 'outline_data' not in st.session_state:
        return
    
    # Get current outline data
    outline_data = st.session_state['outline_data']
    if 'sections' not in outline_data or section_index >= len(outline_data['sections']):
        return
    
    # Get the section
    section = outline_data['sections'][section_index]
    if 'subsections' not in section:
        section['subsections'] = []
    
    # Add new subsection
    new_subsection = {
        'title': "New Subsection",
        'key_points': ["Add key points here"]
    }
    section['subsections'].append(new_subsection)
    
    # Update session state
    st.session_state['outline_data'] = outline_data
    st.session_state['outline'] = json.dumps(outline_data, indent=4)

def delete_subsection(section_index, subsection_index):
    if 'outline_data' not in st.session_state:
        return
    
    # Get current outline data
    outline_data = st.session_state['outline_data']
    if 'sections' not in outline_data or section_index >= len(outline_data['sections']):
        return
    
    # Get the section
    section = outline_data['sections'][section_index]
    if 'subsections' not in section or subsection_index >= len(section['subsections']):
        return
    
    # Remove the subsection
    section['subsections'].pop(subsection_index)
    
    # Update session state
    st.session_state['outline_data'] = outline_data
    st.session_state['outline'] = json.dumps(outline_data, indent=4)

def execute_generate_outline():
    with st.spinner("Generating Outline..."):
        if 'edited_title' in st.session_state and st.session_state['edited_title']:
            try:
                # Generate the outline using the edited title
                outline = generate_outline(st.session_state['edited_title'], st.session_state['thread_id'])
                
                outline_json = outline.model_dump_json(indent=4)
                
                # Store the outline in session state
                st.session_state['outline'] = outline_json
                # print(f"\nBlog Outline:\n{st.session_state['outline']}")
                
                # Parse the outline JSON and store in session state
                st.session_state['outline_data'] = json.loads(outline_json)
                
                # Convert to markdown for display and editing
                markdown_outline = outline_to_markdown(outline)
                st.session_state['markdown_outline'] = markdown_outline
                
                # Hide the title section
                st.session_state['show_title_section'] = False
                
                # Clear the title data but keep the final title
                st.session_state['titles'] = []
                st.session_state['topic'] = ""
                
                # Rerun to refresh the UI
                st.rerun()
            except Exception as e:
                import traceback
                st.error(f"Error generating outline: {str(e)}")
                print(f"Error details: {traceback.format_exc()}")
        else:
            st.error("Please select or edit a title first.")

def execute_generate_article():
    with st.spinner("Researching and Drafting Article..."):
        try:
            # Convert the processed outline to a BlogOutline object if it's not already
            if not isinstance(st.session_state['processed_outline'], BlogOutline):
                try:
                    # If it's a dictionary, convert it to a BlogOutline object
                    outline_dict = st.session_state['processed_outline']
                    blog_outline = BlogOutline(**outline_dict)
                    st.session_state['processed_outline'] = blog_outline
                    # st.success("Outline converted to BlogOutline successfully!")
                except Exception as e:
                    st.error(f"Failed to convert outline to BlogOutline: {str(e)}")
                    return
            
            # Generate the article using the processed outline
            st.success("Researching and Drafting article...")
            article = generate_article(st.session_state['processed_outline'], st.session_state['thread_id'])
            
            # Store the article in session state
            st.session_state['generated_article'] = article
            
            # Initialize critique if not already present
            if 'article_critique' not in st.session_state:
                st.session_state['article_critique'] = ""
                
            # Initialize edited article if not already present
            if 'edited_article' not in st.session_state:
                st.session_state['edited_article'] = article
                
            # Set flags to show only article section
            st.session_state['show_article_section'] = True
            st.session_state['show_outline_only'] = False
            st.session_state['show_article_only'] = True
            
            # Rerun to display the article section
            st.rerun()
        except Exception as e:
            import traceback
            st.error(f"Error generating article: {str(e)}")
            print(f"Error details: {traceback.format_exc()}")

def execute_finalize_article():
    with st.spinner("Finalizing the article..."):
        st.success("Finalizing the article...")
        title, article = finalize_article(st.session_state['edited_article'], st.session_state['article_critique'], st.session_state['thread_id'])
        
        # Store the finalized article in session state
        st.session_state['finalized_article'] = article
        st.session_state['edited_title'] = title
        st.session_state['show_final_article'] = True
        
        # Rerun to display the finalized article
        st.rerun()


def display_article_critique():
    """Display the draft article with critique capabilities"""
    st.subheader("Draft Article")
    
    # Create two tabs - one for viewing and one for editing
    view_tab, edit_tab = st.tabs(["View Article", "Edit Article"])
    
    # Tab 1: View the draft article
    with view_tab:
        st.markdown(st.session_state['edited_article'])
    
    # Tab 2: Edit the draft article
    with edit_tab:
        edited_article = st.text_area(
            "Edit Article:",
            value=st.session_state['edited_article'],
            height=500,
            key="article_editor"
        )
        st.session_state['edited_article'] = edited_article
    
    # Message for user guidance
    st.markdown("**Provide critique in the box below.**")
    
    # Critique text box
    critique = st.text_area(
        "Critique (optional):", 
        value=st.session_state.get('article_critique', ''),
        height=150,
        key="critique_box",
        help="Provide feedback or suggestions for improving the article"
    )
    st.session_state['article_critique'] = critique
    
    # Submit button for the article and critique
    if st.button("Submit Critique"):
        try:
            execute_finalize_article()
        except Exception as e:
            st.error(f"Error submitting article: {str(e)}")

# This function is no longer needed as its functionality has been moved directly into write_blog
# Keeping it as a placeholder to avoid breaking any other code that might call it
def display_article_section():
    """This function is deprecated. Its functionality has been moved into write_blog."""
    # Simply redirect to the appropriate section in write_blog by setting flags
    if not st.session_state.get('show_article_section', False):
        st.session_state['show_article_section'] = True
        st.rerun()

# Title of the app
st.title("Blog Magic: AI Content Creation")


def write_blog():
    st.subheader("Blog Writer")

    if not all([st.session_state['openai_api_key'], st.session_state['gpt_model']]):
        st.info("First Configure OpenAI API Key and Model Name in the 'Configuration' tab.")
    
    # Initialize session states if they don't exist
    if 'selected_title' not in st.session_state:
        st.session_state['selected_title'] = ""
    if 'edited_title' not in st.session_state:
        st.session_state['edited_title'] = ""
    if 'markdown_outline' not in st.session_state:
        st.session_state['markdown_outline'] = ""
    if 'show_title_section' not in st.session_state:
        st.session_state['show_title_section'] = True
    if 'show_article_section' not in st.session_state:
        st.session_state['show_article_section'] = False
    if 'show_outline_only' not in st.session_state:
        st.session_state['show_outline_only'] = False
    if 'show_article_only' not in st.session_state:
        st.session_state['show_article_only'] = False
    
    # Check if we should show the article section (highest priority)
    if 'generated_article' in st.session_state and st.session_state.get('show_article_section', False):
        # Check if we have a finalized article to display
        if st.session_state.get('show_final_article', False) and 'finalized_article' in st.session_state:
            st.subheader("Final Article")
            
            # Display the finalized article in markdown format
            st.markdown(st.session_state['finalized_article'])
            
            # Add download buttons for the final article
            article_title = st.session_state.get('edited_title', 'article')
            safe_filename_md = sanitize_filename(article_title) + ".md"
            safe_filename_pdf = sanitize_filename(article_title) + ".pdf"
            
            # Create columns for the download buttons
            col1, col2 = st.columns(2)
            
            # Create a download button for the markdown file
            with col1:
                download_key_md = str(uuid.uuid4())
                st.download_button(
                    label="Download as Markdown",
                    data=st.session_state['finalized_article'],
                    file_name=safe_filename_md,
                    mime="text/markdown",
                    key=download_key_md
                )
            
            # Create a button to view as HTML (which can be printed as PDF)
            with col2:
                # Convert markdown to HTML with styling
                html = markdown.markdown(st.session_state['finalized_article'])
                html_content = f"""<!DOCTYPE html>
                <html>
                <head>
                    <title>{article_title}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                        h1 {{ color: #333366; }}
                        h2 {{ color: #333366; margin-top: 30px; }}
                        h3 {{ color: #333366; }}
                        p {{ margin-bottom: 20px; }}
                        img {{ max-width: 100%; height: auto; }}
                        @media print {{
                            body {{ margin: 1cm; }}
                        }}
                    </style>
                    <script>
                        window.onload = function() {{
                            // Add a print button
                            var printBtn = document.createElement('button');
                            printBtn.innerHTML = 'Print as PDF';
                            printBtn.style.padding = '10px 20px';
                            printBtn.style.backgroundColor = '#4CAF50';
                            printBtn.style.color = 'white';
                            printBtn.style.border = 'none';
                            printBtn.style.borderRadius = '4px';
                            printBtn.style.cursor = 'pointer';
                            printBtn.style.marginBottom = '20px';
                            printBtn.onclick = function() {{
                                this.style.display = 'none';
                                window.print();
                                this.style.display = 'block';
                            }};
                            document.body.insertBefore(printBtn, document.body.firstChild);
                        }};
                    </script>
                </head>
                <body>
                    {html}
                </body>
                </html>"""
                
                # Create download button for HTML
                download_key_html = str(uuid.uuid4())
                st.download_button(
                    label="View as HTML/Print PDF",
                    data=html_content,
                    file_name=safe_filename_pdf.replace('.pdf', '.html'),
                    mime="text/html",
                    key=download_key_html
                )
            
            # Add a button to start over
            if st.button("Start New Article"):
                # Clear all data and show title section again
                st.session_state['outline'] = ""
                st.session_state['markdown_outline'] = ""
                st.session_state['generated_article'] = ""
                st.session_state['edited_article'] = ""
                st.session_state['article_critique'] = ""
                st.session_state['finalized_article'] = ""
                st.session_state['show_title_section'] = True
                st.session_state['show_article_section'] = False
                st.session_state['show_final_article'] = False
                st.session_state['show_article_only'] = False
                st.rerun()
        else:
            # Display the article and critique functionality
            display_article_critique()
            
            # Show a button to start over completely
            if st.button("Start Over with New Topic", key="start_over_from_article"):
                # Clear all data and show title section again
                st.session_state['outline'] = ""
                st.session_state['markdown_outline'] = ""
                st.session_state['generated_article'] = ""
                st.session_state['edited_article'] = ""
                st.session_state['article_critique'] = ""
                st.session_state['show_title_section'] = True
                st.session_state['show_article_section'] = False
                st.session_state['show_outline_only'] = False
                st.session_state['show_article_only'] = False
                st.rerun()
    
    # Check if we should show the outline section (medium priority)
    elif 'outline' in st.session_state and st.session_state['outline'] and not st.session_state['show_title_section']:
        # Show a button to start over from outline
        if st.button("Start Over with New Topic", key="start_over_from_outline"):
            # Clear outline and show title section again
            st.session_state['outline'] = ""
            st.session_state['markdown_outline'] = ""
            st.session_state['show_title_section'] = True
            st.session_state['show_outline_only'] = False
            st.rerun()
    
    # Show the title section (lowest priority)
    else:
        # Show the title section
        with st.form(key='query_form'):
            topic = st.text_input("Enter your topic:", value=st.session_state['topic'], key="topic_input")
            submit_button = st.form_submit_button(label="Write Article", on_click=execute_generate_title)
        
        # Display titles after form submission if titles are available
        if 'titles' in st.session_state and st.session_state['titles']:
            st.subheader("Generated Titles")
            
            # Get the titles from session state - they should already be a proper list from graph_executer.py
            titles = st.session_state['titles']
            
            # Set the initial selected title to the first one if not already set
            if not st.session_state['selected_title'] and titles:
                st.session_state['selected_title'] = titles[0]
                st.session_state['edited_title'] = titles[0]
            
            # Display the titles as radio options
            st.radio("", titles, key="title_options", on_change=update_selected_title, index=0)
            
            # Message to guide user
            st.markdown("**Select one title from above and edit if required. After that press submit button.**")
            
            # Text box for editing the selected title
            # Only set the key, and let Session State handle the value
            st.text_input("Edit Title:", key="edited_title")
            
            # Submit button for generating outline
            if st.button("Submit Title"):
                if st.session_state['edited_title']:
                    # Set flag to show only outline after generation
                    st.session_state['show_outline_only'] = True
                    execute_generate_outline()
                else:
                    st.error("Please enter a title before submitting.")
    
    # Display outline for editing if available
    if 'outline' in st.session_state and st.session_state['outline'] and st.session_state.get('show_outline_only', False):
        st.subheader("Blog Outline")
        st.markdown("**Edit the outline below as needed:**")
        
        # Parse the JSON outline
        try:
            import json
            outline_data = json.loads(st.session_state['outline'])
            
            # Create tabs for different editing modes
            tab1, tab2 = st.tabs(["Structured Editor", "Raw JSON"])
            
            with tab1:
                # Structured editor for the outline
                st.markdown("### Add, edit, or delete sections and subsections below")
                
                # Get the sections from the outline
                sections = outline_data.get('sections', [])
                updated_sections = []
                
                # Initialize state for section operations if not already present
                if 'add_section_clicked' not in st.session_state:
                    st.session_state['add_section_clicked'] = False
                
                if 'sections_to_delete' not in st.session_state:
                    st.session_state['sections_to_delete'] = []
                    
                if 'add_subsection' not in st.session_state:
                    st.session_state['add_subsection'] = {}
                    
                if 'delete_subsection' not in st.session_state:
                    st.session_state['delete_subsection'] = {}
                
                # Handle adding a new section
                if st.session_state.get('add_section_clicked', False):
                    new_section = {
                        'title': "New Section",
                        'key_points': ["Add key points here"],
                        'subsections': []
                    }
                    sections.append(new_section)
                    st.session_state['add_section_clicked'] = False
                
                # Filter out sections marked for deletion
                sections = [section for i, section in enumerate(sections) 
                           if i not in st.session_state.get('sections_to_delete', [])]
                
                # For each section in the outline
                for i, section in enumerate(sections):
                    with st.expander(f"Section {i+1}: {section.get('title', 'Untitled Section')}"):
                        # Edit section title
                        section_title = st.text_input(f"Section {i+1} Title", 
                                                    value=section.get('title', ''), 
                                                    key=f"section_title_{i}")
                        
                        # Edit section key points
                        section_key_points_str = "\n".join(section.get('key_points', []))
                        section_key_points = st.text_area(f"Section {i+1} Key Points (one per line)", 
                                                        value=section_key_points_str,
                                                        height=100, 
                                                        key=f"section_key_points_{i}")
                        # Process key points into a list
                        key_points_list = [point.strip() for point in section_key_points.split('\n') if point.strip()]
                        
                        # Delete section button
                        if st.button(f"Delete Section {i+1}", key=f"delete_section_{i}", on_click=delete_section, args=(i,)):
                            pass  # The on_click callback handles the deletion
                        
                        # Handle subsections
                        subsections = section.get('subsections', [])
                        updated_subsections = []
                        
                        # For each subsection
                        st.markdown("**Subsections:**")
                        for j, subsection in enumerate(subsections):
                            with st.container():
                                st.markdown(f"**Subsection {j+1}:**")
                                # Edit subsection title
                                subsection_title = st.text_input(f"Subsection {j+1} Title", 
                                                            value=subsection.get('title', ''), 
                                                            key=f"subsection_title_{i}_{j}")
                                
                                # Edit subsection key points
                                subsection_key_points_str = "\n".join(subsection.get('key_points', []))
                                subsection_key_points = st.text_area(f"Subsection {j+1} Key Points (one per line)", 
                                                                value=subsection_key_points_str,
                                                                height=100, 
                                                                key=f"subsection_key_points_{i}_{j}")
                                
                                # Process subsection key points into a list
                                subsection_key_points_list = [point.strip() for point in subsection_key_points.split('\n') if point.strip()]
                                
                                # Delete subsection button
                                if st.button(f"Delete Subsection {j+1}", key=f"delete_subsection_{i}_{j}", on_click=delete_subsection, args=(i, j)):
                                    pass  # The on_click callback handles the deletion
                                
                                # Create updated subsection
                                updated_subsection = {
                                    'title': subsection_title,
                                    'key_points': subsection_key_points_list
                                }
                                updated_subsections.append(updated_subsection)
                        
                        # Add new subsection button
                        if st.button(f"+ Add Subsection", key=f"add_subsection_{i}", on_click=add_subsection, args=(i,)):
                            pass  # The on_click callback handles the addition
                        
                        # Update section with changes
                        section['title'] = section_title
                        section['key_points'] = key_points_list
                        section['subsections'] = updated_subsections
                
                # Add new section button
                if st.button("+ Add Section", key="add_section_button", on_click=add_section):
                    pass  # The on_click callback handles the addition
                
                # Update the sections list for the final JSON
                updated_sections = sections
            
            with tab2:
                # Raw JSON editor
                st.markdown("### Edit the raw JSON below")
                json_str = json.dumps(outline_data, indent=2)
                edited_json = st.text_area("JSON Outline", value=json_str, height=400, key="json_outline")
                
                # Validate JSON button
                if st.button("Validate JSON"):
                    try:
                        json.loads(edited_json)
                        st.success("JSON is valid!")
                    except json.JSONDecodeError as e:
                        st.error(f"Invalid JSON: {str(e)}")
            
            # Submit button for generating article from outline
            if st.button("Submit Outline"):
                try:
                    # Get the updated outline from the appropriate tab
                    if tab1._active:
                        # Use the structured editor data
                        final_outline = {'sections': updated_sections}
                    else:
                        # Use the raw JSON editor data
                        final_outline = json.loads(edited_json)
                    
                    # Store the processed outline
                    st.session_state['processed_outline'] = final_outline
                    
                    # Display a message and start article generation
                    execute_generate_article()  
                except Exception as e:
                    st.error(f"Error processing outline: {str(e)}")
        except Exception as e:
            st.error(f"Error parsing outline JSON: {str(e)}")
            # Fallback to markdown editor
            if 'markdown_outline' in st.session_state:
                edited_outline = st.text_area("Outline", value=st.session_state['markdown_outline'], 
                                            height=400, key="edited_outline")
                
                if st.button("Submit Outline"):
                    if edited_outline:
                        # Convert markdown back to outline structure
                        outline_structure = markdown_to_outline(edited_outline)
                        st.session_state['processed_outline'] = outline_structure
                        st.success("Outline submitted successfully!")
                    else:
                        st.error("Please provide an outline before submitting.")

    
def configuration_content():
    st.subheader("Configuration")

    # Input fields for API key and model name
    tavily_api_key_input = st.text_input("Tavily API Key", value=st.session_state['tavily_api_key'], type="password")
    openai_api_key_input = st.text_input("OpenAI API Key", value=st.session_state['openai_api_key'], type="password")
    model_options = ["gpt-4o", "gpt-4o-mini", "o3-mini", "gpt-3.5-turbo"]
    model_name_input = st.selectbox("OpenAI Model Name", options=model_options, index=model_options.index(st.session_state['gpt_model']) if st.session_state['gpt_model'] in model_options else 0)
    def save_configuration():
        # Update session state with the new configuration values
        st.session_state['tavily_api_key'] = tavily_api_key_input
        st.session_state['openai_api_key'] = openai_api_key_input
        st.session_state['gpt_model'] = model_name_input

        update_env_variable("TAVILY_API_KEY", tavily_api_key_input)
        update_env_variable("OPENAI_API_KEY", openai_api_key_input)
        update_env_variable("GPT_MODEL", model_name_input)
        st.success("Configuration saved successfully!")

    # Save configuration button with the callback function
    st.button("Save Configuration", on_click=save_configuration)


# Tab structure
tab1, tab2 = st.tabs(["Blog Writer", "Configuration"])

with tab1:
    write_blog()
with tab2:
    configuration_content()

    
