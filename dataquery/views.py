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
        new_file_path = os.path.join(upload_dir, 'customers-100.csv')
        os.rename(file_path, new_file_path)

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
            result = process_query(query)  # Assuming this returns list of dicts

            save_dir = os.path.join('media', 'saves')
            os.makedirs(save_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"result_{timestamp}.csv"
            file_path = os.path.join(save_dir, filename)

            # Use pandas for efficient CSV writing
            pd.DataFrame(result).to_csv(file_path, index=False)

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
    if not os.path.abspath(file_path).startswith(os.path.abspath('media/saves')):
        return JsonResponse({"error": "Access denied"}, status=403)
    
    return FileResponse(open(file_path, 'rb'), as_attachment=True)


import signal
import psycopg2
import atexit
from django.db import connection

import shutil
import os
def empty_media_folder():
    media_dir = os.path.join('media')
    if os.path.exists(media_dir):
        # Recursively remove all files and folders inside 'media' folder
        shutil.rmtree(media_dir)
        # Recreate the 'media' folder after deletion
        os.makedirs(media_dir)
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt  # Exempt CSRF for this API
def drop_files(request):
    try:
        empty_media_folder()
        print("files dropped successfully!")
    except Exception as e:
        print(f"Error dropping files: {e}")


# **Handle Ctrl+C and Server Shutdown**
signal.signal(signal.SIGINT, lambda signum, frame: drop_files())   # Ctrl+C
signal.signal(signal.SIGTERM, lambda signum, frame: drop_files())  # Server stop
atexit.register(drop_files)  # Ensures cleanup at exit





# from django.shortcuts import render
# from django.http import JsonResponse
# import duckdb
# import os
# import psycopg2
# import csv

# def home(request):
#     return render(request, 'dataquery/home.html')

# DATABASE_URL = "postgresql://neondb_owner:npg_VMpDEhwj40aU@ep-frosty-mouse-a1r1wmnz-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
# def process_file(request):
#     if request.method == 'POST' and request.FILES.get('file'):
#         uploaded_file = request.FILES['file']
#         upload_dir = os.path.join('media', 'uploads')
#         os.makedirs(upload_dir, exist_ok=True)  
#         file_path = os.path.join(upload_dir, uploaded_file.name)

#         # Save the file locally first
#         with open(file_path, 'wb') as f:
#             for chunk in uploaded_file.chunks():
#                 f.write(chunk)

#         conn = psycopg2.connect(DATABASE_URL)
#         cursor = conn.cursor()
        
#         # Drop table before re-creating (to prevent conflicts)
#         cursor.execute("DROP TABLE IF EXISTS data;")  
        
#         with open(file_path, 'r', encoding='utf-8') as file:
#             csv_reader = csv.reader(file)
#             header = next(csv_reader)  

#             # Use original column names safely
#             column_names = [f'"{col.strip()}"' for col in header]

#             # Create table dynamically (use VARCHAR instead of TEXT)
#             create_table_sql = f"CREATE TABLE data ({', '.join([f'{col} VARCHAR' for col in column_names])})"
#             cursor.execute(create_table_sql)

#             # Fastest way: Use COPY FROM (bulk insert)
#             file.seek(0)  # Move file cursor to beginning
#             cursor.copy_expert(f"COPY data FROM STDIN WITH CSV HEADER", file)

#         conn.commit()
#         cursor.close()
#         conn.close()

#         return JsonResponse({'message': 'File successfully uploaded', 'file_path': file_path})

#     return JsonResponse({'error': 'No file uploaded or invalid request method'}, status=400)


# from django.http import JsonResponse
# from .utils import process_query
# from django.http import FileResponse
# from datetime import datetime
# import pandas as pd

# from django.shortcuts import render
# from django.http import JsonResponse, FileResponse
# import duckdb
# import os
# import psycopg2
# import csv
# from datetime import datetime
# import pandas as pd
# import atexit
# import signal

# def query_view(request):
#     if request.method == "POST":
#         query = request.POST.get('query')
#         if query:
#             result = process_query(query)  # Assuming this returns list of dicts

#             save_dir = os.path.join('media', 'saves')
#             os.makedirs(save_dir, exist_ok=True)
            
#             timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
#             filename = f"result_{timestamp}.csv"
#             file_path = os.path.join(save_dir, filename)

#             # Use pandas for efficient CSV writing
#             pd.DataFrame(result).to_csv(file_path, index=False)

#             return JsonResponse({
#                 "result": result,
#                 "download_url": f"/download/?file={filename}"
#             })
#         return JsonResponse({"error": "No query provided"}, status=400)
#     return JsonResponse({"error": "Invalid request method"}, status=405)


# def download_result(request):
#     filename = request.GET.get('file')
#     if not filename:
#         return JsonResponse({"error": "Filename missing"}, status=400)
    
#     file_path = os.path.join('media', 'saves', filename)
    
#     if not os.path.exists(file_path):
#         return JsonResponse({"error": "File not found"}, status=404)
#     if not os.path.abspath(file_path).startswith(os.path.abspath('media/saves')):
#         return JsonResponse({"error": "Access denied"}, status=403)
    
#     return FileResponse(open(file_path, 'rb'), as_attachment=True)



# import signal
# import psycopg2
# import atexit
# from django.db import connection

# # DATABASE_URL = "postgresql://neondb_owner:npg_VMpDEhwj40aU@ep-frosty-mouse-a1r1wmnz-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

# def drop_database():
#     try:
#         conn = psycopg2.connect(DATABASE_URL)
#         conn.autocommit = True
#         cursor = conn.cursor()
#         cursor.execute("DROP TABLE IF EXISTS data;")
#         cursor.close()
#         conn.close()
#         print("Database dropped successfully!")
#     except Exception as e:
#         print(f"Error dropping database: {e}")


# # **Handle Ctrl+C and Server Shutdown**
# # signal.signal(signal.SIGINT, lambda signum, frame: drop_database())   # Ctrl+C
# # signal.signal(signal.SIGTERM, lambda signum, frame: drop_database())  # Server stop
# atexit.register(drop_database)  # Ensures cleanup at exit

# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# @csrf_exempt  # Exempt CSRF for this API
# def drop_table_view(request):
#     """Drops the database table when a user leaves the site."""
#     try:
#         conn = psycopg2.connect(DATABASE_URL)
#         conn.autocommit = True
#         cursor = conn.cursor()
#         cursor.execute("DROP TABLE IF EXISTS data;")
#         cursor.close()
#         conn.close()
#         print("Database table dropped successfully!")
#         return JsonResponse({"message": "Database table dropped!"})
#     except Exception as e:
#         return JsonResponse({"error": f"Error dropping database: {e}"}, status=500)
