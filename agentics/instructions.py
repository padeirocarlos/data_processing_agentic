from dotenv import load_dotenv
from datetime import datetime
load_dotenv(override=True)

def image_generate(pathsogens:str, prompts:list[str], caption:str, path:str)->str:
    
    _prompt = ""
    
    for i, prompt in enumerate(prompts):
        _prompt += f"{i+1}. {prompt} \n"
        
    prompt_ = (f"""
    "You are a visual crop disease assistant. Based on the input trend insights in {pathsogens}, 
    generate two images using the following prompt and caption.
    
    prompt: 
    {_prompt}

    caption: 
    {caption}
    
    Respond in this format:
    {{"imageUrl1": "...", "imageUrl2": "..."}}
    
    You should call the following tool to save the images:
    - 'save_image' to save the images
    - {path} use this path to save the image 
    
    """)
    return prompt_


def reflect_on_chart_and_improve(
    out_path_name: str,
    python_code_v1: str,  
) -> tuple[str, str]:
    """
    Critique the chart IMAGE and the original code against the instruction, 
    then return refined matplotlib code.
    Returns (feedback, refined_code_with_tags).
    """
    prompt = f"""
    You are a data visualization expert.
    Your task: critique the attached chart and the original code against the given instruction,
    then return improved matplotlib code.

    Original code (for context):
    {python_code_v1}

    OUTPUT FORMAT (STRICT):
    1) First line: a valid JSON object with ONLY the "feedback" field.
    Example: {{"feedback": "The legend is unclear and the axis labels overlap."}}
            {{"python_code": "<execute_python> # valid python code here </execute_python>"}}

    2) Import all necessary libraries in the code. Don't assume any imports from the original code.

    HARD CONSTRAINTS:
    - Do NOT include Markdown, backticks, or any extra prose outside the two parts above.
    - Use pandas/matplotlib only (no seaborn).
    - Assume df already exists; do not read from files.
    - Save to '{out_path_name}' with dpi=300.
    - Always call plt.close() at the end (no plt.show()).
    - Include all necessary import statements.

    Schema (columns available in df):
    - date (M/D/YY)
    - time (HH:MM)
    - cash_type (card or cash)
    - card (string)
    - price (number)
    - coffee_name (string)
    - quarter (1-4)
    - month (1-12)
    - year (YYYY)
    """
    return prompt

   
def build_chart_code(instruction: str, out_path_name: str) -> str:
    """Build Python code to make a plot with matplotlib using tag-based wrapping."""

    prompt = f"""
    You are a data visualization expert.
    Return your answer *strictly* in this format:

    {{"python_code": "<execute_python> # valid python code here </execute_python>"}}

    Do not add explanations, only the tags and the code.

    The code should create a visualization from a DataFrame 'df' with these columns:
    - date (M/D/YY)
    - time (HH:MM)
    - cash_type (card or cash)
    - card (string)
    - price (number)
    - coffee_name (string)
    - quarter (1-4)
    - month (1-12)
    - year (YYYY)

    User instruction: {instruction}

    Requirements for the code:
    1. Assume the DataFrame is already loaded as 'df'.
    2. Use matplotlib for plotting.
    3. Add clear title, axis labels, and legend if needed.
    4. Save the figure as '{out_path_name}' with dpi=300.
    5. Do not call plt.show().
    6. Close all plots with plt.close().
    7. Add all necessary import python statements.
    
    Respond in this format:
    {{"python_code": "<execute_python> # valid python code her </execute_python>"}}"""
    
    return prompt

def email_instructions(to_emails:str=None, sender_email:str=None, report:str="", email_tool:str="email_sender"):
    
    if to_emails is None:
        to_emails=["c.v.padeiro@gmail.com", "cpadeiro2012@gmail.com"]
    if sender_email is None:
        from_emails=["cpadeiro2012@gmail.com"]

    EMAIL_INSTRUCTIONS = f"""You are able to send a nicely formatted HTML email including this detailed report: {report} \n. 
    
    Task:
        You should send one email using following emails from {from_emails} to {to_emails}, providing the report converted into clean, 
        well presented HTML with an appropriate subject line. Before send you must make sure to translate and send the email in portuguese of portugal.
    
    IMPORTANT:
        Make sure to use only tools '{email_tool}' provided in mcp_server to send the email"""
        
    return EMAIL_INSTRUCTIONS

