from supported_types import LOCATION
from abstractType import Type

import re

class Location(Type):
    def get_type(self, input_str):
        try:
            if self.__valid_Location(input_str):
                return LOCATION
            return False
        except:
            return False

    def __valid_Location(self, txt):
        return re.match(r"^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$", txt)
if __name__ == '__main__':
    txts = ["+90.0, -127.554334", '51° 31.7´ N', '36° 30′ N',"10th", "21st", "23rd",  "twenty-first", "second", "one hundred seventy-fifth"]
    for txt in txts:
        obj = Location()
        print(obj.get_type(txt))