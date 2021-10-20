from . import solver

def get_language(text):
    model = solver.loadModel()
    return solver.predictLanguage(text, model)


def get_language_lst(texts):
    model = solver.loadModel()
    return solver.predictLanguages(texts, model)


if __name__ == '__main__':
    model = solver.loadModel()
    print(solver.test(model))
