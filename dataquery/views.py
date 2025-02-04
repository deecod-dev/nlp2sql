from django.conf import settings
DATABASE_URL= settings.DATABASE_URL
from django.views.decorators.csrf import csrf_exempt

# This should be OUTSIDE the DBFLAG conditional blocks
@csrf_exempt
def update_settings_variable(request):
    if request.method == "POST":
        settings.DBFLAG = not settings.DBFLAG
        print("Database flag toggled:", settings.DBFLAG)
        db = "DuckDB" if settings.DBFLAG else "PostgreSQL"
        return JsonResponse({"message": f"Database changed to {db}"})
    return JsonResponse({"error": "Invalid request"}, status=405)


if(settings.DBFLAG):

    from django.shortcuts import render
    from django.http import JsonResponse
    import duckdb
    import os

    def home(request):
        # Clean uploads when home page is loaded/refreshed
        empty_media_folder()  
        return render(request, 'dataquery/home.html')

    from django.conf import settings
    from django.views.decorators.csrf import csrf_exempt
    # Global variable in settings.py (e.g., SETTINGS_FLAG)
    @csrf_exempt  # Disable CSRF for testing (remove this in production)
    def update_settings_variable(request):
        if request.method == "POST":
            settings.DBFLAG = not settings.DBFLAG  # Toggle the variable
            print("variiiiiiiiiiiiiiiiiiiiiiableee: ",settings.DBFLAG)
            db=""
            if(settings.DBFLAG):
                db="DuckDB"
            else:
                db="PostgreSQL"
            return JsonResponse({"message": f"Database changed to {db}"})
        
        return JsonResponse({"error": "Invalid request"}, status=405)

    def process_file(request):
        if request.method == 'POST' and request.FILES.get('file'):
            uploaded_file = request.FILES['file']
            upload_dir = os.path.join('media', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)  # Ensure the directory exists
            file_path = os.path.join(upload_dir, uploaded_file.name)

            # Save the uploaded file
            with open(file_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            new_file_path = os.path.join(upload_dir, 'upfile.csv')

            # ✅ Remove 'upfile.csv' if it already exists
            if os.path.exists(new_file_path):
                os.remove(new_file_path)  

            # Rename the newly uploaded file
            os.rename(file_path, new_file_path)

            # Update file_path to the new location
            file_path = new_file_path

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
                result = process_query(query)
                sql_query = result["result"]['sql_query']  # Get the SQL query from process_query
                result_data = result['result']["result"]
                # db=result["dbused"]

                # Ensure saves directory exists
                save_dir = os.path.join('media', 'saves')
                os.makedirs(save_dir, exist_ok=True)  # This creates the directory if it doesn't exist

                # Save to CSV (existing code)
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"result_{timestamp}.csv"
                file_path = os.path.join('media', 'saves', filename)
                pd.DataFrame(result_data).to_csv(file_path, index=False)

                return JsonResponse({
                    # "db":db,
                    "result": result_data,
                    "sql_query": sql_query,  # Add SQL query to response
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
        """Clean ONLY the uploads directory (preserve saved results)"""
        uploads_dir = os.path.join('media', 'uploads')
        saves_dir = os.path.join('media', 'saves')

        if os.path.exists(uploads_dir):
            for filename in os.listdir(uploads_dir):
                file_path = os.path.join(uploads_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
        # Create empty uploads directory if it doesn't exist
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Create saves directory if it doesn't exist (but don't clear it)
        os.makedirs(saves_dir, exist_ok=True)
    from django.views.decorators.csrf import csrf_exempt
    @csrf_exempt
    def drop_files(request):
        try:
            empty_media_folder()
            print("Files dropped successfully!")
            return JsonResponse({'status': 'success'})  # Add this line
        except Exception as e:
            print(f"Error dropping files: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)  # And this line

    # **Handle Ctrl+C and Server Shutdown**
    # signal.signal(signal.SIGINT, lambda signum, frame: drop_database())   # Ctrl+C
    # signal.signal(signal.SIGTERM, lambda signum, frame: drop_database())  # Server stop
    atexit.register(empty_media_folder)  # Now cleans only uploads by default
else:

    # import shutil
    # import os
    # import signal
    # import atexit
    # from django.http import JsonResponse
    # from django.views.decorators.csrf import csrf_exempt

    # def empty_media_folder():
    #     media_dir = os.path.join('media')
    #     if os.path.exists(media_dir):
    #         # Recursively remove all files and folders inside 'media' folder
    #         shutil.rmtree(media_dir)
    #         # Recreate the 'media' folder after deletion
    #         os.makedirs(media_dir)

    # # This function should be used for system signals and atexit
    # def cleanup_files():
    #     try:
    #         empty_media_folder()
    #         print("Files dropped successfully during cleanup!")
    #     except Exception as e:
    #         print(f"Error during cleanup: {e}")

    # @csrf_exempt
    # def drop_files(request):
    #     try:
    #         empty_media_folder()
    #         print("Files dropped successfully!")

    #         # If this is an HTTP request, return a response
    #         # if request is not None:
    #         return JsonResponse({"message": "Files dropped successfully!"})

    #     except Exception as e:
    #         print(f"Error dropping files: {e}")
    #         if request is not None:
    #             return JsonResponse({"error": f"Error dropping files: {e}"}, status=500)
    #     # If called by a signal, return an empty HttpResponse instead of None
    #     print("hhhhhhhhhhhhhhhhh")
    #     return JsonResponse({"message": "Cleanup executed!"})


    # # **Handle Ctrl+C and Server Shutdown**
    # signal.signal(signal.SIGINT, lambda signum, frame: drop_files())   # Ctrl+C
    # signal.signal(signal.SIGTERM, lambda signum, frame: drop_files())  # Server stop
    # atexit.register(drop_files)  # Ensures cleanup at exit






    from django.shortcuts import render
    from django.http import JsonResponse
    import duckdb
    import os
    import psycopg2
    import csv

    def home(request):
        return render(request, 'dataquery/home.html')

    def process_file(request):
        if request.method == 'POST' and request.FILES.get('file'):
            uploaded_file = request.FILES['file']
            upload_dir = os.path.join('media', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)  
            file_path = os.path.join(upload_dir, uploaded_file.name)

            # Save the uploaded file
            with open(file_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            new_file_path = os.path.join(upload_dir, 'upfile.csv')

            # ✅ Remove 'upfile.csv' if it already exists
            if os.path.exists(new_file_path):
                os.remove(new_file_path)  

            # Rename the newly uploaded file
            os.rename(file_path, new_file_path)

            # Update file_path to the new location
            file_path = new_file_path


            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            # Drop table before re-creating (to prevent conflicts)
            cursor.execute("DROP TABLE IF EXISTS data;")  
            
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                header = next(csv_reader)  

                # Use original column names safely
                column_names = [f'"{col.strip()}"' for col in header]

                # Create table dynamically (use VARCHAR instead of TEXT)
                create_table_sql = f"CREATE TABLE data ({', '.join([f'{col} VARCHAR' for col in column_names])})"
                cursor.execute(create_table_sql)

                # Fastest way: Use COPY FROM (bulk insert)
                file.seek(0)  # Move file cursor to beginning
                cursor.copy_expert(f"COPY data FROM STDIN WITH CSV HEADER", file)

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

    from django.shortcuts import render
    from django.http import JsonResponse, FileResponse
    import duckdb
    import os
    import psycopg2
    import csv
    from datetime import datetime
    import pandas as pd
    import atexit
    import signal

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


    def drop_database():
        try:
            conn = psycopg2.connect(DATABASE_URL)
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS data;")
            cursor.close()
            conn.close()
            print("Database dropped successfully!")
        except Exception as e:
            print(f"Error dropping database: {e}")


    # **Handle Ctrl+C and Server Shutdown**
    # signal.signal(signal.SIGINT, lambda signum, frame: drop_database())   # Ctrl+C
    # signal.signal(signal.SIGTERM, lambda signum, frame: drop_database())  # Server stop
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
