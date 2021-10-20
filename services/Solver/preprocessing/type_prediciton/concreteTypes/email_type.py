from ..supported_types import EMAIl
from ..abstractType import Type

import re



class Email(Type):
    def get_type(self, input_str):
        try:
            if self.__valid_email(input_str):
                return EMAIl
            return False
        except:
            return False

    def __valid_email(self, email):
        return re.match(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email)