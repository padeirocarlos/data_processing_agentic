import os
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


def code_bug_fixer(out_path_name: str, buggy_code: str, error_message:str, traceback:str=None):
    
    prompt = f"""You are a Python debugging expert. Fix the code error.

    BUGGY CODE:
    {buggy_code}

    ERROR:
    {error_message}

    {f"FULL TRACEBACK:\\n{traceback}" if traceback else ""}

    OUTPUT FORMAT (strict):
    Line 1: {{"diagnosis": "root cause and fix applied"}}
    Line 2: {{"python_code": "<execute_python>\\n# fixed code\\n</execute_python>"}}

    CONSTRAINTS:
    - Include all imports
    - pandas/matplotlib only
    - df exists (columns: date, time, cash_type, card, price, coffee_name, quarter, month, year)
    - Save to '{out_path_name}', dpi=300
    - End with plt.close()
    - No extra text outside JSON objects

    Preserve the original visualization intent while fixing the bug.
    """
    return prompt

def reflect_on_chart_and_improve(
    out_path_name: str,
    python_code_v1: str,  
) -> tuple[str, str]:

    prompt = f"""You are a data visualization expert. Critique the attached chart and original code 
                against the instruction, then provide improved matplotlib code.

    ORIGINAL CODE (for reference):
    {python_code_v1}

    OUTPUT FORMAT (strict - no deviations):
    Line 1: {{"feedback": "your critique here"}}
    Line 2: {{"python_code": "<execute_python>\\n# your code here\\n</execute_python>"}}

    REQUIREMENTS:
    - Include ALL necessary imports (pandas, matplotlib, etc.)
    - Use pandas/matplotlib only (no seaborn)
    - Assume df exists (do NOT read files)
    - Save to '{out_path_name}' with dpi=300
    - End with plt.close() (never plt.show())
    - No markdown, backticks, or extra text outside the two JSON objects

    AVAILABLE COLUMNS:
    - date (M/D/YY), time (HH:MM)
    - cash_type (card/cash), card (string)
    - price (float), coffee_name (string)
    - quarter (1-4), month (1-12), year (YYYY)
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

def email_instructions(to_emails:str=f"[{os.getenv("GMAIL_TO"), os.getenv("GMAIL_USER")}]", from_emails:str=os.getenv("GMAIL_USER"), report:str="", email_tool:str="email_sender"):
    
    EMAIL_INSTRUCTIONS = f"""You are able to send a nicely formatted HTML email including this detailed report: {report} \n. 
    
    Task:
        You should send one email using following emails from {from_emails} to {to_emails}, providing the report converted into clean, 
        well presented HTML with an appropriate subject line. Before send you must make sure to translate and send the email in portuguese of portugal.
    
    IMPORTANT:
        Make sure to use only tools '{email_tool}' provided in mcp_server to send the email"""
        
    return EMAIL_INSTRUCTIONS

