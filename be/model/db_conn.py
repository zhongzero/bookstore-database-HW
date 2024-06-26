from be.model import store


class DBConn:
    def __init__(self):
        self.conn = store.get_db_conn()

    def user_id_exist(self, user_id):
        # # sqlite数据库
        # cursor = self.conn.execute(
        #     "SELECT user_id FROM user WHERE user_id = ?;", (user_id,)
        # )
        # mysql数据库
        cursor = self.conn.cursor()
        cursor.execute(
            f"""SELECT user_id FROM user WHERE user_id = '{user_id}';"""
        )
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        # # sqlite数据库
        # cursor = self.conn.execute(
        #     "SELECT book_id FROM store WHERE store_id = ? AND book_id = ?;",
        #     (store_id, book_id),
        # )
        # mysql数据库
        cursor = self.conn.cursor()
        cursor.execute(
            f"""SELECT book_id FROM store WHERE store_id = '{store_id}' AND book_id = '{book_id}';"""
        )
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        # # sqlite数据库
        # cursor = self.conn.execute(
        #     "SELECT store_id FROM user_store WHERE store_id = ?;", (store_id,)
        # )
        # mysql数据库
        cursor = self.conn.cursor()
        cursor.execute(
            f"""SELECT store_id FROM user_store WHERE store_id = '{store_id}';"""
        )
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True
