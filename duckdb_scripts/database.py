import duckdb
dbpath="media/uploads/customers-100.csv"
duckdb.read_csv(dbpath)
print(duckdb.sql(f"SELECT * FROM '{dbpath}'"))
