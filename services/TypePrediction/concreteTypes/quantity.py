from supported_types import QUANTITY
from abstractType import Type
import concreteTypes.area_type as area_type
import concreteTypes.volume_type as volume_type
import concreteTypes.distance_type as distance_type
import re


class Quantity(Type):
    def get_type(self, input_str):
        """ Encapsulates Distance, Area and Volume + original file size"""
        try:
            if self.__valid_quantity(input_str) or \
                    self.__is_distance(input_str) or \
                    self.__is_area(input_str) or \
                    self.__is_volume(input_str):
                return QUANTITY
            return False
        except:
            return False

    def __is_area(self, txt):
        area_obj = area_type.Area()
        return area_obj.get_type(txt)

    def __is_volume(self, txt):
        volume_obj = volume_type.Volume()
        return volume_obj.get_type(txt)

    def __is_distance(self, txt):
        distance_obj = distance_type.Distance()
        return distance_obj.get_type(txt)

    def __valid_quantity(self, txt):
        #convert from "2 MB" --> "2MB"
       txt = txt.replace(" ", "")
       return self.__valid_file_size(txt) #or whatever


    def __valid_file_size(self, txt):
        # It handles plural as an optional "s" letter
        regex = re.compile("(\d+(\.\d+)?)+(B|KB|MB|GB|TB|PB)(s)?$")
        res = re.match(regex, txt) is not None
        return res

if __name__ == '__main__':

    txts = ["10 MBs", "2 KB", "1 squared metre", "2 squared metres", "371,000 km2 (143,000 sq mi)",
            "371000km2 (143,000 sq mi)", "371,000 km2"]

    for txt in txts:
        obj = Quantity()
        print(obj.get_type(txt))