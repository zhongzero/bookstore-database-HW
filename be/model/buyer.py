import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                # # sqlite数据库
                # cursor = self.conn.execute(
                #     "SELECT book_id, stock_level, book_info FROM store "
                #     "WHERE store_id = ? AND book_id = ?;",
                #     (store_id, book_id),
                # )
                # mysql数据库
                cursor = self.conn.cursor()
                cursor.execute(
                    f"""SELECT book_id, stock_level, book_info FROM store WHERE store_id = '{store_id}' AND book_id = '{book_id}';"""
                )
                row = cursor.fetchone()
                if row is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = row[1]
                book_info = row[2]
                book_info_json = json.loads(book_info)
                book_info_json = json.loads(book_info, strict=False)
                price = book_info_json.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                # # sqlite数据库
                # cursor = self.conn.execute(
                #     "UPDATE store set stock_level = stock_level - ? "
                #     "WHERE store_id = ? and book_id = ? and stock_level >= ?; ",
                #     (count, store_id, book_id, count),
                # )
                # mysql数据库
                cursor = self.conn.cursor()
                cursor.execute(
                    f"""UPDATE store set stock_level = stock_level - {count} WHERE store_id = '{store_id}' and book_id = '{book_id}' and stock_level >= {count};"""
                )
                if cursor.rowcount == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)

                # # sqlite数据库
                # self.conn.execute(
                #     "INSERT INTO new_order_detail(order_id, book_id, count, price) "
                #     "VALUES(?, ?, ?, ?);",
                #     (uid, book_id, count, price),
                # )
                # mysql数据库
                cursor = self.conn.cursor()
                cursor.execute(
                    f"""INSERT INTO new_order_detail(order_id, book_id, count, price) VALUES ('{uid}', '{book_id}', {count}, {price});"""
                )

            # # sqlite数据库
            # self.conn.execute(
            #     "INSERT INTO new_order(order_id, store_id, user_id) "
            #     "VALUES(?, ?, ?);",
            #     (uid, store_id, user_id),
            # )
            # mysql数据库
            cursor = self.conn.cursor()
            # cursor.execute(
            #     f"""INSERT INTO new_order(order_id, store_id, user_id) VALUES ('{uid}', '{store_id}', '{user_id}');"""
            # )
            cursor.execute(
                f"""INSERT INTO new_order(order_id, store_id, user_id, is_deliver, is_receive) VALUES ('{uid}', '{store_id}', '{user_id}', 0, 0);"""
            )
            self.conn.commit()
            order_id = uid
        except sqlite.Error as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        conn = self.conn
        try:
            # # sqlite数据库
            # cursor = conn.execute(
            #     "SELECT order_id, user_id, store_id FROM new_order WHERE order_id = ?",
            #     (order_id,),
            # )
            # mysql数据库
            cursor = conn.cursor()
            cursor.execute(
                f"""SELECT order_id, user_id, store_id FROM new_order WHERE order_id = '{order_id}';"""
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id = row[0]
            buyer_id = row[1]
            store_id = row[2]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            # # sqlite数据库
            # cursor = conn.execute(
            #     "SELECT balance, password FROM user WHERE user_id = ?;", (buyer_id,)
            # )
            # mysql数据库
            cursor = conn.cursor()
            cursor.execute(
                f"""SELECT balance, password FROM user WHERE user_id = '{buyer_id}';"""
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            if password != row[1]:
                return error.error_authorization_fail()

            # # sqlite数据库
            # cursor = conn.execute(
            #     "SELECT store_id, user_id FROM user_store WHERE store_id = ?;",
            #     (store_id,),
            # )
            # mysql数据库
            cursor = conn.cursor()
            cursor.execute(
                f"""SELECT store_id, user_id FROM user_store WHERE store_id = '{store_id}';"""
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row[1]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            # # sqlite数据库
            # cursor = conn.execute(
            #     "SELECT book_id, count, price FROM new_order_detail WHERE order_id = ?;",
            #     (order_id,),
            # )
            # mysql数据库
            cursor = conn.cursor()
            cursor.execute(
                f"""SELECT book_id, count, price FROM new_order_detail WHERE order_id = '{order_id}';"""
            )
            total_price = 0
            for row in cursor:
                count = row[1]
                price = row[2]
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            # # sqlite数据库
            # cursor = conn.execute(
            #     "UPDATE user set balance = balance - ?"
            #     "WHERE user_id = ? AND balance >= ?",
            #     (total_price, buyer_id, total_price),
            # )
            # mysql数据库
            cursor = conn.cursor()
            cursor.execute(
                f"""UPDATE user set balance = balance - {total_price} WHERE user_id = '{buyer_id}' AND balance >= {total_price};"""
            )
            if cursor.rowcount == 0:
                return error.error_not_sufficient_funds(order_id)

            # # sqlite数据库
            # cursor = conn.execute(
            #     "UPDATE user set balance = balance + ?" "WHERE user_id = ?",
            #     (total_price, seller_id),
            # )
            # mysql数据库
            cursor = conn.cursor()
            cursor.execute(
                f"""UPDATE user set balance = balance + {total_price} WHERE user_id = '{seller_id}';"""
            )

            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(seller_id)

            # # sqlite数据库
            # cursor = conn.execute(
            #     "DELETE FROM new_order WHERE order_id = ?", (order_id,)
            # )
            # 不再删去历史订单
            # mysql数据库
            # cursor = conn.cursor()
            # cursor.execute(
            #     f"""DELETE FROM new_order WHERE order_id = '{order_id}';"""
            # )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            # # sqlite数据库
            # cursor = conn.execute(
            #     "DELETE FROM new_order_detail where order_id = ?", (order_id,)
            # )
            # 不再删去历史订单
            # mysql数据库
            # cursor = conn.cursor()
            # cursor.execute(
            #     f"""DELETE FROM new_order_detail where order_id = '{order_id}';"""
            # )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            conn.commit()

        except sqlite.Error as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            # # sqlite数据库
            # cursor = self.conn.execute(
            #     "SELECT password from user where user_id=?", (user_id,)
            # )
            # mysql数据库
            cursor = self.conn.cursor()
            cursor.execute(
                f"""SELECT password from user where user_id='{user_id}';"""
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()

            if row[0] != password:
                return error.error_authorization_fail()
            
            # # sqlite数据库
            # cursor = self.conn.execute(
            #     "UPDATE user SET balance = balance + ? WHERE user_id = ?",
            #     (add_value, user_id),
            # )
            # mysql数据库
            cursor = self.conn.cursor()
            cursor.execute(
                f"""UPDATE user SET balance = balance + {add_value} WHERE user_id = '{user_id}';"""
            )
            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(user_id)

            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def receive(self, user_id, order_id) -> (int, str):
        try:
            # 找到order_id对应的user_id
            # mysql数据库
            cursor = self.conn.cursor()
            cursor.execute(
                f"""SELECT user_id FROM new_order WHERE order_id = '{order_id}';"""
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)
            buyer_id = row[0]
            if buyer_id != user_id:
                return error.error_authorization_fail()
            
            # 把new_order表中的is_receive字段置为1
            # mysql数据库
            cursor = self.conn.cursor()
            cursor.execute(
                f"""UPDATE new_order SET is_receive = 1 WHERE order_id = '{order_id}';"""
            )
            
            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
    

    def search_book(self, keyword, search_scope, store_id, start_pos, max_number) -> (int, str, list):
        book_info_list = []
        try:
            if search_scope != "title" and search_scope != "tags" and search_scope != "content" and search_scope != "book_intro":
                return error.error_invalid_search_scope(search_scope) + (book_info_list,)
            if store_id != None and not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (book_info_list,)
            if store_id != None:
                # mysql数据库
                cursor = self.conn.cursor()
                if search_scope == "title":
                    # 在指定store_id中搜索title
                    cursor.execute(
                        f"""SELECT book_info FROM store WHERE store_id = '{store_id}' AND book_title LIKE '%{keyword}%';"""
                    )
                elif search_scope == "tags":
                    # 在指定store_id中搜索tags
                    cursor.execute(
                        f"""SELECT book_info FROM store WHERE store_id = '{store_id}' AND book_tags LIKE '%{keyword}%';"""
                    )
                elif search_scope == "content":
                    # 在指定store_id中搜索content
                    cursor.execute(
                        f"""SELECT book_info FROM store WHERE store_id = '{store_id}' AND book_content LIKE '%{keyword}%';"""
                    )
                elif search_scope == "book_intro":
                    # 在指定store_id中搜索book_intro
                    cursor.execute(
                        f"""SELECT book_info FROM store WHERE store_id = '{store_id}' AND book_book_intro LIKE '%{keyword}%';"""
                    )
                for row in cursor:
                    book_info_list.append(row[0])
                
            else : # store_id == None 表示在全部store中搜索
                # mysql数据库
                cursor = self.conn.cursor()
                if search_scope == "title":
                    # 在指定store_id中搜索title
                    cursor.execute(
                        f"""SELECT book_info FROM store WHERE book_title LIKE '%{keyword}%';"""
                    )
                elif search_scope == "tags":
                    # 在指定store_id中搜索tags
                    cursor.execute(
                        f"""SELECT book_info FROM store WHERE book_tags LIKE '%{keyword}%';"""
                    )
                elif search_scope == "content":
                    # 在指定store_id中搜索content
                    cursor.execute(
                        f"""SELECT book_info FROM store WHERE book_content LIKE '%{keyword}%';"""
                    )
                elif search_scope == "book_intro":
                    # 在指定store_id中搜索book_intro
                    cursor.execute(
                        f"""SELECT book_info FROM store WHERE book_book_intro LIKE '%{keyword}%';"""
                    )
                for row in cursor:
                    book_info_list.append(row[0])
                pass
            
            if start_pos != None and max_number != None: # 分页，只返回指定范围内的搜索结果
                book_info_list = book_info_list[start_pos:start_pos+max_number]
            
            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e)), []
        except BaseException as e:
            return 530, "{}".format(str(e)), []
        return 200, "ok", book_info_list