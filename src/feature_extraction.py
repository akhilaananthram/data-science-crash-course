from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

def get_instance(title, body):
    return title.lower() + " " + body.lower()

def generate_corpus(titles, bodies):
    corpus = [get_instance(t,b) for t, b in zip(titles, bodies)]
    return corpus

class Extractor:
    def __init__(self, vectorizers):
        self.vectorizers = vectorizers

    def transform(self, title, body):
        X = [get_instance(title, body)]
        for v in self.vectorizers:
            X = v.transform(X)

        return X

def bag_of_words(titles, bodies):
    corpus = generate_corpus(titles, bodies)

    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus)

    #vectorizer.get_feature_names()
    #X.toarray()

    return X, Extractor([vectorizer])

def tfidf(titles, bodies):
    transformer = TfidfTransformer()
    counts, bow = bag_of_words(titles, bodies)

    X = transformer.fit_transform(counts)
    return X, Extractor([bow, transformer])

def n_grams(titles, bodies, n_lower=1, n_upper=2):
    corpus = generate_corpus(titles, bodies)
    vectorizer = CountVectorizer(ngram_range=(n_lower, n_upper))
    X = vectorizer.fit_transform(corpus)

    return X, Extractor([vectorizer])
