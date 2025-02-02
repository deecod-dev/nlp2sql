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
import psycopg2
import csv

def home(request):
    return render(request, 'dataquery/home.html')

DATABASE_URL = "postgresql://neondb_owner:npg_VMpDEhwj40aU@ep-frosty-mouse-a1r1wmnz-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
def process_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        upload_dir = os.path.join('media', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)  
        file_path = os.path.join(upload_dir, uploaded_file.name)

        with open(file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)  

            # **Use original column names from CSV**
            column_names = [f'"{col.strip()}"' for col in header]  # Preserve case & handle spaces
            
            create_table_sql = f"CREATE TABLE IF NOT EXISTS data ({', '.join([f'{col} TEXT' for col in column_names])})"
            cursor.execute(create_table_sql)

            # **Insert using original column names**
            insert_sql = f"INSERT INTO data ({', '.join(column_names)}) VALUES ({', '.join(['%s' for _ in column_names])})"

            for row in csv_reader:
                if len(row) == len(header):  
                    cursor.execute(insert_sql, row)

        conn.commit()
        cursor.close()
        conn.close()

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



import signal
import psycopg2
import atexit
from django.db import connection

# DATABASE_URL = "postgresql://neondb_owner:npg_VMpDEhwj40aU@ep-frosty-mouse-a1r1wmnz-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

def drop_database():
    """Drops the database when the server stops."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS data;")  # Drop table instead of database if needed
        cursor.close()
        conn.close()
        print("Database dropped successfully!")
    except Exception as e:
        print(f"Error dropping database: {e}")

# **Handle Ctrl+C and Server Shutdown**
# signal.signal(signal.SIGINT, lambda signum, frame: drop_database())   # Ctrl+C
signal.signal(signal.SIGTERM, lambda signum, frame: drop_database())  # Server stop
atexit.register(drop_database)  # Ensures cleanup at exit

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt  # Exempt CSRF for this API
def drop_table_view(request):
    """Drops the database table when a user leaves the site."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS data;")
        cursor.close()
        conn.close()
        print("Database table dropped successfully!")
        return JsonResponse({"message": "Database table dropped!"})
    except Exception as e:
        return JsonResponse({"error": f"Error dropping database: {e}"}, status=500)
