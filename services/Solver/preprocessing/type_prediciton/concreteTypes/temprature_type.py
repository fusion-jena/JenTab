from ..supported_types import TEMPRATURE
from ..abstractType import Type
import re


class Temprature(Type):
    def get_type(self, input_str):
        try:
            if self.__valid_temprature(input_str):
                return TEMPRATURE
            return False
        except:
            return False

    def __valid_temprature(self, txt):
        #convert from "18 Kelvin" --> "18Kelvin"
        temp_txt = txt.replace(" ", "")
        temp_txt = temp_txt.lower()

        #It handles plural as an optional "s" letter
        regex = re.compile("(\d+(\.\d+)?)+(fahrenheit|kelvin|celsius|k|f|c|)$")
        res = re.match(regex, temp_txt) is not None

        return res

if __name__ == '__main__':

    txts = ["15.5F", "2C", "18K", "18 Kelvin", "30 Fahrenheit", "80F"]

    for txt in txts:
        obj = Temprature()
        print(obj.get_type(txt))