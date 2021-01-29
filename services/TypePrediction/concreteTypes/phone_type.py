from supported_types import PHONE
from abstractType import Type

import phonenumbers


class Phone(Type):
    def get_type(self, input_str):
        try:
            if self.__valid_phone(input_str):
                return PHONE
            return False
        except:
            return False

    def __valid_phone(self, txt):
        z = phonenumbers.parse(txt, None)
        #print (z)
        return z

if __name__ == '__main__':

    txts = ["+1 (650) 123-4567", "+12001230101", "+49 176 1234 5678", "+442083661177", "123", "49 176 1234 5678"]

    for txt in txts:
        obj = Phone()
        print(obj.get_type(txt))