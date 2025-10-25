import os
from pydantic import BaseModel, Field

class PythonCodeResult(BaseModel):
    python_code: str = Field(description="Generate Python code to make a plot with matplotlib using tag-based wrapping in <execute_python> # valid python code here </execute_python>")

class PythonCodeCheckedResult(BaseModel):
    diagnosis: str = Field(description="root cause and fix applied")
    python_code: str = Field(description="Generate Python code to make a plot with matplotlib using tag-based wrapping in <execute_python> # valid python code here </execute_python>")

class ReflectImprovedPythonCodeResult(BaseModel):
    feedback: str = Field(description="A valid JSON object with ONLY the 'feedback' field")
    python_code: str = Field(description="Generate Python code to make a plot with matplotlib using tag-based wrapping in <execute_python> # valid python code here </execute_python>")
    