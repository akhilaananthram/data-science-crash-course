import time
import plotly.plotly as py
from plotly.graph_objs import *
import urllib2
from bs4 import BeautifulSoup
import sqlite3

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
    hrefs = = soup.findAll('a', {'class':"question-hyperlink"})

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
def read_data(filename):
    titles = []
    bodies = []
    tags = []
    allTags = {}
    
    with file(filename) as f:
        stream = ""
        for line in f:
            line = line.strip()
            stream = stream + '\n' + line
            #finished one instance
            if stream.count('"') == 8:
                s = stream.split('"')
                title = s[3]
                body = s[5]
                t = set(s[7].split(" "))
                
                titles.append(title)
                bodies.append(body)
                tags.append(t)
                for tg in t:
                    count = allTags.get(tg, 0)
                    allTags[tg] = count + 1

                stream = '"'.join(s[8:])

    print "Sorting"
    orderedTags = sorted(allTags.keys(), key=lambda x:allTags[x], reverse=True)

    return titles, bodies, tags, orderedTags

def simplify_data(titles, bodies, tags, orderedTags, num_sets=2):
    #labels to use
    Y = set(orderedTags[:num_sets])

    simpTitles = []
    simpBodies = []
    simpTags = []
    for t, b, tg in zip(titles, bodies, tags):
        #This instance contains one of the final tags
        #To ensure the categories are separate, it can contain at most one tag
        if len(tg & Y) == 1:
            simpTitles.append(t)
            simpBodies.append(b)
            simpTags.append(list(tg & Y)[0])

    return simpTitles, simpBodies, simpTags, Y

def save_data(titles, bodies, tags, file_name="output.csv"):
    id = 1
    with file(file_name, 'w') as f:
        for t, b, tg in zip(titles, bodies, tags):
            instance = ",".join(['"' + str(id) + '"', '"' + t + '"', '"' + b + '"', '"' + tg + '"'])
            f.write(instance + "\n")

            id += 1

def create_cc_data(input_file, output_file):
    print "Reading in data..."
    start = time.time()
    titles, bodies, tags, orderedTags = read_data(input_file)
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
