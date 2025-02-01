from django.shortcuts import render
from django.http import JsonResponse
import duckdb
import os

def home(request):
    return render(request, 'dataquery/home.html')

def process_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        upload_dir = os.path.join('media', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)  # Ensure the directory exists
        file_path = os.path.join(upload_dir, uploaded_file.name)

        # Save the file to the server
        with open(file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        # Return a success message
        return JsonResponse({'message': 'File successfully uploaded', 'file_path': file_path})

    return JsonResponse({'error': 'No file uploaded or invalid request method'}, status=400)


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