import random
import pytest

from fe import conf
from fe.access.new_seller import register_new_seller
from fe.access.new_buyer import register_new_buyer
from fe.access import book
import uuid


class TestSearchBook:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # do before test
        self.seller_id = "test_search_book_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_search_book_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_payment_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.seller = register_new_seller(self.seller_id, self.password)
        self.seller2 = register_new_seller(self.seller_id + "y", self.password)
        self.buyer = register_new_buyer(self.buyer_id, self.password)

        code = self.seller.create_store(self.store_id)
        code = self.seller2.create_store(self.store_id+ "y")
        assert code == 200
        book_db = book.BookDB(conf.Use_Large_DB)
        self.books = book_db.get_book_info(0, 10)
        self.books2 = book_db.get_book_info(0, 10)
        
        self.books_all = self.books + self.books2
        
        for b in self.books:
            code = self.seller.add_book(self.store_id, 0, b)
            assert code == 200
        
        for b in self.books2:
            code = self.seller2.add_book(self.store_id + "y", 0, b)
            assert code == 200
        
        yield
        # do after test
        
    def check(self, keyword, search_scope, books, book_info_list):
        # print("keyword: ", keyword)
        # print("search_scope: ", search_scope)
        # print("books: ", books)
        book_info_list_true = []
        for book in books:
            book_info = book.__dict__
            if search_scope =="title":
                if book_info["title"].find(keyword) != -1:
                    book_info_list_true.append(book_info)
            elif search_scope == "tags":
                if str(book_info["tags"]).find(keyword) != -1:
                    book_info_list_true.append(book_info)
            elif search_scope == "content":
                if book_info["content"].find(keyword) != -1:
                    book_info_list_true.append(book_info)
            elif search_scope == "book_intro":
                if book_info["book_intro"].find(keyword) != -1:
                    book_info_list_true.append(book_info)
        # 给book_info_list和book_info_list_true排序
        book_info_list.sort(key=lambda x: str(x))
        book_info_list_true.sort(key=lambda x: str(x))
        # print("book_info_list_true: ", book_info_list_true)
        # print("book_info_list: ", book_info_list)
        # if len(book_info_list_true)!=1:
        #     print(len(book_info_list_true), len(book_info_list))
        # 判断两个list是否相等
        assert book_info_list == book_info_list_true
        pass

    def test_ok(self):
        for book in self.books:
            if book.title != "":
                code, book_info_list = self.buyer.search_book(keyword=book.title, search_scope="title", store_id=self.store_id)
                assert code == 200
                self.check(book.title, "title", self.books, book_info_list)
            if len(book.tags) != 0 and book.tags[0] != "":
                code, book_info_list = self.buyer.search_book(keyword=book.tags[0], search_scope="tags", store_id=self.store_id)
                assert code == 200
                self.check(book.tags[0], "tags", self.books, book_info_list)
            if book.content != "":
                code, book_info_list = self.buyer.search_book(keyword=book.content, search_scope="content", store_id=self.store_id)
                assert code == 200
                self.check(book.content, "content", self.books, book_info_list)
            if book.book_intro != "":
                code, book_info_list = self.buyer.search_book(keyword=book.book_intro, search_scope="book_intro", store_id=self.store_id)
                assert code == 200
                self.check(book.book_intro, "book_intro", self.books, book_info_list)
            
            if book.title != "":
                code, book_info_list = self.buyer.search_book(keyword=book.title, search_scope="title", store_id=None) # store_id=None表示搜索所有商店
                assert code == 200
                # self.check(book.title, "title", self.books_all, book_info_list) # pytest只测试当前文件时可以Check，但是测试所有文件时由于其他test case的影响，无法Check
            if len(book.tags) != 0 and book.tags[0] != "":
                code, book_info_list = self.buyer.search_book(keyword=book.tags[0], search_scope="tags", store_id=None) # store_id=None表示搜索所有商店
                assert code == 200
                # self.check(book.tags[0], "tags", self.books_all, book_info_list) # pytest只测试当前文件时可以Check，但是测试所有文件时由于其他test case的影响，无法Check
            if book.content != "":
                code, book_info_list = self.buyer.search_book(keyword=book.content, search_scope="content", store_id=None) # store_id=None表示搜索所有商店
                assert code == 200
                # self.check(book.content, "content", self.books_all, book_info_list) # pytest只测试当前文件时可以Check，但是测试所有文件时由于其他test case的影响，无法Check
            if book.book_intro != "":
                code, book_info_list = self.buyer.search_book(keyword=book.book_intro, search_scope="book_intro", store_id=None) # store_id=None表示搜索所有商店
                assert code == 200
                # self.check(book.book_intro, "book_intro", self.books_all, book_info_list) # pytest只测试当前文件时可以Check，但是测试所有文件时由于其他test case的影响，无法Check
        
        book = self.books[0]
        code, book_info_list = self.buyer.search_book(keyword=book.title, search_scope="title", store_id=None, start_pos=0, max_number=1)
        assert code == 200
        assert len(book_info_list) == 1

    def test_error_search_scope(self):
        book = self.books[0]
        code, book_info_list = self.buyer.search_book(keyword=book.book_intro, search_scope="false_scope", store_id=self.store_id)
        # print("@@@@@@@@@@@@@@@@@@@", book_info_list)
        assert code != 200
    
    def test_error_store_id(self):
        book = self.books[0]
        code, book_info_list = self.buyer.search_book(keyword=book.book_intro, search_scope="title", store_id=self.store_id + "x")
        # print("@@@@@@@@@@@@@@@@@@@", book_info_list)
        assert code != 200