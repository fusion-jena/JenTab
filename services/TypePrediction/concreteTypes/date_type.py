from date_detector import Parser as dDetector
from dateutil.parser import parse as dparse
from datetime import datetime
import calendar
from supported_types import DATE
from abstractType import Type

class Date(Type):
    def __hard_coded_date(self, txt):
        """ Try parsing default date formats (most common) overcome date_detector limitation for very old dates"""
        formats = ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",
                   "%d/%m/%y", "%d-%m-%y", "%d.%m.%y",

                   "%Y/%m/%d", "%Y-%m-%d", "%Y.%m.%d",
                   "%y/%m/%d", "%y-%m-%d", "%y.%m.%d",

                   "%B %d %Y",  # fullMonth day YYYY
                   "%b %d %Y",  # shortMonth day YYYY

                   "%B %d %y",  # fullMonth day YY
                   "%b %d %y",  # shortMonth day YY

                   "%d %B %Y",  # day fullMonth YYYY
                   "%d %b %Y",  # day shortMonth YYYY

                   "%d %B %y",  # day fullMonth YY
                   "%d %b %y",  # day shortMonth YY

                   "%m/%d/%Y", "%m-%d-%Y", "%m.%d.%Y",  # month(num) ? day ? YYYY
                   "%m/%d/%y", "%m-%d-%y", "%m.%d.%y",  # month(num) ? day ? YY

                   "%b %d %Y %I%p",  # 12-hour format
                   "%b %d %y %I%p",

                   "%B %d %Y %I%p",
                   "%B %d %y %I%p",

                   "%b %d %Y %I:%M%p",  # 12-hour format:Minutes
                   "%b %d %y %I:%M%p",

                   "%B %d %Y %I:%M%p",
                   "%B %d %y %I:%M%p",

                   "%b %d %Y %I:%M:%S%p",  # 12-hour format:Minutes:Seconds
                   "%b %d %y %I:%M:%S%p",

                   "%B %d %Y %I:%M:%S%p",
                   "%B %d %y %I:%M:%S%p",

                   "%b %d %Y %H",  # 24-hour format
                   "%b %d %y %H",

                   "%B %d %Y %H",
                   "%B %d %y %H",

                   "%b %d %Y %H:%M",  # 24-hour format:Minutes
                   "%b %d %y %H:%M",

                   "%B %d %Y %H:%M",
                   "%B %d %y %H:%M",

                   "%b %d %Y %H:%M:%S",  # 24-hour format:Minutes:Seconds
                   "%b %d %y %H:%M:%S",

                   "%B %d %Y %H:%M:%S",
                   "%B %d %y %H:%M:%S",

                   "%H:%M:%S"]
        isValid = False
        for format in formats:
            try:
                parsed = datetime.strptime(txt, format)
                if parsed:
                    isValid = True
                    break
            except ValueError as err:
                continue
        return isValid

    def __valid_fuzz_data(self, txt):
        """
            Enables Fuzzy parsing od dparse in case of the following keywords Only
            if you just enabled the Fuzzy match unconditionally, it will return true for cases like 123456789
            tried (May 2020)
        """
        keywords = ["today", "morning", "yesterday", "next", "last", "week", "month", "year", "evening", "night"]
        months = [calendar.month_name[i].lower() for i in range(1,12)]
        months_shortname = [calendar.month_abbr[i].lower() for i in range(1,12)]
        weekdays = [calendar.day_name[i].lower() for i in range(1,7)]
        weekdays_shortname = [calendar.day_abbr[i].lower() for i in range(1, 7)]
        keywords = keywords + months + months_shortname + weekdays + weekdays_shortname

        txt_lowered = txt.lower()
        for keyword in keywords:
            if txt_lowered.find(keyword) >= 0:
                try:
                    dparse(txt_lowered, fuzzy=True)
                    return True
                    break
                except ValueError as err:
                    return False

    def __valid_date(self, txt):
        """
        Locates any date inside a string. Useful for cases that contains multiple dates
        i.e., 2009-10-20 October 20, 2009
        NOTE: date_detector works fine for dates >= 1950, it will fail for 1900 for example.
        """
        try:
            # Parse method from date_detector looks for multiple matches inside a given string
            parser = dDetector()
            matches = parser.parse(txt)
            for m in matches:
                # print(m)
                # Return True iff there is a real match, simulates matches.any()
                return True
            return False

        except ValueError:
            return False

    def get_type(self, input_str):
        try:
            if self.__hard_coded_date(input_str) or \
                    self.__valid_date(input_str) or \
                    self.__valid_fuzz_data(input_str):
                return DATE
            return False
        except:
            return False

if __name__ == '__main__':
    # txts = ["Lake is on Baffin Island  and  is th e largest lake on an island .26"]
    txts = ["1900-01-01", "2012-01-23", "2009-10-20 October 20, 2009", "$2.3US", "4/30/2010", "May 18, 2009  02009-05-19", "tonight 9am", "Jun 1 2005  23:33:00", "Jun 1 05 1:33:00PM", "Jun 1 2005  1:33:00PM","Jun 1 05  1:33PM", "04/01/2020",
            "October 04 2020", "4 October 2020", "12/12/2001", "01-01-2020", "31.01.20"]
    for txt in txts:
        obj = Date()
        print(obj.get_type(txt))