from . import solver


def get_type_lst(texts):
    return solver.get_type_lst(texts)


def get_type(text):
    return solver.get_type(text)


def get_spacy_type(text):
    lst = solver.get_spacy_type(text)
    lst = [str(i) for i in lst]
    return lst


def get_spacy_type_lst(texts):
    return solver.get_spacy_type_lst(texts)


if __name__ == '__main__':
    texts = ['1.05', 'Hamza']
    print(get_type_lst(texts))