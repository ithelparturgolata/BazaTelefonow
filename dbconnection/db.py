import mysql.connector


connection = mysql.connector.connect(host="localhost", port="3306", database="bazasm", user="root", password="Savakiran03")
cursor = connection.cursor()
select_query = "select * from mieszkaniec"
cursor.execute(select_query)
records = cursor.fetchall()