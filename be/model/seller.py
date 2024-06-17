import json
import sqlite3 as sqlite
from be.model import error
from be.model import db_conn


class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_json_str: str,
        stock_level: int,
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            book_info = json.loads(book_json_str)
            # print(book_info)
            book_title = book_info["title"]
            book_tags = str(book_info["tags"])
            book_content = book_info["content"]
            book_book_intro = book_info["book_intro"]
            
            # # sqlite数据库
            # self.conn.execute(
            #     "INSERT into store(store_id, book_id, book_info, stock_level)"
            #     "VALUES (?, ?, ?, ?)",
            #     (store_id, book_id, book_json_str, stock_level),
            # )
            # mysql数据库
            cursor = self.conn.cursor()
            # book_json_str=book_json_str.replace("\\", "\\\\")
            # book_json_str=book_json_str.replace("\'", "\\\'")
            # cursor.execute(
            #     f"""INSERT into store(store_id, book_id, book_info, stock_level) VALUES ('{store_id}', '{book_id}', '{book_json_str}', {stock_level});""" # 使用f-string需要注意str类型数据处理问题
            # )
            # cursor.execute(
            #     f"""INSERT into store(store_id, book_id, book_info, stock_level) VALUES (%s, %s, %s, %s);""", (store_id, book_id, book_json_str, stock_level)
            # )
            # 增加了book_title，book_tags, book_content, book_book_intro
            cursor.execute(
                f"""INSERT into store(store_id, book_id, book_info, stock_level, book_title, book_tags, book_content, book_book_intro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""", (store_id, book_id, book_json_str, stock_level, book_title, book_tags, book_content, book_book_intro)
            )
            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(
        self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            # # sqlite数据库
            # self.conn.execute(
            #     "UPDATE store SET stock_level = stock_level + ? "
            #     "WHERE store_id = ? AND book_id = ?",
            #     (add_stock_level, store_id, book_id),
            # )
            # mysql数据库
            cursor = self.conn.cursor()
            cursor.execute(
                f"""UPDATE store SET stock_level = stock_level + {add_stock_level} WHERE store_id = '{store_id}' AND book_id = '{book_id}';"""
            )
            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            # # sqlite数据库
            # self.conn.execute(
            #     "INSERT into user_store(store_id, user_id)" "VALUES (?, ?)",
            #     (store_id, user_id),
            # )
            # mysql数据库
            cursor = self.conn.cursor()
            cursor.execute(
                f"""INSERT into user_store(store_id, user_id) VALUES ('{store_id}', '{user_id}');"""
            )
            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
    
    def deliver(
        self, user_id: str, order_id: str
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            
            # 找到order_id对应的store_id
            # mysql数据库
            cursor = self.conn.cursor()
            cursor.execute(
                f"""SELECT store_id FROM new_order WHERE order_id = '{order_id}';"""
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)
            store_id = row[0]
            
            # 检查store_id是否属于user_id
            # mysql数据库
            cursor = self.conn.cursor()
            cursor.execute(
                f"""SELECT store_id FROM user_store WHERE store_id = '{store_id}' AND user_id = '{user_id}';"""
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()
            
            # 把new_order表中的is_deliver字段置为1
            # mysql数据库
            cursor = self.conn.cursor()
            cursor.execute(
                f"""UPDATE new_order SET is_deliver = 1 WHERE order_id = '{order_id}';"""
            )
            
            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
