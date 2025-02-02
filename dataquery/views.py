# from django.shortcuts import render
# from django.http import JsonResponse
# import duckdb
# import os

# def home(request):
#     return render(request, 'dataquery/home.html')

# def process_file(request):
#     if request.method == 'POST' and request.FILES.get('file'):
#         uploaded_file = request.FILES['file']
#         upload_dir = os.path.join('media', 'uploads')
#         os.makedirs(upload_dir, exist_ok=True)  # Ensure the directory exists
#         file_path = os.path.join(upload_dir, uploaded_file.name)

#         # Save the file to the server
#         with open(file_path, 'wb') as f:
#             for chunk in uploaded_file.chunks():
#                 f.write(chunk)

#         # Return a success message
#         return JsonResponse({'message': 'File successfully uploaded', 'file_path': file_path})

#     return JsonResponse({'error': 'No file uploaded or invalid request method'}, status=400)


# from django.http import JsonResponse
# from .utils import process_query
# def query_view(request):
#     if request.method == "POST":
#         query = request.POST.get('query')  # Get the query from the request
#         if query:
#             result = process_query(query)  # Process the query using the utility function
#             return JsonResponse({"result": result})
#         return JsonResponse({"error": "No query provided"}, status=400)
#     return JsonResponse({"error": "Invalid request method"}, status=405)


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

        # # Save the file to the server
        with open(file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        conn = duckdb.connect('db.duckdb')
        conn.execute(f"CREATE OR REPLACE TABLE customer_data AS SELECT * FROM read_csv_auto('{file_path}');")
        conn.close()
        # Return a success message
        return JsonResponse({'message': 'File successfully uploaded', 'file_path': file_path})

    return JsonResponse({'error': 'No file uploaded or invalid request method'}, status=400)


from django.http import JsonResponse
from .utils import process_query
from django.http import FileResponse
from datetime import datetime
import pandas as pd

def query_view(request):
    if request.method == "POST":
        query = request.POST.get('query')
        if query:
            fpath = "media/uploads/customers-100.csv"
            result = process_query(query)  # Assuming this returns list of dicts

            # Save results to CSV
            save_dir = os.path.join('media', 'saves')
            os.makedirs(save_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"result_{timestamp}.csv"
            file_path = os.path.join(save_dir, filename)
            
            # Convert to DataFrame and save
            df = pd.DataFrame(result)
            df.to_csv(file_path, index=False)

            return JsonResponse({
                "result": result,
                "download_url": f"/download/?file={filename}"
            })
        return JsonResponse({"error": "No query provided"}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)

def download_result(request):
    filename = request.GET.get('file')
    if not filename:
        return JsonResponse({"error": "Filename missing"}, status=400)
    
    file_path = os.path.join('media', 'saves', filename)
    
    if not os.path.exists(file_path):
        return JsonResponse({"error": "File not found"}, status=404)
    
    # Security check to prevent directory traversal
    if not os.path.abspath(file_path).startswith(os.path.abspath('media/saves')):
        return JsonResponse({"error": "Access denied"}, status=403)
    
    return FileResponse(open(file_path, 'rb'), as_attachment=True)