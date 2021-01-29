from ftfy import fix_text
from config import normalization
from date_detector import Parser as dParser
import re

# regexp to remove multiple whitespaces
# https://stackoverflow.com/a/2077906/1169798
_RE_COMBINE_WHITESPACE = re.compile(r"\s+")

# init common objects
dDetector = dParser()


def decode(text):
    # https://github.com/LuminosoInsight/python-ftfy/tree/v5.5.1
    return fix_text(text, normalization=normalization)


def remove_special_chars(word):
    # parts = []
    # for part in word.split(' '):
    #     parts = parts + [''.join(e for e in part if e.isalnum() or e == '\'')]
    # return '_'.join(parts)

    # remove whitespace
    word = _RE_COMBINE_WHITESPACE.sub(" ", word).strip()

    # remove parenthesis
    odd_chars = ['[', ']', '{', '}', '(', ')', '*', '^', '/', '\\']
    return ''.join(e for e in word if e not in odd_chars)


def clean_data(lst):
    """
    Removes artificial NaNs and noisy cells -
    Noisy cell contains only special chars.
    """
    empty = ['nan', 'NaN']
    res = []
    for cell in lst:
        if str(cell) in empty:
            cell = ""
        else:
            alphaNum = ''.join(e for e in str(cell) if e.isalnum())
            if alphaNum == "":
                cell = ""
        res = res + [cell]
    return res


def find_date(txt):
    """
    Find first date match in a given string, a string contains multiple dates, it will return the first one only
    Fixed format will also be returned YYY-MM-DD
    """
    clean = txt
    matches = dDetector.parse(txt)
    for m in matches:
        # override clean value with only one date
        # m.date will always return YYYY-MM-DD format
        clean = str(m.date)
        break
    return clean


def find_num(txt):
    """ Find first match to any number in a given txt """
    p = r'[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+'
    lst_nums = re.findall(p, txt)

    # if not match, then return the original string
    if not lst_nums:
        return txt
    else:
        # if some matches here, just pick the first one
        num = lst_nums[0]

        # remove most common mask for numbers
        num = num.replace(',', '')
        return num