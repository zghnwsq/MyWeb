# coding:utf8
from json import JSONDecodeError
import requests
from requests.cookies import RequestsCookieJar
from requests.utils import cookiejar_from_dict
import json
import jsonpath
import lxml.etree as etree


class HttpRequest:

    def __init__(self):
        self.session = requests.session()
        self.url = ''
        self.response = None
        self.headers = {}
        self.cookie = {}
        self.cookies = RequestsCookieJar()

    def __set_url_params(self, dic):
        """
        将字典形式的url参数拼接到url中
        :param dic: 字典形式的url参数
        :return: 拼接后的url
        """
        if type(dic) != dict:
            raise Exception("Wrong type! Dict required!")
        url_params = '?'
        for key in dic.keys():
            url_params = url_params + '&' + key + '=' + dic[key]
        self.url += url_params

    def set_headers(self, hds):
        """
        设置请求的headers，原有headers将被清空
        :param hds: 字典形式的headers
        :return:
        """
        if type(hds) != dict:
            raise Exception("Wrong type! Dict required!")
        else:
            self.headers.clear()
            self.headers = hds

    def add_headers(self, headers):
        """
        添加/更新请求的headers，保持原有键值
        :param headers: 字典形式的headers
        :return:
        """
        if type(headers) != dict:
            raise Exception("Wrong type! Dict required!")
        else:
            for key in headers.keys():
                self.headers[key] = headers[key]

    def remove_headers(self, headers):
        """
        删除部分headers
        :param headers: 待删除headers的key
        :return:
        """
        keys = headers.split(sep=',')
        for key in keys:
            del self.headers[key]

    def clear_headers(self):
        """
        清空headers
        :return:
        """
        self.headers.clear()

    def set_cookie(self, cookie):
        """
        手动设置cookie
        :param cookie: 要设置的cookie
        :return:
        """
        if type(cookie) != dict:
            raise Exception("Wrong type! Dict required!")
        else:
            for key in cookie.keys():
                self.cookie[key] = cookie[key]

    def clear_cookie(self):
        """
        清空cookie
        :return:
        """
        self.cookie.clear()

    def get(self, url, url_param=None, headers=None, cookie=None):
        """
        以Get方式发送请求
        :param url: 请求的URL，可以直接拼接好参数
        :param url_param: 以字典形式存储的url参数
        :param headers: 以字典形式存储的Header
        :param cookie: 以字典形式存储的cookie
        :return: 返回requests.response对象(状态码)
        """
        self.url = url
        if url_param is not None:
            self.__set_url_params(url_param)
        if headers is not None:
            self.session.headers = headers
        elif self.headers != {}:
            self.session.headers = self.headers
        if cookie is not None:
            self.set_cookie(cookie)
            # 合并自动管理cookie和手动设置cookie
            self.cookies = cookiejar_from_dict(self.cookie, cookiejar=self.cookies, overwrite=True)
            self.session.cookies = self.cookies
        self.response = self.session.get(self.url)
        # 自动更新cookie
        self.cookies.update(self.response.cookies)
        return self.response

    def post(self, url, url_param=None, headers=None, cookie=None, data: str = None, js: dict = None, files=None):
        """
        以POST方式发送请求
        :param url: 请求的URL，可以直接拼接好参数
        :param url_param: 以字典形式存储的url参数
        :param headers: 以字典形式存储的Header
        :param cookie: 以字典形式存储的cookie
        :param data: body中要发送的数据, str
        :param js: body中要发送的json, dict
        :param files: body中要发送的文件{'file_name': file_stream_reader}
        :return: 返回requests.response对象(状态码)
        """
        self.url = url
        if url_param is not None:
            self.__set_url_params(url_param)
        if headers is not None:
            self.session.headers = headers
        elif self.headers != {}:
            self.session.headers = self.headers
        if cookie is not None:
            self.set_cookie(cookie)
            # 合并自动管理cookie和手动设置cookie
            self.cookies = cookiejar_from_dict(self.cookie, cookiejar=self.cookies, overwrite=True)
            self.session.cookies = self.cookies
        self.response = self.session.post(self.url, data=data, json=js, files=files)
        # 自动更新cookie
        self.cookies.update(self.response.cookies)
        return self.response

    def get_response_headers(self):
        """
        :return: 返回响应的Headers
        """
        return self.response.headers

    def get_response_text(self):
        """
        :return: 返回响应的文本结果
        """
        resp = self.response.text
        if isinstance(resp, bytes):
            resp = resp.decode('utf-8')
        return resp

    def get_response_status_code(self):
        """
        :return: 返回响应的状态码
        """
        return self.response.status_code

    def get_value_by_json_path(self, json_path):
        """
        以jsonpath提取响应body中的数据
        :param json_path: jsonpath
        :return: body中的数据
        """
        try:
            js = json.loads(self.response.text)
            result = jsonpath.jsonpath(js, json_path)
            return result
            # if isinstance(result, list):
            #     return result[0]
            # else:
            #     return result
        except JSONDecodeError:
            return 'Error: 响应文本解析为json格式失败.'

    def get_text_by_xpath(self, xpath):
        """
        以xpath提取响应body中的文本数据
        :param xpath: xpath
        :return: body中的数据
        """
        tree = etree.HTML(self.response.text)
        nodes = tree.xpath(xpath)
        values = []
        for node in nodes:
            values.append(node.text)
        # value = tree.xpath(xpath)
        return values

    def get_value_by_xpath(self, xpath):
        """
        以xpath提取响应body中的数据,如attribute::value、attribute::csrf、attribute::style
        :param xpath: xpath
        :return: body中的数据
        """
        tree = etree.HTML(self.response.text)
        value = tree.xpath(xpath)
        return value


