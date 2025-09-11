import mysql.connector

mydb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = 'pdr0tz0x4tl0nxD$'
)
print(mydb)

mycursor = mydb.cursor()
mycursor.execute("DROP DATABASE mysql")