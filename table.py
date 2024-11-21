import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',            
    password='r00t@123**//', 
    database='spclg',      
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    c = conn.cursor()

    c.execute('''
        CREATE TABLE stud (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            phno VARCHAR(15) NOT NULL UNIQUE,
            pwd VARCHAR(255) NOT NULL
        );

    ''')
    conn.commit()
    print("Table 'users' created successfully!")
finally:
    conn.close()
