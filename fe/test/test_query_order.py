import pytest

from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
import uuid


class TestQueryOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_new_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_new_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_new_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        yield
    
    def test_ok(self):
        # import time
        # time.sleep(2)
        code, order_list = self.buyer.query_order()
        # print(order_list)
        assert code == 200
        assert len(order_list) == 1
        assert order_list[0]["order_id"] == self.order_id
        assert order_list[0]["store_id"] == self.store_id
        assert order_list[0]["is_pay"] == 0
        assert order_list[0]["is_deliver"] == 0
        assert order_list[0]["is_receive"] == 0

    def test_non_exist_user_id(self):
        self.buyer.user_id = self.buyer.user_id + "x"
        code, order_list = self.buyer.query_order()
        assert code != 200
