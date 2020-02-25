#Author: Casey Moroney
#Date Created: 8/8/2019
#Description: Scripte to scrape auto-data website and pull year/make/model and details

#Import necessary libraries

from bs4 import BeautifulSoup
import urllib.request
from urllib import parse
import requests
import re
import ssl
from datetime import datetime
ssl._create_default_https_context = ssl._create_unverified_context
import pandas as pd
from requests import get


homeUrl = "https://www.auto-data.net/en"
homeResponse = get(homeUrl)
homeSoup = BeautifulSoup(homeResponse.text, 'html.parser')

# brandPages  = homeSoup.body.find('div', class_ = 'markite').a['href']


# Build array of brand pages
baseUrl = "https://www.auto-data.net"



brands = homeSoup.find_all('a', class_ = 'marki_blok')
brandPages = []


for brand in brands:
    # brandPage = brands.find('a').a['href']
    brandPage = brand.attrs['href']
    # brandPage = brands.find('a', class_ = 'marki_block').a['href']
    brandPages.append(baseUrl + brandPage)

modelPages = []

for i in brandPages:

    brandPageResponse = get(i)
    modelSoup = BeautifulSoup(brandPageResponse.text, 'html.parser')
    models = modelSoup.find_all('a', class_='modeli')
    # modelPages.append(models)

    for i in models:
        modelPage = i.attrs['href']
        modelPages.append(baseUrl + modelPage)

genPages = []
row = 0
row2 = 0

for i in modelPages:

    row = row + 1
    rowmod = row % 100  # set frequency of print message
    if rowmod == 0:
        print("Model pages completed: " + str(row))  # prints progress message
    modelPageResponse = get(i)
    generationSoup = BeautifulSoup(modelPageResponse.text, 'html.parser')
    generations = generationSoup.find_all('li', class_ = 'generation')

    for i in generations:
        row2 = row2 + 1
        print("Generations finished: " + str(row2))
        genPage = i.a['href']
        genPages.append(baseUrl + genPage)

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
#START FROM HERE
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
modificationPages = []

gen = 0
mod = 0
for i in genPages:
    gen = gen + 1
    if gen % 100 == 0:
        print("Fetching modifications for generation " + str(gen))
    modNameResponse = get(i)
    modSoup = BeautifulSoup(modNameResponse.text, 'html.parser')
    modifications = modSoup.find_all('a', class_ = 'mn')

    for i in modifications:
        mod = mod + 1
        if mod % 100 == 0:
            print("Fetching modification " + str(mod))
        modificationPage = i.attrs['href']
        modificationPages.append(baseUrl + modificationPage)

row = 0
specs = []
titles = []
descriptions = []

response = get(modificationPages[1])
specTags = BeautifulSoup(response.text, 'html.parser').findAll('th')

specNames = []

for i in specTags:
    specName = i.text
    specNames.append(specName)


df = pd.DataFrame()
row = 0
before = datetime.now()
npages = len(modificationPages)

for i in modificationPages:
    row = row + 1
    if row % 100 == 0:
        print("Fetching data for car number " + str(row))
        now = datetime.now()
        diff = now - before
        diffMin = diff.seconds/60
        minPerRec = diffMin/row
        minRemain = minPerRec * (npages-row)
        print("Scipt has been running for " + str(diffMin) + " minutes. Estimated time remaining (min): " + str(minRemain))
    response = get(i)
    html_soup = BeautifulSoup(response.text, 'html.parser')

    # specDf = pd.DataFrame()
    specDict = {}

    title = html_soup.find('h1').text
    specDict["title"] = title

    description = html_soup.table.caption.h3.text
    specDict["description"] = description

    attributes = html_soup.findAll('tr')
    att = 2

    for j in attributes:
        spec = j.td.text
        specName = j.th.text
        specDict[str(specName)] = spec
        # specDf[str(specName)] = spec

        # df[row, att] = spec
        # att = att + 1
        # specs.append(spec)
    # specDf = pd.DataFrame([specDict])
    # df = pd.concat([specDf], df)
    specDf = pd.DataFrame()
    specDf = specDf.append(specDict, ignore_index = True)
    df = pd.concat([df, specDf], axis = 0, ignore_index = True)


df.to_csv('output.csv', encoding='utf-8', index=False)  # outputs to csv

