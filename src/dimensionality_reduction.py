import cv2
from sklearn.decomposition import PCA
import numpy as np
import plotly.plotly as py
from plotly.graph_objs import *

def read_images():
    data = []
    for i in xrange(1, 28):
        img = cv2.imread('../data/smilie/smilie' + str(i) + '.jpeg')
        data.append(img.flatten())

    return np.array(data)

def pca():
    #This example is from CS 4786
    data = read_images()
    pca_fitter = PCA(n_components=2)
    transformed = pca_fitter.fit_transform(data)

    X = [x for x, y in transformed]
    Y = [y for x, y in transformed]
    trace = Scatter(
            x=X,
            y=Y,
            mode='markers',
            name='images',
            text=range(1,29),
            marker=Marker(
                color='rgb(164, 194, 244)',
                size=12,
                line=Line(
                    color='white',
                    width=0.5
                )
            )
        )
    
    data = Data([trace])

    layout = Layout(
            title='PCA Dimensionality Reduction',
        )

    fig = Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename='PCA')

if __name__=="__main__":
    pca()
