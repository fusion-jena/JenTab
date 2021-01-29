import edlib


def levenshtein(src, target):
    return edlib.align(src, target)['editDistance']


def levenshtein_norm(src, target):
    dist = edlib.align(src, target)['editDistance']
    return float(dist) / max(len(src), len(target))