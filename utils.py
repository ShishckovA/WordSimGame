from navec import Navec

from config import EMBEDDINGS_PATH, WORDS_PATH


def load_embeddings_navec(emb_path):
    return Navec.load(emb_path)


def load_embeddings_ruscorp(emb_path):
    res = {}
    with open(emb_path, "r") as fin:
        next(fin)
        for line in fin:
            sp = line.split()
            word, type = sp[0].split("_")
            if type != "NOUN":
                continue
            emb = list(map(float, sp[1:]))
            res[word] = emb
    return res


def read_vocab(filename):
    words = []
    with open(filename) as f:
        for elem in f.readlines():
            words.append(elem.strip())
    return words


def filter_words(words, embeddings):
    new_words = []
    for word in words:
        if word in embeddings:
            new_words.append(word)
        # else:
        #     print(word)
    return new_words


# EMBEDDINGS = load_embeddings_navec(EMBEDDINGS_PATH)
EMBEDDINGS = load_embeddings_ruscorp("180/model.txt")
WORDS = filter_words(read_vocab(WORDS_PATH), EMBEDDINGS)
