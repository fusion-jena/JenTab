from re import finditer
import utils.string_dist as sDist


def parse_string(input_str):
    input_str = input_str.replace('_', ' ')
    matches = finditer('.+?(?:(?<=[0-9])(?=[A-Z])|(?<=[0-9])(?=[a-z])|$)', input_str)
    intermediate = ' '.join([m.group(0) for m in matches])
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', intermediate)
    final = ' '.join([m.group(0) for m in matches])
    return final.split(' ')


def remove_special_chars(word):
    parts = []
    for part in word.split(' '):
        parts = parts + [''.join(e for e in part if e.isalnum() or e == '\'')]
    return ''.join(parts)


def get_most_similar(candidates, target_val, endpointService):
    """
    select the entity from candidates that are most similar to the original one
    ties are broken by overall popularity
    """

    closest_dist = float('inf')
    closest_matches = []

    target_val = target_val.lower()
    for cand in candidates:

        # skip candidates, we dont have a label for
        if not cand['labels']:
            continue

        # the dist of this candidate
        distances = [sDist.levenshtein(target_val, label.lower()) for label in cand['labels']]
        dist = min(distances)

        # do we need to update?
        if dist < closest_dist:
            closest_dist = dist
            closest_matches = [cand]
        elif dist == closest_dist:
            closest_matches.append(cand)

    # we got a unique best-match
    if len(closest_matches) == 1:
        return closest_matches[0]

    # break ties by popularity
    cands_uris = [cand['uri'] for cand in closest_matches]
    popularity = endpointService.get_popularity_for_lst.send([cands_uris])
    for cand in closest_matches:
        if (cand['uri'] in popularity) and (len(popularity[cand['uri']]) > 0) and ('popularity' in popularity[cand['uri']][0]):
            cand['popularity'] = int(popularity[cand['uri']][0]['popularity'])
        else:
            cand['popularity'] = 0
    closest_matches.sort(key=lambda x: x['popularity'], reverse=True)
    return closest_matches[0]
