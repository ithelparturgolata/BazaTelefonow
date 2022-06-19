import mysql.connector

connection = mysql.connector.connect(host="localhost", port="3306",
                                     database="bazasm", user="root", password="Savakiran03")
cursor = connection.cursor()
