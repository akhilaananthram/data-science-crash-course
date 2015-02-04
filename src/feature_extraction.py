from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

def generate_corpus(titles, bodies):
    corpus = [t.lower() + " " + b.lower() for t, b in zip(titles, bodies)]

def bag_of_words(titles, bodies):
    corpus = generate_corpus(titles, bodies)

    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus)

    #vectorizer.get_feature_names()
    #X.toarray()

    return X

def tfidf(titles, bodies):
    transformer = TfidfTransformer()
    counts = bag_of_words(titles, bodies).toarray()

    X = transformer.fit_transform(counts)
    return X

def n_grams(titles, bodies, n_lower=1, n_upper=2):
    corpus = generate_corpus(titles, bodies)
    vectorizer = CountVectorizer(ngram_range=(n_lower, n_upper))
    X = vectorizer.fit_transform(corpus)

    return X
