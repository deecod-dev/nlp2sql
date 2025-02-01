from django.shortcuts import render
from django.http import JsonResponse
import duckdb
import os

def home(request):
    return render(request, 'dataquery/home.html')

def process_file(request):
    if request.method == 'POST' and request.FILES['file']:
        # Save the uploaded CSV file
        uploaded_file = request.FILES['file']
        file_path = os.path.join('media', 'uploads', uploaded_file.name)
        
        # Save the file to the server
        with open(file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
        # Now process the file with DuckDB
        conn = duckdb.connect()
        conn.execute(f"CREATE TABLE customer_data AS SELECT * FROM '{file_path}';")
        
        # Optional: Get a sample query or data preview for the output
        results = conn.execute("SELECT * FROM customer_data LIMIT 5;").fetchall()

        # Return the results as JSON for dynamic page update
        return JsonResponse({'results': results})
    return JsonResponse({'error': 'No file uploaded'}, status=400)

from django.http import JsonResponse
from .utils import process_query
def query_view(request):
    if request.method == "POST":
        query = request.POST.get('query')  # Get the query from the request
        if query:
            result = process_query(query)  # Process the query using the utility function
            return JsonResponse({"result": result})
        return JsonResponse({"error": "No query provided"}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)