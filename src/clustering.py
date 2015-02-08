from sklearn.cluster import KMeans
import cv2
import matplotlib.pyplot as plt
import numpy as np

def pick_k():
    #read in image as grayscale
    img = cv2.imread('../data/tower.jpg', cv2.CV_LOAD_IMAGE_GRAYSCALE)
    #bucket the pixel intensities
    h = np.histogram(img, 255)
    y, _ = h
    x = range(0, 255)

    plt.scatter(x, y)

def cluster_image():
    img = cv2.imread("../data/tower.jpg")
    w, h, c = img.shape

    X = np.reshape(img, (w * h, c))

    #Fit k-means
    k_means = KMeans(n_clusters=5, n_init=1)
    k_means.fit(X)

    centers = k_means.cluster_centers_.squeeze()
    labels = k_means.labels_

    #view the clusters
    clustered = []
    for l in labels:
        r, g, b = centers[l]
        clustered.append([int(r), int(g), int(b)])

    clustered = np.array(clustered, dtype=np.uint8)

    cv2.imshow("clustered image", np.reshape(clustered, (w, h, c)))
