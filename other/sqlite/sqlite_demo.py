import sqlite3

# Connection Object that represents our database. Can pass in a file or have an in-memory database with "_:memory:_"
# Creates a file or connects to it if it already exists
conn = sqlite3.connect('.\sqlite\employee.db')

# Cursor that allows us to execute SQL commands
c = conn.cursor()

# wrap string with doc string. Allows us to write a string that's multiple lines without any special breaks
# 5 data types: NULL, INTEGER, REAL, TEXT, BLOB
# c.execute("""CREATE TABLE employees(
#             first text,
#             last text,
#             pay integer
#             )""")

# c.execute("INSERT INTO employees VALUES ('Corey', 'Schafer', 50000)")

c.execute("SELECT * FROM employees WHERE last='Schafer'")

# c.fetchone() # Get next row in our result and only return that row, or None
# c.fetchmany() # shows the param # of rows as a list, or an empty list
# c.fetchall() # get the remaining rows
 
conn.commit() # commits the current transaction
conn.close() # close the connection. good practice