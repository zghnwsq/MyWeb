import json
import os.path
from json import JSONDecodeError
from ApiTest.VarMap import VarMap
from ApiTest.HttpRequest import HttpRequest
from requests.utils import dict_from_cookiejar
from ApiTest.models import ApiAttachment
from MyWeb import settings


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
        p1 = args[0]
        self.root = self.var_map.handle_var(p1)
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
            if p1 and p2:
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
            self.__debug_info = f'Debug: Fail to set header: {p1}, {p2}. \n|| Info: {e.__str__()}'
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
        print(args)
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
            self.__debug_info = f'Debug: Fail to set cookie: {p1}, {p2}. \n|| Info: {e.__str__()}'
            return False, self.__debug_info if self.__debug else self.__res

    def __eval_url(self, p1):
        """
             拼接完整url路径
         :param p1: url或uri
         :return: 完整url
         """
        uri = self.var_map.handle_var(p1)
        if p1.startswith('/') and self.root is not None:
            url = f'{self.root}{uri}'
        elif self.root is not None:
            url = f'{self.root}/{uri}'
        else:
            url = uri
        return url

    def get(self, *args):
        """
            发送get请求，headers和cookies通过set方法设置
            1.组装url和url params
            2.发送get请求
        :param args: p1: uri;p2: url params json-like string
        :return: boolean, information
        """
        p1 = self.var_map.handle_var(args[0])
        p2 = self.var_map.handle_var(args[1])
        try:
            url = self.__eval_url(p1)
            url_params_dict = {}
            if p2:
                url_params_dict = json.loads(p2)
            for key in url_params_dict.keys():
                url_params_dict[key] = self.var_map.handle_var(url_params_dict[key])
            request_headers = self.http.headers
            request_cookies = dict_from_cookiejar(self.http.cookies)
            self.http.get(url, url_param=url_params_dict)
            response_headers = self.http.get_response_headers()
            status_code = self.http.get_response_status_code()
            self.__res = self.http.get_response_text()
            self.__debug_info = f'Debug: Url: {url} \n|| Vars: {self.var_map} \n|| Url Params: {url_params_dict} \n|| Request headers: {request_headers} \n|| Request cookies: {request_cookies} \n|| Url: {url} \n|| Response status code: {status_code} \n|| Respones headers: {response_headers} \n|| Response data: {self.__res} \n'
            return True, self.__debug_info if self.__debug else self.__res
        except JSONDecodeError:
            self.__res = f'Url params json.loads解析失败: {p1}, {p2}'
            self.__debug_info = f'Url params json.loads解析失败: {p1}, {p2}. \n|| Vars: {self.var_map} '
            return False, self.__debug_info if self.__debug else self.__res
        except Exception as e:
            self.__res = f'Fail to get: {p1}, {p2}'
            self.__debug_info = f'Debug: Fail to get: {p1}, {p2}.  \n|| Vars: {self.var_map} \n|| Info: {e.__str__()}'
            return False, self.__debug_info if self.__debug else self.__res

    def post(self, *args):
        """
            发送post请求，headers和cookies通过set方法设置
        :param args:p1: uri;p2: data
        :return: boolean, information
        """
        p1 = args[0]
        p2 = args[1]
        data = ''
        try:
            url = self.__eval_url(p1)
            data = self.var_map.handle_var(p2)
            request_headers = self.http.headers
            # jsonpath提取数组转字符串为单引号,json只认双引号
            if 'Content-Type' in self.http.headers and 'json' in self.http.headers['Content-Type'].lower():
                data = data.replace('\'', '\"')
            request_cookies = dict_from_cookiejar(self.http.cookies)
            if not isinstance(data, bytes):
                data = data.encode('utf-8')
            self.http.post(url, data=data)
            response_headers = self.http.get_response_headers()
            status_code = self.http.get_response_status_code()
            self.__res = self.http.get_response_text()
            self.__debug_info = f'Debug: Url: {url} \n|| Data: {data}; Vars: {self.var_map} \n|| Request headers: {request_headers} \n|| Request cookies: {request_cookies} \n|| Url: {url} \n|| Response status code: {status_code} \n|| Respones headers: {response_headers} \n|| Response data: {self.__res} \n'
            return True, self.__debug_info if self.__debug else self.__res
        except Exception as e:
            self.__res = f'Fail to post: {p1}, {data}; \n|| Vars: {self.var_map}'
            self.__debug_info = f'Debug: Fail to post: {p1}, {data}; \n|| Vars: {self.var_map}. \n|| Info: {e.__str__()}'
            return False, self.__debug_info if self.__debug else self.__res

    def post_upload(self, *args):
        """
            发送post请求上传文件，headers和cookies通过set方法设置
        :param args:p1: uri;p2: 文件的uuid; p3: dict-like其他参数
        :return: boolean, information
        """
        p1 = args[0]
        p2 = args[1]
        p3 = args[2]
        try:
            url = self.__eval_url(p1)
            data = self.var_map.handle_var(p3)
            data = json.loads(data)
            request_headers = self.http.headers
            request_cookies = dict_from_cookiejar(self.http.cookies)
            uids = p2.split(';')
            files = {}
            file_streams = []
            result = False
            file_index = 1
            for uid in uids:
                attach = ApiAttachment.objects.filter(uuid=uid)
                file_path = os.path.join(settings.API_ATTACHMENT_ROOT, attach[0].path)
                if attach and os.path.isfile(file_path):
                    file_stream = open(file_path, 'rb')
                    file_streams.append(file_stream)
                    file = (attach[0].file_name, file_stream)
                    files[f'field{file_index}'] = file
            if files:
                self.http.post(url, data=data, files=files)
                response_headers = self.http.get_response_headers()
                status_code = self.http.get_response_status_code()
                result = True
                self.__res = self.http.get_response_text()
                self.__debug_info = f'Debug: Url: {url} \n|| Files: {p2}\n|| Data: {p3}; Vars: {self.var_map} \n|| Request headers: {request_headers} \n|| Request cookies: {request_cookies} \n|| Url: {url} \n|| Response status code: {status_code} \n|| Respones headers: {response_headers} \n|| Response data: {self.__res} \n'
            else:
                self.__res = self.__debug_info = f'File not exists:{p2}'
            for f in file_streams:
                # 重复关闭不会报错
                f.close()
            return result, self.__debug_info if self.__debug else self.__res
        except Exception as e:
            print(e.with_traceback(None))
            self.__res = f'Fail to upload files: {p1}, {p2}, {p3}; \n|| Vars: {self.var_map}'
            self.__debug_info = f'Debug: Fail to upload files: {p1}, {p2}, {p3}; \n|| Vars: {self.var_map}. \n|| Info: {e.__str__()}'
            return False, self.__debug_info if self.__debug else self.__res

    def json_extractor(self, *args, match: int = 1):
        """
            根据json path提取值到var map
        :param args:p1: 参数名;p2: json path
        :param match: 匹配方式, -1:返回全部, 1:返回第一个
        :return: boolean, information
        """
        p1 = args[0]
        p2 = args[1]
        try:
            value = self.http.get_value_by_json_path(p2)
            if isinstance(match, int) and match > 0:
                value = value[match - 1]
            if 'Error' not in value:
                self.var_map.set_var(p1, value)
                self.__res = f'Set "{p1}={value}" by json_path="{p2}" from response.'
                return True, self.__res
            else:
                return False, value
        except JSONDecodeError as e:
            return False, e.__str__()

    def json_value(self, *args):
        """
        :param args: args:p1: 参数名;p2: json path
        :return: 返回第一个
        """
        return self.json_extractor(*args, match=1)

    def json_values(self, *args):
        """
        :param args: args: args:p1: 参数名;p2: json path
        :return: 返回全部
        """
        return self.json_extractor(*args, match=-1)

    def xpath_extractor(self, *args, match: int = 1):
        """
            根据xpath提取文本值到var map
        :param args:p1: 参数名;p2: xpath
        :param match: 匹配方式, -1:返回全部, 1:返回第一个
        :return: boolean, information
        """
        p1 = args[0]
        p2 = args[1]
        try:
            value = self.http.get_text_by_xpath(p2)
            if isinstance(match, int) and match > 0:
                value = value[match - 1]
            self.var_map.set_var(p1, value)
            self.__res = f'Set "{p1}={value}" by xpath="{p2}" from response.'
            return True, self.__res
        except Exception as e:
            return False, e.__str__()

    def xpath_node_text(self, *args):
        """
        :param args: args:p1: 参数名;p2: xpath
        :return: 返回第一个
        """
        return self.xpath_extractor(*args, match=1)

    def xpath_nodes_texts(self, *args):
        """
        :param args: args:p1: 参数名;p2: xpath
        :return: 返回全部
        """
        return self.xpath_extractor(*args, match=-1)

    def xpath_node_attr(self, *args):
        """
        根据xpath提取属性值到var map
        :param args:p1: 参数名;p2: xpath
        :return: boolean, information
        """
        p1 = args[0]
        p2 = args[1]
        try:
            attr = self.http.get_value_by_xpath(p2)[0]
            self.var_map.set_var(p1, attr)
            self.__res = f'Set "{p1}={attr}" by xpath="{p2}" from response.'
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
        self.__res = f'Assert equals: expected: {p1}, actual: {p2}'
        if p1.strip() == p2.strip():
            return True, self.__res
        else:
            return False, self.__res

    def assert_not_equals(self, *args):
        """
            断言值
        :param args:p1: 期望值; p2: 实际值
        :return: boolean, information
        """
        p1 = args[0]
        p2 = args[1]
        p1 = self.var_map.handle_var(p1)
        p2 = self.var_map.handle_var(p2)
        self.__res = f'Assert not equals: not expected: {p1}, actual: {p2}'
        if p1.strip() == p2.strip():
            return False, self.__res
        else:
            return True, self.__res

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
            self.__debug_info = f'Debug: Assert result contains: {p1}, True \n|| Vars: {self.var_map}. \n|| Response: {res}'
            return True, self.__debug_info if self.__debug else self.__res
        else:
            self.__res = f'Assert result contains: {p1}, False'
            self.__debug_info = f'Debug: Assert result contains: {p1}, False \n|| Vars: {self.var_map}. \n|| Response: {res}'
            return False, self.__debug_info if self.__debug else self.__res

    def assert_res_not_contains(self, *args):
        """
        断言response中的值是否不包含预期值
        :param args:p1: 期望不包含的值
        :return: boolean, information
        """
        p1 = args[0]
        res = self.http.get_response_text()
        p1 = self.var_map.handle_var(p1)
        if p1 not in res:
            self.__res = f'Assert result not contains: {p1}, True'
            self.__debug_info = f'Debug: Assert result not contains: {p1}, True \n|| Vars: {self.var_map}. \n|| Response: {res}'
            return True, self.__debug_info if self.__debug else self.__res
        else:
            self.__res = f'Assert result contains: {p1}, False'
            self.__debug_info = f'Debug: Assert result contains: {p1}, False \n|| Vars: {self.var_map}. \n|| Response: {res}'
            return False, self.__debug_info if self.__debug else self.__res

    def assert_by_xpath(self, *args):
        """
            根据xpath取值断言
        :param args:p1: 期望值; p2: xpath
        :return: boolean, information
        """
        p1 = args[0]
        p2 = args[1]
        try:
            value = self.http.get_text_by_xpath(p2)[0]
            if not value:
                value = 'Xpath match nothing.'
            elif 'Error' in value:
                return False, value
            p1 = self.var_map.handle_var(p1)
            res = self.http.get_response_text()
            self.__res = f'Assert by xpath={p2}: expected: {p1}, actual: {value}'
            self.__debug_info = f'Debug: Assert by xpath={p2}: expected: {p1}, actual: {value} \n|| Vars: {self.var_map}. \n|| Response: {res}'
            if p1.strip() == value.strip():
                return True, self.__debug_info if self.__debug else self.__res
            else:
                return False, self.__debug_info if self.__debug else self.__res
        except Exception as e:
            return False, e.__str__()

    def assert_by_jpath(self, *args):
        """
            根据json path取值断言
        :param args:p1: 期望值; p2: jsonpath
        :return: boolean, information
        """
        p1 = args[0]
        p2 = args[1]
        try:
            value = self.http.get_value_by_json_path(p2)[0]
            if isinstance(value, bool):
                value = str(value).lower()
            elif not value:
                value = 'Json path match nothing.'
            elif 'Error' in value:
                return False, value
            p1 = self.var_map.handle_var(p1)
            self.__res = f'Assert by json_path={p2}: expected: {p1}, actual: {value}'
            self.__debug_info = f'Debug: Assert by json_path={p2}: expected: {p1}, actual: {value} \n|| Vars: {self.var_map}. \n||'
            if p1.strip() == value.strip():
                return True, self.__debug_info if self.__debug else self.__res
            else:
                return False, self.__debug_info if self.__debug else self.__res
        except JSONDecodeError as e:
            return False, e.__str__()

    def assert_json_contains_keys(self, *args):
        """
            根据json path断言json响应某一层包含键, 多键用;分隔
        :param args: p1: 期望键, p2：json path
        :return:
        """
        p1 = args[0]
        p2 = args[1]
        try:
            # 列表要使用$.data.apply[*]的形式，否则是二维列表
            values = self.http.get_value_by_json_path(p2) or 'Error: Json path match nothing.'
            if 'Error' in values:
                return False, values
            p1 = self.var_map.handle_var(p1)
            keys = p1.split(';')
            not_contains = []
            for value in values:
                if not isinstance(value, dict):
                    not_contains.append(f'values: {values} is not a list of dict')
                    break
                missing_keys = []
                for key in keys:
                    if key and key not in value.keys():
                        missing_keys.append(key)
                if missing_keys:
                    not_contains.append(f'missing {missing_keys}')
            self.__res = f'Assert json contains keys by json_path={p2}: expected keys: {keys}, actual info: {not_contains}'
            self.__debug_info = f'Debug: Assert json contains keys by json_path={p2}:\n|| expected keys: {keys},\n|| actual missing: {not_contains} \n|| Vars: {self.var_map}. \n||'
            if not_contains:
                return False, self.__debug_info if self.__debug else self.__res
            else:
                return True, self.__debug_info if self.__debug else self.__res
        except JSONDecodeError as e:
            return False, e.__str__()

    def assert_json_value_in(self, *args):
        """
            根据json path断言json某个值属于集合, 集合元素用;分隔
        :param args: p1: 期望集合, p2：json path
        :return:
        """
        p1 = args[0]
        p2 = args[1]
        p1 = self.var_map.handle_var(p1)
        try:
            value = self.http.get_value_by_json_path(p2)
            if not value:
                value = 'Json path match nothing.'
            elif 'Error' in value:
                return False, value
            if isinstance(p1, str):
                p1 = p1.split(';')
            elif isinstance(p1, (list, tuple)):
                pass
            else:
                value = f'P1 should be a collection, but: {p1}.'
            # if not isinstance(value, list):
            #     value = [value]
            not_in = []
            for v in value:
                if v not in p1:
                    not_in.append(v)
            self.__res = f'Assert json value in {p1} by json_path={p2}, actual values: {value}'
            self.__debug_info = f'Debug: Assert json value in {p1} by json_path={p2},\n|| actual values: {value}\n|| Vars: {self.var_map}. \n||'
            if not_in:
                return False, self.__debug_info if self.__debug else self.__res
            else:
                return True, self.__debug_info if self.__debug else self.__res
        except JSONDecodeError as e:
            return False, e.__str__()

    def assert_json_value_not_empty(self, *args):
        """
            根据json path取值断言是否不为空
        :param args:p1: jsonpath;
        :return: boolean, information
        """
        p1 = args[0]
        p1 = self.var_map.handle_var(p1)
        try:
            values = self.http.get_value_by_json_path(p1)
            if 'Error' in values:
                return False, values
            empty = []
            for value in values:
                if isinstance(value, bool) or value is None:
                    value = str(value).lower()
                if not value.strip() and value in ('None', 'null', 'Null'):
                    empty.append(value)
            self.__res = f'Assert by json_path={p1}: expected not null or empty, actual: "{empty}"'
            self.__debug_info = f'Debug: Assert by json_path={p1}: expected not null or empty, actual: "{empty}" \n|| Vars: {self.var_map}. \n||'
            if not empty:
                return True, self.__debug_info if self.__debug else self.__res
            else:
                return False, self.__debug_info if self.__debug else self.__res
        except JSONDecodeError as e:
            return False, e.__str__()

    def assert_json_value_empty(self, *args):
        """
            根据json path取值断言是否为空
        :param args:p1: jsonpath;
        :return: boolean, information
        """
        p1 = args[0]
        p1 = self.var_map.handle_var(p1)
        try:
            values = self.http.get_value_by_json_path(p1)
            if 'Error' in values:
                return False, values
            not_empty = []
            for value in values:
                if isinstance(value, bool) or value is None:
                    value = str(value).lower()
                if value.strip() and value not in ('None', 'null', 'Null'):
                    not_empty.append(value)
            self.__res = f'Assert by json_path={p1}: expected null or empty, actual not empty: "{not_empty}"'
            self.__debug_info = f'Debug: Assert by json_path={p1}: expected null or empty, actual not empty: "{not_empty}" \n|| Vars: {self.var_map}. \n||'
            if not_empty:
                return False, self.__debug_info if self.__debug else self.__res
            else:
                return True, self.__debug_info if self.__debug else self.__res
        except JSONDecodeError as e:
            return False, e.__str__()
