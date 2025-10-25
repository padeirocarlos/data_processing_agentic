import os
import uuid

import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

load_dotenv(override=True)

# Create FastMCP server
mcp = FastMCP(name="Email_Management_Server")

@mcp.resource("config://app-version")
def get_app_version() -> dict:
    """Static resource providing application version information"""
    return {
        "name": "Email Management Server",
        "version": "1.0.0",
        "release_date": "2025-10-15",
        "environment": "production"
    }

@mcp.tool()
def email_sender(body: str=None, subject: str=None, to_emails:list=None):
    """ Send out an email with the given body to all sales prospects via Gmail SMTP """
    
    # Set up email sender, recipient, and content
    from_email = os.getenv("GMAIL_USER")  # Replace with your Gmail address or set as env var
    to_email = os.getenv("GMAIL_TO")     # Replace with recipient or set as env var
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")  # Use your Gmail app password or set as env var
    
    # Create the email
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = from_email
    to_email = None
    
    if to_emails is None:
        to_emails = [from_email, to_email]
    
    if subject is None:
        msg['Subject'] = "Sales email list test 1"
    
    for index, email in enumerate(to_emails):
        if index !=0:
            to_email += "," + email
        else:
            to_email = email
            
    if to_email is not None:
        msg['To'] = to_email
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            if to_email:
                server.starttls()  # Secure the connection
                server.login(from_email, gmail_app_password)
                server.send_message(msg)
            
        return {"status": "success"}
    except Exception as e:
        return {"status": "failure", "message": str(e)}

if __name__ == "__main__":
    mcp.run(transport='stdio')