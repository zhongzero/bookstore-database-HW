import logging
import os
import sqlite3 as sqlite
import pymysql
import threading


class Store:
    # database: str
    
    # # sqlite数据库
    # def __init__(self, db_path):
    #     self.database = os.path.join(db_path, "be.db")
    #     self.init_tables()
        
    # mysql数据库
    def __init__(self, db_path):
        self.init_tables_mysql()
    
    # # sqlite数据库
    # def init_tables(self):
    #     try:
    #         conn = self.get_db_conn()
    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS user ("
    #             "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
    #             "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
    #         )

    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS user_store("
    #             "user_id TEXT, store_id, PRIMARY KEY(user_id, store_id));"
    #         )

    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS store( "
    #             "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
    #             " PRIMARY KEY(store_id, book_id))"
    #         )

    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS new_order( "
    #             "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
    #         )

    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS new_order_detail( "
    #             "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
    #             "PRIMARY KEY(order_id, book_id))"
    #         )

    #         conn.commit()
    #     except sqlite.Error as e:
    #         logging.error(e)
    #         conn.rollback()
    
    # mysql数据库
    def init_tables_mysql(self):
        try:
            conn = self.get_db_conn_mysql()
            # 使用cursor()方法获取操作游标 
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS user")
            cursor.execute("""CREATE TABLE IF NOT EXISTS user (
                user_id VARCHAR(300) PRIMARY KEY, password TEXT NOT NULL,
                balance INTEGER NOT NULL, token TEXT, terminal TEXT);""")
            
            cursor.execute("DROP TABLE IF EXISTS user_store")
            cursor.execute("""CREATE TABLE IF NOT EXISTS user_store(
                user_id VARCHAR(300), store_id VARCHAR(300), PRIMARY KEY(user_id, store_id));""")
            
            # 为查找操作添加book_title，book_tags, book_content, book_book_intro
            cursor.execute("DROP TABLE IF EXISTS store")
            # cursor.execute("""CREATE TABLE IF NOT EXISTS store(
            #     store_id VARCHAR(300), book_id VARCHAR(300), book_info MediumText, stock_level INTEGER,
            #     PRIMARY KEY(store_id, book_id));""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS store(
                store_id VARCHAR(300), book_id VARCHAR(300), book_info MediumText, stock_level INTEGER, book_title MediumText, book_tags MediumText, book_content MediumText, book_book_intro MediumText,
                PRIMARY KEY(store_id, book_id));""")
            
            cursor.execute("DROP TABLE IF EXISTS new_order")
            # cursor.execute("""CREATE TABLE IF NOT EXISTS new_order(
            #     order_id VARCHAR(300) PRIMARY KEY, user_id VARCHAR(300), store_id VARCHAR(300));""")
            # 添加发货收货状态
            cursor.execute("""CREATE TABLE IF NOT EXISTS new_order(
                order_id VARCHAR(300) PRIMARY KEY, user_id VARCHAR(300), store_id VARCHAR(300), is_deliver INTEGER, is_receive INTEGER);""")
            
            cursor.execute("DROP TABLE IF EXISTS new_order_detail")
            cursor.execute("""CREATE TABLE IF NOT EXISTS new_order_detail(
                order_id VARCHAR(300), book_id VARCHAR(300), count INTEGER, price INTEGER,
                PRIMARY KEY(order_id, book_id));""")

            conn.commit()
        except pymysql.Error as e:
            logging.error(e)
            conn.rollback()
    

    # # sqlite数据库
    # def get_db_conn(self) -> sqlite.Connection:
    #     return sqlite.connect(self.database)
    
    # mysql数据库 
    def get_db_conn_mysql(self) -> sqlite.Connection:
        return pymysql.connect(host='localhost',user='root',passwd='123456',database='bookstore')


database_instance: Store = None
# global variable for database sync
init_completed_event = threading.Event()


def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)


def get_db_conn():
    global database_instance
    # return database_instance.get_db_conn()
    return database_instance.get_db_conn_mysql()
