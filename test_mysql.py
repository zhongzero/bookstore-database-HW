import pymysql
import logging

# 打开数据库连接
conn = pymysql.connect(host='localhost',user='root',passwd='123456',database='test')

# 使用cursor()方法获取操作游标 
cursor = conn.cursor()

# # 如果数据表已经存在使用 execute() 方法删除表。
# cursor.execute("DROP TABLE IF EXISTS EMPLOYEE")
# # 创建数据表SQL语句
# sql = """CREATE TABLE EMPLOYEE (
#          FIRST_NAME  CHAR(20) NOT NULL,
#          LAST_NAME  CHAR(20),
#          AGE INT,  
#          SEX CHAR(1),
#          INCOME FLOAT );"""
# cursor.execute(sql)


# 如果数据表已经存在使用 execute() 方法删除表。
# cursor.execute("DROP TABLE IF EXISTS user")
# cursor.execute("CREATE TABLE IF NOT EXISTS user_store("
#                 "user_id TEXT, store_id, PRIMARY KEY(user_id, store_id));")
# pymysql.err.ProgrammingError: (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ', PRIMARY KEY(user_id, store_id))' at line 1")
# cursor.execute("CREATE TABLE IF NOT EXISTS user_store("
#                 "user_id TEXT(100), store_id TEXT, PRIMARY KEY(user_id, store_id));")
# try :
#     cursor.execute("""CREATE TABLE IF NOT EXISTS store(
#                     store_id VARCHAR(100), book_id VARCHAR(100), book_info TEXT, stock_level INTEGER,
#                     PRIMARY KEY(store_id, book_id));sss""")
#     conn.commit()
# except pymysql.Error as e:
#     logging.error(e)
#     conn.rollback()



# # SQL 插入语句
# try:
#     sql = """INSERT INTO EMPLOYEE(FIRST_NAME, LAST_NAME, AGE, SEX, INCOME)
#             VALUES ('Mac', 'Mohan', 20, 'M', 2000);"""
#     # 执行sql语句
#     cursor.execute(sql)
#     # 提交到数据库执行
#     conn.commit()
# except:
#     # Rollback in case there is any error
#     conn.rollback()


# try:
#     sql = "SELECT * FROM EMPLOYEE;" 
#     # 执行SQL语句
#     cursor.execute(sql)
#     # 获取所有记录列表
#     results = cursor.fetchall()
#     for row in results:
#         fname = row[0]
#         lname = row[1]
#         age = row[2]
#         sex = row[3]
#         income = row[4]
#         # 打印结果
#         print(f"fname={fname},lname={lname},age={age},sex={sex},income={income}")
# except:
#     print("Error: unable to fetch data")

# 查询指定数据库占用空间大小
sql="use information_schema;"
cursor.execute(sql)
sql="select concat(round(sum(data_length/1024/1024),2),'MB') as data from tables where table_schema='test';"
cursor.execute(sql)
results = cursor.fetchone()
print(f"database 'test' memory size:{results[0]}")


# 关闭数据库连接
conn.close()