class VarMap:

    def __init__(self):
        self.vars = {}

    def __str__(self):
        return self.vars.__str__()

    def set_var(self, key, value):
        self.vars[key] = value

    def del_var(self, key):
        k = key.replace('${', '').replace('}', '')
        if k in self.vars:
            return self.vars.pop(key)
        else:
            return 'No such Var!'

    def handle_var(self, string):
        if '${' in string:
            return self._handle_variables_in_string(string)
        else:
            return string

    def _handle_variables_in_string(self, string):
        p = string
        beg = 0
        end = 0
        if '${' in p:
            while p.find('${', beg) != -1:
                beg = p.find('${', beg) + 2
                end = p.find('}', end + 1)
                k = p[beg: end].strip()
                if k in self.vars:
                    val = self.vars[k]
                    # 兼容json格式字符串，不使用替代${、}的方法
                    p = p[:beg - 2] + str(val) + p[end + 1:]
                # map中没有的键，不替换
        return p

    def clear_val(self):
        self.vars.clear()

