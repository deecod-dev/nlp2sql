import sys
print("sql ran")
sqlq=sys.argv[1].strip("`")
# print(sqlq)
sqlq=sqlq.replace("\n"," ")
# print(sqlq)
sqlq=sqlq.replace("sql", "").strip()
print(sqlq)
print("hmm")


import pandasql as psql
import pandas as pd

# Load the CSV file into a pandas DataFrame
csv_file = 'customers-100.csv'
df = pd.read_csv(csv_file)

# Example SQL query (you can modify this query based on your needs)
query = sqlq

# Run the query using pandasql
results = psql.sqldf(query, locals())

# Print results
print(results)
