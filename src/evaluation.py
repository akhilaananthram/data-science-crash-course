from sklearn import cross_validation as cv
from sklearn.metrics import confusion_matrix as cm

def cross_validation(X, Y):
    X_train, X_test, y_train, y_test = cv.train_test_split(X, Y, test_size=0.3, random_state=0)
    return X_train, X_test, y_train, y_test

def confusion_matrix(actual, prediction):
    matrix = cm(actual, prediction)

    print matrix
