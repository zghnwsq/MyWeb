import re


class StringUtils:

    @staticmethod
    def len_check(obj, lo=0, hi=0):
        if not hasattr(input, 'len') or not input:
            return False
        elif not lo and not hi:
            return len(obj)
        
        length = len(obj)
        if lo:
            if length < lo:
                return False
        if hi:
            if length > hi:
                return False
        return True

    @staticmethod
    def reg_check(string: str, reg: str):
        if not isinstance(string, str) or not isinstance(reg, str):
            return None
        return re.match(reg, string)

