import argparse
import numpy as np

from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm

import data_acquisition as da
import feature_extraction as fe
import evaluation

def parse_args():
    parser = argparse.ArgumentParser(description='Supervised Learning Tutorial')
    parser.add_argument('data', type=str, help="Path to tagged data file")
    parser.add_argument('--feature', dest='feat', type=str, default='bow',
        options=['bow', 'tfidf', 'bigram', 'trigram'], help="Type of feature to use")
    parser.add_argument('--classifier', dest='classifier', type=str, default='knn',
        options=['knn','log-reg', 'dec-tree', 'svm'], help="Type of classifier to use")

    return parser.parse_args()

if __name__=="__main__":
    args = parse_args()

    print "Reading data..."
    titles, bodies, tags_sets, _ = da.read_data(args.data)
    tags = [list(t)[0] for t in tags_sets]

    X_train, X_test, y_train, y_test = evaluation.cross_validation(zip(titles, bodies), tags)
    X_train_t, X_train_b = zip(*X_train)

    print "Generating features..."
    if args.feat == "bow":
        X, extractor = fe.bag_of_words(X_train_t, X_train_b)
    elif args.feat == "tfidf":
        X, extractor = fe.tfidf(X_train_t, X_train_b)
    elif args.feat == "bigram":
        X, extractor = fe.ngrams(X_train_t, X_train_b, n_upper=2)
    else:
        X, extractor = fe.ngrams(X_train_t, X_train_b, n_upper=3)

    print "Train..."
    if args.classifier == "knn":
        classifier = KNeighborsClassifier(n_neighbors=3)
    elif args.classifier == "log-reg":
        classifier = LogisticRegression(C=1e5)
    elif args.classifier == "dec-tree":
        classifier = DecisionTreeClassifier()
    else:
        classifier = svm.SVC()

    classifier.fit(X, y_train)

    print "Test..."
    predictions = [classifier.predict(extractor.transform(t, b))[0] for t,b in X_test]

    evaluation.confusion_matrix(y_test, predictions)
