from config import Num_Special_Chars
from supported_types import DECIMAL
from abstractType import Type
import re


class Decimal(Type):
    def get_type(self, input_str):
        # Tolerate some masks using , [] and ()
        possibleMasks = [' ', ',', '[', ']', '(', ')']
        for ch in possibleMasks:
            input_str = input_str.replace(ch, '')
        try:
            # myRe = r"[-+]?[0-9]+[.]?[0-9]+"
            myRe = r"[-+]?[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+"
            if re.fullmatch(myRe, input_str):
                return DECIMAL
            else:
                return False
        except:
            return False


if __name__ == '__main__':
    txts = ['1,884.32', "+123", "+12,34", '1234 345a', '1234']
    # txts = ['1234 345a']
    for txt in txts:
        obj = Decimal()
        print(obj.get_type(txt))
