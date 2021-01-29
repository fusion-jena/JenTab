from supported_types import AREA
from abstractType import Type
import re


class Area(Type):
    def get_type(self, input_str):
        try:
            if self.__valid_area(input_str):
                return AREA
            return False
        except:
            return False

    def __valid_area(self, txt):
        # convert from "2 squared metres" --> "2squaredmetres"
        temp_txt = txt.replace(" ", "")
        temp_txt = temp_txt.lower()

        # It handles plural as an optional "s" letter
        # regex = r"(\d+(\.\d+)?)+(squaredmetre|squaredmeter|squaredfoot|squaredmile" \
        #                    "|squaredinch|squaredcentimetre|squaredcentimeter|mi2|m2|mm2|cm2|km2|in2|ft2|yd2)(s)?$"
        regex = r'([\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+)(squaredmetre|squaredmeter|squaredfoot|squaredmile' \
                            '|squaredinch|squaredcentimetre|squaredcentimeter|mi2|m2|mm2|cm2|km2|in2|ft2|yd2)(s)?'
        matches = re.findall(regex, temp_txt)
        if not matches:
            return False
        else:
            return True


if __name__ == '__main__':

    txts = ["1 squared metre", "2 squared metres", "371,000 km2 (143,000 sq mi)",
            "371000km2 (143,000 sq mi)", "371,000 km2", "noise area"]

    for txt in txts:
        obj = Area()
        print(obj.get_type(txt))
