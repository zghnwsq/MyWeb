import json
from json import JSONDecodeError
from ApiTest.VarMap import VarMap
from ApiTest.HttpRequest import HttpRequest
from requests.utils import dict_from_cookiejar


class ApiKeywords:

    def __init__(self, var_map: VarMap, debug=False):
        self.__res = ''
        self.__debug_info = ''
        self.__debug = debug
        self.var_map = var_map
        self.root = None
        self.http = HttpRequest()

    def base_url(self, *args):
        """
            设置域名和根路径
        :param args: 域名和根路径
        :return: boolean, information
        """
        self.root = args[0]
        self.__res = f'Base url set to: {self.root}'
        return True, self.__res

    def set_header(self, *args):
        """
            设置请求头
        :param args: p1: dict/header_key; p2: header_value
        :return: boolean, information
        """
        p1 = args[0]
        p2 = args[1]
        try:
            if p2:
                p2 = self.var_map.handle_var(p2)
                self.http.add_headers({p1: p2})
            else:
                hds = json.loads(p1)
                for key in hds.keys():
                    hds[key] = self.var_map.handle_var(hds[key])
                self.http.add_headers(hds)
            self.__res = f'Set header: {p1}, {p2}'
            return True, self.__res
        except Exception as e:
            self.__res = f'Fail to set header: {p1}, {p2}'
            self.__debug_info = f'Fail to set header: {p1}, {p2}. Info: {e.__str__()}'
            return False, self.__debug_info if self.__debug else self.__res

    def del_header(self, *args):
        """
            按照key删除header
        :param args:p1: header的key
        :return: boolean, information
        """
        p1 = args[0]
        if p1.strip() != '':
            self.http.remove_headers(p1)
            self.__res = f'Delete header: {p1}'
            return True, self.__res
        else:
            self.__res = f'Empty header: {p1}'
            return False, self.__res

    def clear_headers(self, *args):
        """
            清空headers
        :return: boolean, information
        """
        self.http.clear_headers()
        self.__res = 'Clear all headers.'
        return True, self.__res

    def set_cookie(self, *args):
        """
            手动设置cookie
        :param args: p1: dict/cookie_key; p2: cookie_value
        :return: boolean, information
        """
        p1 = args[0]
        p2 = None if len(args) == 1 else args[1]
        try:
            if p2:
                p2 = self.var_map.handle_var(p2)
                self.http.set_cookie({p1: p2})
            else:
                hds = json.loads(p1)
                for key in hds.keys():
                    hds[key] = self.var_map.handle_var(hds[key])
                self.http.set_cookie(hds)
            self.__res = f'Set cookie: {p1}, {p2}'
            return True, self.__res
        except Exception as e:
            self.__res = f'Fail to set cookie: {p1}, {p2}'
            self.__debug_info = f'Fail to set cookie: {p1}, {p2}. Info: {e.__str__()}'
            return False, self.__debug_info if self.__debug else self.__res

    def get(self, *args):
        """
            发送get请求，headers和cookies通过set方法设置
            1.组装url和url params
            2.发送get请求
        :param args: p1: uri;p2: url params json-like string
        :return: boolean, information
        """
        p1 = args[0]
        p2 = args[1]
        try:
            if p1.startswith('/') and self.root is not None:
                url = f'{self.root}{p1}'
            elif self.root is not None:
                url = f'{self.root}/{p1}'
            else:
                url = p1
            url_params_dict = json.loads(p2)
            for key in url_params_dict.keys():
                url_params_dict[key] = self.var_map.handle_var(url_params_dict[key])
            request_headers = self.http.headers
            request_cookies = dict_from_cookiejar(self.http.cookies)
            self.http.get(url, url_param=url_params_dict)
            response_headers = self.http.get_response_headers()
            status_code = self.http.get_response_status_code()
            self.__res = self.http.get_response_text()
            self.__debug_info = f'Url: {url} \n Url Params: {p2} \n Request headers: {request_headers} \n Request cookies: {request_cookies} \n Url: {url} \n Response status code: {status_code} \n Respones headers: {response_headers} \n Response data: {self.__res}'
            return True, self.__debug_info if self.__debug else self.__res
        except JSONDecodeError:
            self.__res = f'Url params json.loads解析失败: {p1}, {p2}'
            self.__debug_info = f'Url params json.loads解析失败: {p1}, {p2}.'
            return False, self.__debug_info if self.__debug else self.__res
        except Exception as e:
            self.__res = f'Fail to get: {p1}, {p2}'
            self.__debug_info = f'Fail to get: {p1}, {p2}. Info: {e.__str__()}'
            return False, self.__debug_info if self.__debug else self.__res

    def post(self, *args):
        """
            发送post请求，headers和cookies通过set方法设置
        :param args:p1: uri;p2: data
        :return: boolean, information
        """
        p1 = args[0]
        p2 = args[1]
        try:
            uri = self.var_map.handle_var(p1)
            if p1.startswith('/') and self.root is not None:
                url = f'{self.root}{uri}'
            elif self.root is not None:
                url = f'{self.root}/{uri}'
            else:
                url = uri
            request_headers = self.http.headers
            request_cookies = dict_from_cookiejar(self.http.cookies)
            self.http.post(url, data=p2)
            response_headers = self.http.get_response_headers()
            status_code = self.http.get_response_status_code()
            self.__res = self.http.get_response_text()
            self.__debug_info = f'Url: {url} \n Data: {p2} \n Request headers: {request_headers} \n Request cookies: {request_cookies} \n Url: {url} \n Response status code: {status_code} \n Respones headers: {response_headers} \n Response data: {self.__res}'
            return True, self.__debug_info if self.__debug else self.__res
        except Exception as e:
            self.__res = f'Fail to post: {p1}, {p2}'
            self.__debug_info = f'Fail to post: {p1}, {p2}. Info: {e.__str__()}'
            return False, self.__debug_info if self.__debug else self.__res

    def json_extractor(self, *args):
        """
            根据json path提取值到var map
        :param args:p1: 参数名;p2: json path
        :return: boolean, information
        """
        p1 = args[0]
        p2 = args[1]
        try:
            value = self.http.get_value_by_json_path(p2)
            self.var_map.set_var(p1, value)
            self.__res = f'Set "{p1}={value}" by json_path="{p2}" from response.'
            return True, self.__res
        except JSONDecodeError as e:
            return False, e.__str__()

    def xpath_extractor(self, *args):
        """
            根据xpath提取值到var map
        :param args:p1: 参数名;p2: xpath
        :return: boolean, information
        """
        p1 = args[0]
        p2 = args[1]
        try:
            value = self.http.get_value_by_xpath(p2)[0]
            self.var_map.set_var(p1, value)
            self.__res = f'Set "{p1}={value}" by xpath="{p2}" from response.'
            return True, self.__res
        except Exception as e:
            return False, e.__str__()

    def assert_status_code(self, *args):
        """
            断言状态码
        :param args:p1: 期望值，多值逗号分隔
        :return: boolean, information
        """
        p1 = args[0]
        status_code = self.http.get_response_status_code()
        expected = p1.split(',')
        self.__res = f'Assert status code: expected: {p1}, actual: {status_code}'
        if str(status_code) in expected:
            return True, self.__res
        else:
            return False, self.__res

    def assert_equals(self, *args):
        """
            断言值
        :param args:p1: 期望值; p2: 实际值
        :return: boolean, information
        """
        p1 = args[0]
        p2 = args[1]
        p1 = self.var_map.handle_var(p1)
        p2 = self.var_map.handle_var(p2)
        self.__res = f'Assert status code: expected: {p1}, actual: {p2}'
        if p1.strip() == p2.strip():
            return True, self.__res
        else:
            return False, self.__res

    def assert_by_xpath(self, *args):
        """
            根据xpath取值断言
        :param args:p1: 期望值; p2: xpath
        :return: boolean, information
        """
        p1 = args[0]
        p2 = args[1]
        try:
            value = self.http.get_value_by_xpath(p2)
            p1 = self.var_map.handle_var(p1)
            res = self.http.get_response_text()
            self.__res = f'Assert by xpath={p2}: expected: {p1}, actual: {value}'
            self.__debug_info = f'Assert by xpath={p2}: expected: {p1}, actual: {value} \n Response: {res}'
            if p1.strip() == value.strip():
                return True, self.__debug_info if self.__debug else self.__res
            else:
                return False, self.__debug_info if self.__debug else self.__res
        except Exception as e:
            return False, e.__str__()

    def assert_by_jpath(self, *args):
        """
            根据json path取值断言
        :param args:p1: 期望值; p2: xpath
        :return: boolean, information
        """
        p1 = args[0]
        p2 = args[1]
        try:
            value = self.http.get_value_by_json_path(p2)
            p1 = self.var_map.handle_var(p1)
            res = self.http.get_response_text()
            self.__res = f'Assert by json_path={p2}: expected: {p1}, actual: {value}'
            self.__debug_info = f'Assert by json_path={p2}: expected: {p1}, actual: {value} \n Response: {res}'
            if p1.strip() == value.strip():
                return True, self.__debug_info if self.__debug else self.__res
            else:
                return False, self.__debug_info if self.__debug else self.__res
        except JSONDecodeError as e:
            return False, e.__str__()

    def assert_res_contains(self, *args):
        """
        断言response中的值是否包含预期值
        :param args:p1: 期望值
        :return: boolean, information
        """
        p1 = args[0]
        res = self.http.get_response_text()
        p1 = self.var_map.handle_var(p1)
        if p1 in res:
            self.__res = f'Assert result contains: {p1}, True'
            self.__debug_info = f'Assert result contains: {p1}, True \n Response: {res}'
            return True, self.__debug_info if self.__debug else self.__res
        else:
            self.__res = f'Assert result contains: {p1}, False'
            self.__debug_info = f'Assert result contains: {p1}, False \n Response: {res}'
            return False, self.__debug_info if self.__debug else self.__res




