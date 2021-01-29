from supported_types import VOLUME
from abstractType import Type
import re


class Volume(Type):
    def get_type(self, input_str):
        try:
            if self.__valid_volume(input_str):
                return VOLUME
            return False
        except:
            return False

    def __valid_volume(self, txt):
        # convert from "2 cubic metres" --> "2cubicmetres"
        temp_txt = txt.replace(" ", "")
        temp_txt = temp_txt.lower()

        # It handles plural as an optional "s" letter
        regex = r'([\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+)(cubicmetre|cubicmeter|cubicfoot|cubicmile' \
                  '|cubicinch|cubiccentimetre|litre|liter|gallon|cubiccentimeter|m3|mm3|cm3|km3|in3|ft3|yd3)(s)?'
        matches = re.findall(regex, temp_txt)
        if not matches:
            return False
        else:
            return True


if __name__ == '__main__':

    txts = ["78,200 km3", "78,200 km3 (18,800 cu mi)", "1 cubic metre", "2 cubic metres", "1 gallon", "1.65 litre", "2 cubic"]

    for txt in txts:
        obj = Volume()
        print(obj.get_type(txt))
