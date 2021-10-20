from ..supported_types import DISTANCE
from ..abstractType import Type
import re


class Distance(Type):
    def get_type(self, input_str):
        try:
            if self.__valid_distance(input_str) or self.__fuzzy_distance(input_str):
                return DISTANCE
            return False
        except:
            return False

    def __fuzzy_distance(self, txt):
        tokens = txt.split(' ')
        for i, t in enumerate(tokens):
            temp = t
            for tt in tokens[i:]:
                if t != tt:
                    temp = temp + " " + tt
                    if self.__valid_distance(temp):
                        return True
        return False

    def __valid_distance(self, txt):
        # convert from "18 Kilometer" --> "18Kilometer"
        temp_txt = txt.replace(" ", "")
        temp_txt = temp_txt.lower()

        # It handles plural as an optional "s" letter
        regex = r"([\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+)(meter|metre|kilometer|kilometre|mile|millimeter|millimetre' \
                '|foot|feet|yard|inch|centimetre|centimeter|m|mm|cm|km|in|ft|yd)(s)?$"

        matches = re.findall(regex, temp_txt)
        if not matches:
            return False
        else:
            return True


if __name__ == '__main__':

    txts = ["1,23 ft 30 m", "30 m", "1.5 Meter", "2M", "18Km", "18 Kilometer", "3 miles", "50mm", "10 feet", "15 yards"]

    for txt in txts:
        obj = Distance()
        print(obj.get_type(txt))
