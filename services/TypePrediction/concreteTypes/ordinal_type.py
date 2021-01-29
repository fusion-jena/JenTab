from supported_types import ORDINAL
from abstractType import Type

import re



class Ordinal(Type):
    def get_type(self, input_str):
        try:
            if self.valid_numeric_ordinal(input_str) or \
                    self.valid_text_ordinal(input_str):
                return ORDINAL
            return False
        except:
            return False

    def valid_numeric_ordinal(self, txt):
        regex = re.compile('([2-9]+)?(1st|2nd|3rd|[4-9]th)|[1-9]+0th$', re.S)
        res = re.match(regex, txt) is not None
        return res

    def valid_text_ordinal(self, txt):
        res = self.my_text2int(txt)
        if type(res) is int:
            return True
        else:
            return False

    def my_text2int(self, textnum, numwords={}):
        #if not numwords:
        ord_units = [
            "", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth",
            "ninth", "tenth", "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth",
            "sixteenth", "seventeenth", "eighteenth", "nineteenth",
        ]

        ord_tens = ["", "", "twentieth", "thirtieth", "fortieth", "fiftieth", "sixtieth", "seventieth", "eightieth",
                    "ninetieth"]

        ord_scales = ["hundredth", "thousandth", "millionth", "billionth", "trillionth"]

        units = [
            "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
            "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen",
        ]

        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

        scales = ["hundred", "thousand", "million", "billion", "trillion"]

        numstr = ""
        textnum = textnum.replace("-", " ")  # handling hyphen case

        if textnum.strip() == "":
            raise Exception("Illegal number: " + textnum)

        # map from ordinal to normal number
        for word in textnum.split():
            word = word.lower()
            if word in ord_units:
                for idx, ord_word in enumerate(ord_units):
                    if ord_word == word:
                        numstr = numstr + " " + units[idx] + " "

            elif word in ord_tens:
                for idx, ord_word in enumerate(ord_tens):
                    if ord_word == word:
                        numstr = numstr + " " + tens[idx] + " "

            elif word in ord_scales:
                for idx, ord_word in enumerate(ord_scales):
                    if ord_word == word:
                        numstr = numstr + " " + scales[idx] + " "
            else:
                numstr = numstr + " " + word

        #construct new numwords dict if it is not exists already
        if not numwords:
            numstr = numstr.strip()

            numwords["and"] = (1, 0)
            for idx, word in enumerate(units):    numwords[word] = (1, idx)
            for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
            for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

        # convert from normal number to integer
        current = result = 0
        for word in numstr.split():
            if word not in numwords:
                raise Exception("Illegal word: " + word)

            scale, increment = numwords[word]
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0

        # will be vaild iff it successfuly return a number!
        # print(result + current)
        return result + current

if __name__ == '__main__':
    txts = ["--", 'yes!',"10th", "21st", "23rd",  "twenty-first", "second", "one hundred seventy-fifth"]
    for txt in txts:
        obj = Ordinal()
        print(obj.get_type(txt))