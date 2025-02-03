import duckdb
import os
import google.generativeai as genai
from dotenv import load_dotenv
import pandas as pd
import sys
import pandasql as psql
import pandas as pd



def process_query(query, db_path="media/uploads/customers-100.csv"):
    # query=query+"processedddd bkl"
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

    datapath=db_path
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


    # text=input("Enter your natural language query:\n")
    text=query

    sqlq = nl_to_sql(text)
    print(sqlq)
    

    # import subprocess
    # subprocess.run(['python', 'run_sql.py', sqlq])

    sqlq=sqlq.strip("`")
    sqlq=sqlq.replace("\n"," ")
    sqlq=sqlq.replace("sql", "").strip()
    print(sqlq)

    # Load the CSV file into a pandas DataFrame
    csv_file = db_path
    df = pd.read_csv(csv_file)

    # Example SQL query (you can modify this query based on your needs)
    query = sqlq

    # Run the query using pandasql
    results = psql.sqldf(query, locals())

    # Print results
    # print("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL",results)
    results_list = results.to_dict(orient='records')  # Each row is represented as a dictionary
    return results_list


# import duckdb
# import os
# import google.generativeai as genai
# from dotenv import load_dotenv
# import pandas as pd
# import sys
# import pandasql as psql
# import pandas as pd

# # rules="In DuckDB SQL, identifiers with spaces or special characters (like !@#$%^&*) must be enclosed in double quotes. Reserved keywords and case-sensitive identifiers should also be quoted. Column names starting with numbers can be quoted for clarity. String literals must be enclosed in single quotes, with any internal single quotes escaped by doubling them. For dates, use DATE 'YYYY-MM-DD' and for timestamps, TIMESTAMP 'YYYY-MM-DD HH:MM:SS'. DuckDB supports type casting using the :: operator (preferred) or CAST(expr AS TYPE). Special operators include || for string concatenation, -> and ->> for JSON/struct access, and # for map access. Nested data is accessed with dot notation for structs and 1-based indexing for arrays. DuckDB-specific features include direct file querying (FROM 'file.csv'), sampling (USING SAMPLE), and LIMIT BY for limiting results per group. Temporary tables use the TEMP or TEMPORARY keyword. Common pitfalls include failing to quote identifiers with spaces, misusing case-sensitive identifiers, and incorrect JSON access. Always ensure reserved keywords are quoted, and validate date formats, nested data access, and file paths."
# rules = """PostgreSQL SQL rules:
# - Identifiers with spaces/special characters must be double-quoted
# - String literals use single quotes, escape with ''
# - Use standard SQL date formats: DATE 'YYYY-MM-DD'
# - Use CAST(value AS type) for type conversions
# - String concatenation: ||
# - Use ILIKE for case-insensitive comparisons
# - Use LIMIT instead of TOP for row limiting
# - Use :: for type casting (alternative to CAST())
# - Use TRUE/FALSE for boolean values
# - Table name is always 'data'
# - Use standard PostgreSQL functions (e.g., LENGTH() instead of LEN())
# - For current date use CURRENT_DATE
# - Use IS NULL/IS NOT NULL for null checks
# """
# import psycopg2
# import re
# def process_query(query, db_path="media/uploads/customers-100.csv"):
#     # query=query+"processedddd bkl"
#     def load_data_prompt(data):
#         # Read the CSV file
#         df = pd.read_csv(data)

#         # Extract first two rows
#         first_two_rows = df.head(2)

#         # Dictionary to store column name as key and non-NA example as value
#         example_values = {}

#         for column in first_two_rows.columns:
#             # Get the first two non-null values in the column
#             non_null_values = first_two_rows[column].dropna()

#             if non_null_values.empty:
#                 # If all values are NaN in the first two rows, check the entire column
#                 non_null_values = df[column].dropna()

#             if not non_null_values.empty:
#                 # Take the first non-null value as an example
#                 example_values[column] = non_null_values.iloc[0]
#             else:
#                 # If all values are NaN, append None
#                 example_values[column] = None

#         return example_values

#     datapath=db_path
#     datainfo=load_data_prompt(datapath)
#     print(datainfo)


#     load_dotenv()
#     api_key = os.getenv("gemapikey")

#     if not api_key:
#         raise ValueError("GEMINI_API_KEY not found in .env file!")

#     genai.configure(api_key=api_key)
#     model = genai.GenerativeModel("gemini-pro")

#     def nl_to_sql(natural_query):
#         prompt = f"""Convert this natural language query to PostgreSQL SQL. Data structure (first 2 rows): {datainfo}
#         Rules: {rules}
#         \nReturn ONLY the SQL query without any explanations or formatting
#         \nQuery: {natural_query}
#         \n\nSQL:"""
        
#         try:
#             response = model.generate_content(prompt)
#             sql = response.text.strip().replace('```sql', '').replace('```', '')
#             return re.sub(r'\s+', ' ', sql)
#         except Exception as e:
#             return f"Error: {e}"

#     # text=input("Enter your natural language query:\n")
#     text=query

#     sqlq = nl_to_sql(text)
#     # print(sqlq)
    

#     # import subprocess
#     # subprocess.run(['python', 'run_sql.py', sqlq])

#     # sqlq=sqlq.strip("`")
#     # sqlq=sqlq.replace("\n"," ")
#     # sqlq=sqlq.replace("sql", "").strip()
#     print(sqlq)
#     conn = psycopg2.connect(os.getenv("DATABASE_URL"))
#     cursor = conn.cursor()
    
#     try:
#         cursor.execute(sqlq)
#         results = cursor.fetchall()
#         columns = [desc[0] for desc in cursor.description]
#         return [dict(zip(columns, row)) for row in results]
    
#     except Exception as e:
#         raise Exception(f"SQL Error: {str(e)}")
    
#     finally:
#         cursor.close()
#         conn.close()
#     # # Load the CSV file into a pandas DataFrame
#     # csv_file = db_path
#     # df = pd.read_csv(csv_file)

#     # # Example SQL query (you can modify this query based on your needs)
#     # query = sqlq

#     # # Run the query using pandasql
#     # # results = psql.sqldf(query, locals())
#     # print("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
#     # conn = duckdb.connect('db.duckdb')

#     # # Ensure the table exists before querying
#     # # conn.execute(f"CREATE OR REPLACE TABLE customer_data AS SELECT * FROM read_csv_auto('{db_path}');")

#     # # Now execute the query
#     # # result = conn.execute("SELECT * FROM customer_data").fetchall()
#     # query=query.replace("`","\"")
#     # import re
#     # query = re.sub(r'\s+', ' ', query)
#     # query=query.strip()
#     # # query="SELECT \"First Name\", \"Last Name\" FROM df"
#     # print(query)
#     # # result = conn.execute(query).fetchall()
#     # cursor = conn.execute(query)
#     # result = cursor.fetchall()
#     # column_names = [desc[0] for desc in cursor.description]
    
#     # # Convert to list of dictionaries
#     # result_dicts = [dict(zip(column_names, row)) for row in result]
    
#     # conn.close()
#     # print(result_dicts)
#     # return result_dicts

#     # # conn.close()
#     # # # Print results
#     # # # print("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL",results)
#     # # # results_list = results.to_dict(orient='records')  # Each row is represented as a dictionary
#     # # print(result)
#     # # return result