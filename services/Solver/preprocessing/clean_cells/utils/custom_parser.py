from re import finditer


class CustomParser:

    @staticmethod
    def parse(input_str):
        matches = finditer('.+?(?:((?<=[0-9])st|nd|rd|th)|(?<=[0-9])(?=[A-Z])|(?<=[0-9])(?=[a-z])|$)', input_str)
        intermediate = ' '.join([m.group(0) for m in matches])
        matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', intermediate)
        final = ' '.join([m.group(0) for m in matches])
        return final


if __name__ == '__main__':
    # TODO: fix bug: last value should be the same, current parser is Alessand ro Merli
    words = ['articleTitle', '2011-11-29November 29, 2011', '12no', "1stGlobal Opinion Leader's Summit", "Alessandro Merli"]
    obj = CustomParser()

    for word in words:
        print(obj.parse(word))
