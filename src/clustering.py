from sklearn.cluster import KMeans
import cv2
import matplotlib.pyplot as plt
import numpy as np

def pick_k():
    img = cv2.imread('../data/tower.jpg', cv2.CV_LOAD_IMAGE_GRAYSCALE)
    h = np.histogram(img, 255)
    y, _ = h
    x = range(0, 255)

    plt.scatter(x, y)

def cluster_image():
    img = cv2.imread("../data/tower.jpg")
    w, h, c = img.shape

    X = np.reshape(img, (w * h, c))

    k_means = KMeans(n_clusters=5, n_init=1)
    k_means.fit(X)

    centers = k_means.cluster_centers_.squeeze()
    labels = k_means.labels_

    compressed = []
    for l in labels:
        r, g, b = centers[l]
        compressed.append([int(r), int(g), int(b)])

    compressed = np.array(compressed, dtype=np.uint8)

    cv2.imshow("clustered image", np.reshape(compressed, (w, h, c)))
