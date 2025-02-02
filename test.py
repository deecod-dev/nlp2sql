import duckdb

# Print DuckDB version
# print(duckdb.__version__)

# Connect to DuckDB (Persistent)
conn = duckdb.connect('db.duckdb')

# Path to CSV file
filepath = "media/uploads/customers-100.csv"

# Create Table from CSV
conn.execute(f"CREATE OR REPLACE TABLE customer_data AS SELECT * FROM read_csv_auto('{filepath}');")

# Query and Display the Table
result = conn.execute("SELECT * FROM customer_data").fetchall()
print(result)

# Close the connection
conn.close()