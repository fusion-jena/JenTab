from ..supported_types import BOOL
from ..abstractType import Type


class Boolean(Type):
    def get_type(self, input_str):
        try:
            s = input_str.lower()
            if s == 'true' or s == 'false':
                return BOOL
            if s == 'yes' or s == 'no':
                return BOOL
            if s == 'right' or s == 'wrong':
                return BOOL
            return False
        except:
            return False



if __name__ == '__main__':
    obj = Boolean()
    print(obj.get_type("True"))
