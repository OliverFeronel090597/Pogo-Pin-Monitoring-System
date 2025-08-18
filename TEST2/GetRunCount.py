import cx_Oracle
import os

username = "be_rep"
password = "berep98"
dsn_alias = "TDIDBPROD"  # Must be in tnsnames.ora

output_file = "oracle_tables_list.txt"

conn = cx_Oracle.connect(username, password, dsn_alias)
cursor = conn.cursor()

# Get all tables the user can access
cursor.execute("""
SELECT owner, table_name
FROM all_tables
ORDER BY owner, table_name
""")

tables = cursor.fetchall()

with open(output_file, "w", encoding="utf-8") as f:
    for owner, table_name in tables:
        f.write(f"{owner}.{table_name}\n")

cursor.close()
conn.close()

print(f"✅ Saved {len(tables)} table names to {output_file}")
