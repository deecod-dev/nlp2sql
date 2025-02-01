# dataquery/views.py
import os
import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
import google.generativeai as genai
from dotenv import load_dotenv

# # Load .env file
# load_dotenv()

# # API Key Setup
# api_key = os.getenv("gemapikey")

# if not api_key:
#     raise ValueError("GEMINI_API_KEY not found in .env file!")
api_key=settings.GEMINI_API_KEY

# Setup Google Generative AI API
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-pro")

def load_data_prompt(data):
    df = pd.read_csv(data)
    first_two_rows = df.head(2)
    example_values = {}

    for column in first_two_rows.columns:
        non_null_values = first_two_rows[column].dropna()

        if non_null_values.empty:
            non_null_values = df[column].dropna()

        if not non_null_values.empty:
            example_values[column] = non_null_values.iloc[0]
        else:
            example_values[column] = None

    return example_values

def nl_to_sql(natural_language_query, datapath):
    datainfo = load_data_prompt(datapath)
    prompt = f"""I have a {datapath.split(".")[-1]} database file and its structure(row names and values for the first two rows) are of the format:\n\n
    {str(datainfo)}
    \n\nConvert the following natural language query into SQL for the table name df in the format to be used by pandasql with the column names inside backticks(`):\n\nQuery: {natural_language_query}\nSQL:"""

    try:
        response = model.generate_content(prompt)
        sql_query = response.text.strip() if response.text else "Error: No response"
        if "FROM dfWHERE" in sql_query:
            sql_query = sql_query.replace("FROM dfWHERE", "FROM df WHERE")
        return sql_query

    except Exception as e:
        return f"Error: {e}"

def run_query(request):
    # Example input CSV file path (you can modify this as needed)
    datapath = 'customers-100.csv'
    
    # Get the natural language query from the user
    natural_language_query = request.GET.get('query', '')

    if not natural_language_query:
        return JsonResponse({"error": "Query is missing!"}, status=400)

    # Convert NL query to SQL query
    sql_query = nl_to_sql(natural_language_query, datapath)
    
    # Check for valid SQL
    if "Error" in sql_query:
        return JsonResponse({"error": sql_query}, status=400)
    
    # Load CSV and run SQL query using pandasql
    import pandasql as psql

    df = pd.read_csv(datapath)
    try:
        results = psql.sqldf(sql_query, locals())
        return JsonResponse({"results": results.to_dict(orient='records')})
    except Exception as e:
        return JsonResponse({"error": f"SQL execution failed: {e}"}, status=500)

from django.shortcuts import render
# def home(request):
#     return render(request, 'dataquery/home.html')
from django.shortcuts import render, redirect
from .models import UploadedFile
from .forms import UploadFileForm

def home(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Save the file to the database and `media/uploads/`
            return redirect('home')  # Redirect to clear form
    else:
        form = UploadFileForm()

    return render(request, 'dataquery/home.html', {'form': form})