from supported_types import URL__
from abstractType import Type
import re




class URL(Type):
    def get_type(self, input_str):
        try:
            if self.__valid_url(input_str):
                return URL__
            else:
                return False
        except:
            return False

    def __valid_url(self, txt):
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        res = re.match(regex, txt) is not None
        return res