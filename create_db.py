import mysql.connector
from mysql.connector import errorcode

# Establish a connection to the MySQL server
try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root"
    )
    my_cursor = mydb.cursor()

    # Check if the database already exists
    my_cursor.execute("SHOW DATABASES")
    databases = [db[0] for db in my_cursor]

    if "ComFES" not in databases:
        my_cursor.execute("CREATE DATABASE ComFES")
        print("Database 'ComFES' created successfully.")
    else:
        print("Database 'ComFES' already exists.")
        
        # Optionally, display the existing databases
        print("Current databases:")
        for db in databases:
            print(f"- {db}")

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
finally:
    my_cursor.close()
    mydb.close()
