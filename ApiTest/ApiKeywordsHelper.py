"""
@Time ： 2022/10/12 10:10
@Auth ： Ted
@File ：ApiKeywordsHelper.py
@IDE ：PyCharm
"""
HEADER = '<div style=\\"text-align: left\\"><span style=\\"font-size: 20px;margin-right: 10px\\">Action</span>|' \
         '<span style=\\"font-size: 20px;margin: 10px\\">p1</span>|' \
         '<span style=\\"font-size: 20px;margin: 10px\\">p2</span>|' \
         '<span style=\\"font-size: 20px;margin: 10px\\">p3</span><br/>'
FOOTER = '</div>'
BASE_URL = '<span class=\'keyword\'>BASE_URL</span>|<span class=\'param\'>http://www.baidu.com</span><br/>'
SET_HEADER = '<span class=\'keyword\'>SET_HEADER</span>|<span class=\'param\'>Content-Type</span>|<span class=\'param\'>application/json</span><br/>'
DEL_HEADER = '<span class=\'keyword\'>DEL_HEADER</span>|<span class=\'param\'>X-Auth-Token</span><br/>'
CLEAR_HEADERS = '<span class=\'keyword\'>CLEAR_HEADERS</span><br/>'
SET_COOKIE = '<span class=\'keyword\'>SET_COOKIE</span>|<span class=\'param\'>{\\"SESSIONID\\": \\"123456\\"}</span><br/>' \
             '<span class=\'keyword\'>SET_COOKIE</span>|<span class=\'param\'>SESSIONID</span>|<span class=\'param\'>123456</span><br/>'
GET = '<span class=\'keyword\'>GET</span>|<span class=\'param\'>/weather</span>|<span class=\'param\'>{\\"locatioin\\": \\"Shanghai\\"}</span><br/>'
POST = '<span class=\'keyword\'>POST</span>|<span class=\'param\'>/login</span>|<span class=\'param\'>{\\"user\\":\\"admin\\"}</span><br/>'
POST_UPLOAD = '<span class=\'keyword\'>POST_UPLOAD</span>|' \
              '<span class=\'param\'>/upload</span></span>|' \
              '<span class=\'param\'>File-Id-abcdefghijk</span></span>|' \
              '<span class=\'param\'>{\\"attach_type\\": \\"bank_card\\"}</span><br/>'
JSON_VALUE = '<span class=\'keyword\'>JSON_VALUE</span>|<span class=\'param\'>token</span>|<span class=\'param\'>$.data.token</span><br/>'
JSON_VALUES = '<span class=\'keyword\'>JSON_VALUES</span>|<span class=\'param\'>result_list</span>|<span class=\'param\'>$.data.result</span><br/>'
XPATH_NODE_TEXT = '<span class=\'keyword\'>XPATH_NODE_TEXT</span>|<span class=\'param\'>user</span>|<span class=\'param\'>//div[@id=\\"user\\"]</span><br/>'
XPATH_NODE_TEXTS = '<span class=\'keyword\'>XPATH_NODE_TEXTS</span>|<span class=\'param\'>results</span>|<span class=\'param\'>//li[@class=\\"cell\\"]</span><br/>'
XPATH_NODE_ATTR = '<span class=\'keyword\'>XPATH_NODE_ATTR</span>|' \
                  '<span class=\'param\'>msg_display</span>|' \
                  '<span class=\'param\'>//div[@class=\\"msg\\"]/attribute::display</span><br/>'
ASSERT_STATUS_CODE = '<span class=\'keyword\'>ASSERT_STATUS_CODE</span>|<span class=\'param\'>200</span><br/>' \
                     '<span class=\'keyword\'>ASSERT_STATUS_CODE</span>|<span class=\'param\'>401,403,404</span><br/>'
ASSERT_EQUALS = '<span class=\'keyword\'>ASSERT_EQUALS</span>|' \
                '<span class=\'param\'>expected_result</span>|' \
                '<span class=\'param\'>${msg}</span><br/>'
ASSERT_NOT_EQUALS = '<span class=\'keyword\'>ASSERT_NOT_EQUALS</span>|' \
                    '<span class=\'param\'>not_expected_result</span>|' \
                    '<span class=\'param\'>${msg}</span><br/>'
ASSERT_RES_CONTAINS = '<span class=\'keyword\'>ASSERT_RES_CONTAINS</span>|<span class=\'param\'>success</span><br/>'
ASSERT_RES_NOT_CONTAINS = '<span class=\'keyword\'>ASSERT_RES_NOT_CONTAINS</span>|<span class=\'param\'>error</span><br/>'
ASSERT_BY_XPATH = '<span class=\'keyword\'>ASSERT_BY_XPATH</span>|' \
                  '<span class=\'param\'>open</span>|' \
                  '<span class=\'param\'>//div[@class=\\"status\\"]</span><br/>'
ASSERT_BY_JPATH = '<span class=\'keyword\'>ASSERT_BY_JPATH</span>|' \
                  '<span class=\'param\'>success</span>|' \
                  '<span class=\'param\'>$.data.msg</span><br/>'
ASSERT_JSON_CONTAINS = '<span class=\'keyword\'>ASSERT_JSON_CONTAINS</span>|' \
                       '<span class=\'param\'>sucess</span>|' \
                       '<span class=\'param\'>$.data.msg</span><br/>'
ASSERT_JSON_CONTAINS_KEYS = '<span class=\'keyword\'>ASSERT_JSON_CONTAINS_KEYS</span>|' \
                            '<span class=\'param\'>id;card_no;info</span>|' \
                            '<span class=\'param\'>$.data.results[*]</span><br/>' \
                            '<span class=\'keyword\'>ASSERT_JSON_CONTAINS_KEYS</span>|' \
                            '<span class=\'param\'>code;msg</span>|' \
                            '<span class=\'param\'>$.data</span><br/>'
ASSERT_JSON_VALUE_IN = '<span class=\'keyword\'>ASSERT_JSON_VALUE_IN</span>|' \
                       '<span class=\'param\'>open;running</span>|' \
                       '<span class=\'param\'>$.data.status</span><br/>' \
                       '<span class=\'keyword\'>ASSERT_JSON_VALUE_IN</span>|' \
                       '<span class=\'param\'>${options}</span>|' \
                       '<span class=\'param\'>$.data.status</span><br/>'
ASSERT_JSON_VALUE_NOT_EMPTY = '<span class=\'keyword\'>ASSERT_JSON_VALUE_NOT_EMPTY</span>|' \
                              '<span class=\'param\'>$.data.status</span><br/>'
ASSERT_JSON_VALUE_EMPTY = '<span class=\'keyword\'>ASSERT_JSON_VALUE_EMPTY</span>|' \
                          '<span class=\'param\'>$.data.error_msg</span><br/>'

# TEMP = '<span class=\'keyword\'>DEL_HEADER</span>|<span class=\'param\'>Token</span><br/>'
HELPER = ''.join(
    [HEADER, BASE_URL, SET_HEADER, DEL_HEADER, CLEAR_HEADERS, SET_COOKIE, GET, POST, POST_UPLOAD, JSON_VALUE,
     JSON_VALUES, XPATH_NODE_TEXT, XPATH_NODE_TEXTS, XPATH_NODE_ATTR, ASSERT_STATUS_CODE, ASSERT_EQUALS,
     ASSERT_NOT_EQUALS, ASSERT_RES_CONTAINS, ASSERT_RES_NOT_CONTAINS, ASSERT_BY_XPATH, ASSERT_BY_JPATH,
     ASSERT_JSON_CONTAINS, ASSERT_JSON_CONTAINS_KEYS, ASSERT_JSON_VALUE_IN, ASSERT_JSON_VALUE_NOT_EMPTY,
     ASSERT_JSON_VALUE_EMPTY, FOOTER])
