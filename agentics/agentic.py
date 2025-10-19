
import os
import re
from datetime import datetime

# --- Third-party ---
import pandas as pd
from dotenv import load_dotenv
from agents import Agent, Runner
from .agents_client import model_client_name_dict
from mcp_server.mcp_server import Agentic_MCP_Server
from .out_puts import PythonCodeResult, ReflectImprovedPythonCodeResult
from .instructions import build_chart_code, email_instructions, reflect_on_chart_and_improve

load_dotenv(override=True)

class DataProcessingAgentic:
    
    def __init__(self, name: str, model_name: str="llama3.2", dataset_path:str="coffee_sales.csv"):
        self.name = name
        self.df = None
        self.dataset_path=dataset_path
        self.model_name = model_name
        self.agentic_mcp_server = None
        
    async def connect_to_servers(self):
        self.agentic_mcp_server = Agentic_MCP_Server()
        await self.agentic_mcp_server.connect_to_servers()
        return self.agentic_mcp_server
        
    async def generate_chart_python_agent(self, generate_chart_instructions:str, 
                                          tools_details: list=[], 
                                          model_name: str = None,
                                          out_path_name: str =None, 
                                          output_type=None) -> Agent:
        
        if self.agentic_mcp_server is None:
            self.agentic_mcp_server = await self.connect_to_servers()
        
        instructions_ = build_chart_code(instruction=generate_chart_instructions, out_path_name=out_path_name)

        return Agent(
            name = self.name,
            # tools = tools_details,
            instructions = instructions_,
            model = self.get_model(self.model_name) if model_name is None else self.get_model(model_name),
            output_type=output_type,
            )
    
    async def reflect_improve_chart_python_agent(self,
                                              out_path_name: str,
                                              python_code_v1: str, 
                                              tools_details: list=None, 
                                              model_name: str = None, 
                                              output_type=None) -> Agent:
        if self.agentic_mcp_server is None:
            self.agentic_mcp_server = await self.connect_to_servers()
        
        instructions_ = reflect_on_chart_and_improve( out_path_name=out_path_name, python_code_v1=python_code_v1)
            
        return Agent(
            name = self.name,
            instructions = instructions_,
            tools = tools_details,
            model = self.get_model(self.model_name) if model_name is None else self.get_model(model_name),
            output_type=output_type,)
        
        
    async def send_email_agent(self, report, 
                               to_emails:list=["c.v.padeiro@gmail.com","cpadeiro2012@gmail.com"], 
                               sender_email:str="cpadeiro2012@gmail.com", 
                               model_name:str="llama3.2", 
                               output_type=None) -> Agent:
        
        instructions_= email_instructions( to_emails, sender_email, report=report, email_tool="email_sender")

        return Agent(
            name = self.name,
            instructions = instructions_,
            model = self.get_model(model_name),
            tools = self.agentic_mcp_server.call_tool(tool_name="email_sender", tool_args={"body":None, "subject":None,"to_emails":to_emails,}),
            output_type=output_type,)
    
    async def run(self, query:str="Create a plot comparing Q1 coffee sales in 2024 and 2025 using the data in coffee_sales.csv."):
        
        try:
            self.load_and_prepare_data()
            print(self.df.head())
            
            dt = datetime.now()
            name = f"generate_chart_{dt.strftime("%Y_%m_%d")}{dt.hour}{dt.minute}{dt.second}"
            # out_path_name=os.path.join(os.getcwd(),"out_puts",f"{name}.png")
            out_path_name=os.path.join("out_puts",f"{name}.png")
            
            if self.agentic_mcp_server is None:
                self.agentic_mcp_server = await self.connect_to_servers()
                     
            ## STEP: 1
            generate_chart_python_agent = await self.generate_chart_python_agent(generate_chart_instructions = query, 
                                                                    # tools_details = self.agentic_mcp_server.available_tools(),
                                                                    out_path_name = out_path_name,
                                                                    model_name = self.get_model("qwen3-coder"), # ollama3  gemma12B_v qwen3 gemini deepseek qwen3-coder
                                                                    output_type = PythonCodeResult,
                                                                    )
            
            content_ = """ You are a data visualization expert.
                            Return your answer *strictly* in this format:
                            {"python_code": "<execute_python> # valid python code here </execute_python>"}
                        """
            
            messages = [{"role": "user", "content": content_}]
            generate_chart_python_result = await Runner.run(generate_chart_python_agent, messages)
            await self.agentic_mcp_server.cleanup()
            
            # ## STEP: 2
            content_ = """ You are a data visualization expert.
                            Your task: critique the attached chart and the original code against the given instruction,
                            then return improved matplotlib code
                        """
            python_code_v1 = generate_chart_python_result.final_output.python_code.strip()
            print(f" ============= 1.0 Python_code_v1: {python_code_v1} =============")
            self.extract_exc_python_code(python_code_v1)
            
            dt = datetime.now()
            name = f"reflect_chart_{dt.strftime("%Y_%m_%d")}{dt.hour}{dt.minute}{dt.second}"
            # out_path_name=os.path.join(os.getcwd(),"out_puts",f"{name}.png")
            out_path_name=os.path.join("out_puts",f"{name}.png")
            
            reflect_python_code_agent = await self.reflect_improve_chart_python_agent( 
                                                                    out_path_name=out_path_name, 
                                                                    python_code_v1=python_code_v1,
                                                                    model_name=self.get_model("qwen3-coder"),
                                                                    output_type=ReflectImprovedPythonCodeResult,
                                                                    )
            
            messages = [{"role": "user", "content": content_}]
            reflect_python_code_agent_result = await Runner.run(reflect_python_code_agent, messages)
            await self.agentic_mcp_server.cleanup()
            
            ## STEP: 3
            content_ = """ You are expert in send emails to one or more recipients with custom subject and message content.
                           with a subject line and body content
                        """
            
            report = f"feedback: {reflect_python_code_agent_result.final_output.feedback["feedback"].strip()}  \n Python code: {reflect_python_code_agent_result.final_output.python_code["python_code"].strip()}"
            print(f" ============= {report} =============")
            self.extract_exc_python_code(reflect_python_code_agent_result.final_output.python_code["python_code"].strip())
            
            
            email_sender_agent = await self.send_email_agent(report = report, 
                                                             model_name = self.get_model("qwen3"),) ## ollama3.2 qwen3-coder qwen3
            
            messages = [{"role": "user", "content": content_}]
            await Runner.run(email_sender_agent, messages)
            await self.agentic_mcp_server.cleanup()
            
        except Exception as e:
            print(f"Error running {self.name}: {e}")
    
    def get_model(self, model_name: str) -> Agent:
        return model_client_name_dict.get(model_name, model_client_name_dict["ollama"])
    
    def load_and_prepare_data(self, csv_path: str=os.path.join(os.getcwd(),"dataset/coffee_sales.csv")) -> pd.DataFrame:
        """Load CSV and derive date parts commonly used in charts."""
        self.df = pd.read_csv(csv_path)
        
        # Be tolerant if 'date' exists
        if "date" in self.df.columns:
            self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")
            self.df["quarter"] = self.df["date"].dt.quarter
            self.df["month"] = self.df["date"].dt.month
            self.df["year"] = self.df["date"].dt.year
        return self.df

    def extract_exc_python_code(self, python_code_v1: str):
        code_v1 = re.search(r"<execute_python>([\s\S]*?)</execute_python>", python_code_v1)
        
        if self.df is None:
            self.load_and_prepare_data()
        
        if code_v1:
            initial_code = code_v1.group(1).strip()
            exec_globals = {"df": self.df}
            exec(initial_code, exec_globals)
        else:
            exec_globals = {"df": self.df}
            exec(python_code_v1, exec_globals)
    
