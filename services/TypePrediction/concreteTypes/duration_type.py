from supported_types import DURATION
from abstractType import Type
import re


class Duration(Type):
    def get_type(self, input_str):
        try:
            if self.__valid_duration(input_str):
                return DURATION
            return False
        except:
            return False

    def __valid_duration(self, txt):
        #convert from "2 hours" --> "2hours"
       temp_txt = txt.replace(" ", "")

       #It handles plural as an optional "s" letter
       regex = re.compile("(\d+(\.\d+)?)+((min|minute|hour|seconds|sec|day|week|month|year)(s)?)$")
       res = re.match(regex, temp_txt) is not None
       return res

if __name__ == '__main__':

    txts = ["1 min", "2 hours", "160 seconds", "2 days", "1 month", "3 months"]

    for txt in txts:
        obj = Duration()
        print(obj.get_type(txt))