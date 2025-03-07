import os
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
GOOGLE_API_KEY = "AIzaSyBiTuybfxMQD7Y8MHvJQ3fTW8rSYwbk_q8"
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

def generate_sql_query(prompt, table_info):
    system_prompt = f"""You are an AI assistant that generates SQL queries based on natural language prompts.
    The available table(s) and their structure(s) are:
    {table_info}
    
    Generate only the SQL query without any explanations or formatting. Do not include backticks, 'sql' keyword, or any other markdown. Ensure the query is valid SQLite syntax."""

    response = model.generate_content([system_prompt, prompt])
    return response.text.strip()

st.set_page_config(page_title="Query Ease")

