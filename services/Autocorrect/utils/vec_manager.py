from gensim.models import KeyedVectors
from os.path import join
from utils import util_log
from config import ASSET_PATH

class VecIO():
    def load_model(self):
        util_log.info("Loading model...")
        model = KeyedVectors.load_word2vec_format(
            join(ASSET_PATH, 'GoogleNews-vectors-negative300.bin'), binary=True)
        return model

    def load_fasttext_model(self):
        util_log.info("Loading fasttext model...")
        model = KeyedVectors.load_word2vec_format(
                join(ASSET_PATH, 'wiki-news-300d-1M.vec'))
        return model

if __name__ == '__main__':
    model = VecIO().load_model()
    similar = model.most_similar(positive=['man'], topn=1)
    print(similar)
