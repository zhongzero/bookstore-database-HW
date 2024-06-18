import pytest

from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
import uuid


class TestCancelOrder:
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
        code = self.buyer.cancel_order(self.order_id)
        # print(order_list)
        assert code == 200
        code, order_list = self.buyer.query_order()
        assert code == 200
        assert order_list[0]["is_cancel"] == 1

    def test_authorization_fail(self):
        self.buyer2 = register_new_buyer(self.buyer_id + "x", self.password)
        code = self.buyer2.cancel_order(self.order_id)
        assert code != 200
    
    def test_non_exist_order_id(self):
        code = self.buyer.cancel_order(self.order_id + "x")
        assert code != 200
