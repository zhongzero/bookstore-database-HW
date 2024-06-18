import json
import requests
import simplejson
from urllib.parse import urljoin
from fe.access.auth import Auth


class Buyer:
    def __init__(self, url_prefix, user_id, password):
        self.url_prefix = urljoin(url_prefix, "buyer/")
        self.user_id = user_id
        self.password = password
        self.token = ""
        self.terminal = "my terminal"
        self.auth = Auth(url_prefix)
        code, self.token = self.auth.login(self.user_id, self.password, self.terminal)
        assert code == 200

    def new_order(self, store_id: str, book_id_and_count: [(str, int)]) -> (int, str):
        books = []
        for id_count_pair in book_id_and_count:
            books.append({"id": id_count_pair[0], "count": id_count_pair[1]})
        json = {"user_id": self.user_id, "store_id": store_id, "books": books}
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "new_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        response_json = r.json()
        return r.status_code, response_json.get("order_id")

    def payment(self, order_id: str):
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "order_id": order_id,
        }
        url = urljoin(self.url_prefix, "payment")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def add_funds(self, add_value: str) -> int:
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "add_value": add_value,
        }
        url = urljoin(self.url_prefix, "add_funds")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code
    
    def receive(self, order_id: str) -> int:
        json = {
            "user_id": self.user_id,
            "order_id": order_id,
        }
        url = urljoin(self.url_prefix, "receive")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code
    
    def search_book(self, keyword: str, search_scope: str, store_id: str, start_pos: int=None, max_number: int=None) -> (int, list):
        json_ = {
            "keyword": keyword,
            "search_scope": search_scope,
            "store_id": store_id,
            "start_pos": start_pos,
            "max_number": max_number
        }
        url = urljoin(self.url_prefix, "search_book")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json_)
        response_json = r.json()
        book_info_list = [json.loads(book) for book in response_json.get("book_info_list")]
        return r.status_code, book_info_list
    
    def query_order(self) -> (int, list):
        json_ = {
            "user_id": self.user_id
        }
        url = urljoin(self.url_prefix, "query_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json_)
        response_json = r.json()
        order_list = [json.loads(book) for book in response_json.get("order_list")]
        return r.status_code, order_list
    
    def cancel_order(self, order_id: str) -> (int, list):
        json_ = {
            "user_id": self.user_id,
            "order_id": order_id
        }
        url = urljoin(self.url_prefix, "cancel_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json_)
        return r.status_code