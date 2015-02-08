import time
import plotly.plotly as py
from plotly.graph_objs import *
import urllib2
from bs4 import BeautifulSoup
import sqlite3
from collections import Counter # For quick counting and sorting
import pandas as pd # C libraries for efficient tabular data
import csv # for fancy cvs handling like auto quoting

#CRAWLER: stackexchange questions
def get_stats(url):
    response = urllib2.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'lxml')

    #title
    s = soup.find('h1', {'itemprop':"name"})
    title = s.get_text()
    title = title.strip()

    #body
    s = soup.find('div', {'class':"post-text"})
    body = s.findChild()

    #tags
    s = soup.find('div', {'class':"post-taglist"})
    tags = [c.get_text() for c in s.findChildren()]

    return title, body, tags

def getAllLinksOnPage(page):
    response = urllib2.urlopen(page)
    html = response.read()
    soup = BeautifulSoup(html, 'lxml')
    hrefs = soup.findAll('a', {'class':"question-hyperlink"})

    links = [h.get('href') for h in hrefs]

    return links

def crawl(seeds, number_to_collect = 250):
    crawled = set()
    print "Starting Crawling"

    count = 0
    frontier = seeds

    #clear old file
    with file("crawled.csv", "w") as f:
        f.write("")

    while count < number_to_collect and frontier != []:
        link = frontier.pop()
        if link in crawled:
            continue

        #link is for a question
        if '/questions/' in link:
            title, body, tags = get_stats(link)
            instance = '"' + str(count) + '","' + title + '","' + body + '","' + " ".join(tags) + '"'
            with file("crawled.csv", "a") as f:
                f.write(instance + "\n")
            count += 1

        crawled.add(link)
        if count == number_to_collect:
            return

        newLinks = getAllLinksOnPage(link)
        frontier = newLinks + frontier

    return sorted(crawled)

#SQL
def sql_example(database):
    db = sqlite3.connect(database)
    db.execute("SELECT * FROM users;")

#READ DATA
def read_data(filename,maxRows=0):
    ####################
    # Dave Fol - Feb 7 #
    # Edited read_data to use c libraries (pandas) #
    ####################

    if maxRows == 0:
        print "Max Rows not specified, data will be read in full and in chunks"
        chunking = True
    else:
        print "Max Rows:" + str(maxRows)
        print "No chunking will occur"
        chunking = False


    #   dataTable is a pandas data frame (numpy array) containing our data
    print "Reading in "+ filename + " ..." 
    if chunking:
        tp = pd.read_csv(filename,names=['index','title','body','tags'],index_col='index',iterator=True,chunksize=5000)
        dataTable = pd.concat(tp, ignore_index=True)
    else:
        dataTable = pd.read_csv(filename,names=['index','title','body','tags'],index_col='index',nrows=maxRows)

    #   Our titles, bodies, and tags can now be accessed as elements of dataTable
    titles = dataTable['title']
    bodies = dataTable['body']
    tags = dataTable['tags']
    tagsSeparated = [x.split() for x in tags]

    #   An empty list is created to hold all of the tags
    unorderedTags = []

    #   tags are separated by space so split() is used and the list is exteneded
    for tagsList in tags: unorderedTags.extend(tagsList.split())

    #   Built in python libraries automaticall count and order our list
    orderedTags = Counter(unorderedTags)

    ####################
    # End of Edit      #
    ####################
    

    return list(titles), list(bodies), tagsSeparated, orderedTags

def simplify_data(titles, bodies, tags, orderedTags, num_sets=2):
    #labels to use
    #Y = set(orderedTags[:num_sets])
    Y =  set([ x[0] for x in orderedTags.most_common(num_sets)])

    simpTitles = []
    simpBodies = []
    simpTags = []
    for t, b, tg in zip(titles, bodies, tags):
        #This instance contains one of the final tags
        #To ensure the categories are separate, it can contain at most one tag
        if len(set(tg) & Y) == 1:
            simpTitles.append(t)
            simpBodies.append(b)
            simpTags.append(list(set(tg) & Y)[0])

    return simpTitles, simpBodies, simpTags, Y

def save_data(titles, bodies, tags, file_name="output.csv"):

    ####################
    # Dave Fol - Feb 7 #
    # Using data frames instead of manual writes #
    ####################

    dataToWrite = pd.DataFrame({'Title':titles,'Body':bodies,'Tags':tags})
    dataToWrite.index +=1
    dataToWrite.to_csv(file_name,header=True,columns=['Title','Body','Tags'],quoting=csv.QUOTE_ALL,index_label="Id")

    ####################
    # End of Edit      #
    ####################

def create_cc_data(input_file, output_file,max_input_size=0):
    print "Reading in data..."
    start = time.time()
    titles, bodies, tags, orderedTags = read_data(input_file,max_input_size)
    end = time.time()
    print end - start
    print "Simplifying data..."
    start = time.time()
    simpTitles, simpBodies, simpTags, Y = simplify_data(titles, bodies, tags, orderedTags)
    end = time.time()
    print end - start
    print "Outputing data..."
    start = time.time()
    save_data(simpTitles, simpBodies, simpTags, output_file)
    end = time.time()
    print end - start

#VISUALIZE DATA
def visualize(titles, bodies, tags):
    #bar graph
    counts = {}
    for tg in tags:
        #in case original data is used
        if type(tg)==list or type(tg)==set:
            for t in tags:
                c = counts.get(t, 0)
                counts[t] = c + 1
        else:
            c = counts.get(tg, 0)
            counts[tg] = c + 1

    labels = []
    values = []
    for t, c in counts.iteritems():
        labels.append(t)
        values.append(c)

    data = Data([
        Bar(
          x = labels,
          y = values
          )
        ])

    layout = Layout(
        title='Frequency of the tags',
        xaxis=XAxis(
            title='Stack Overflow tags',
            titlefont=Font(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        ),
        yaxis=YAxis(
            title='Frequency',
            titlefont=Font(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        )
    )

    fig = Figure(data=data, layout=layout)
    plot = py.plot(fig, filename='Frequencies')

    #word cloud
