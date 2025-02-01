import os
import google.generativeai as genai
from dotenv import load_dotenv
import pandas as pd

def load_data_prompt(data):
    # Read the CSV file
    df = pd.read_csv(data)

    # Extract first two rows
    first_two_rows = df.head(2)

    # Dictionary to store column name as key and non-NA example as value
    example_values = {}

    for column in first_two_rows.columns:
        # Get the first two non-null values in the column
        non_null_values = first_two_rows[column].dropna()

        if non_null_values.empty:
            # If all values are NaN in the first two rows, check the entire column
            non_null_values = df[column].dropna()

        if not non_null_values.empty:
            # Take the first non-null value as an example
            example_values[column] = non_null_values.iloc[0]
        else:
            # If all values are NaN, append None
            example_values[column] = None

    return example_values

datapath="customers-100.csv"
datainfo=load_data_prompt(datapath)
print(datainfo)


load_dotenv()
api_key = os.getenv("gemapikey")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file!")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-pro")

def nl_to_sql(natural_language_query):
    prompt = f"""I have a {datapath.split(".")[-1]} database file and it's structure(row names and values for the first two rows) are of the format:\n\n
    {str(datainfo)}
    \n\nConvert the following natural language query into SQL for the table name df in the format to be used by pandasql with the column names inside backticks(`):\n\nQuery: {natural_language_query}\nSQL:"""
    print(prompt)
    try:
        response = model.generate_content(prompt)
        sql_query = response.text.strip() if response.text else "Error: No response"
        return sql_query

    except Exception as e:
        return f"Error: {e}"


text=input("Enter your natural language query:\n")

sqlq = nl_to_sql(text)
print(sqlq)
 

import subprocess
subprocess.run(['python', 'run_sql.py', sqlq])