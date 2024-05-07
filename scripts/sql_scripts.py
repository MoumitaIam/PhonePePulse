import mysql.connector as sql

#CONNECT DATABASE
def connect_database():
    conn = sql.connect(
        host="localhost", user="root", password="root", db="phonepe_pulse"
    )
    cur = conn.cursor()
    return cur, conn

# SELECT STATEMENT
def execute_select(query, cur):
    cur.execute(query)
    return cur

def get_year_list(tablename,cursor):
    query = f'select distinct(year) from {tablename}' 
    data = execute_select(query,cursor)
    year_list = [row[0]for row in data.fetchall()]
    return year_list

def get_quarter_list(tablename,cursor,year):
    query = f'select distinct(quarter) from {tablename} where year = {year}' 
    data = execute_select(query,cursor)
    year_list = [f'Q{row[0]}'for row in data.fetchall()]
    return year_list