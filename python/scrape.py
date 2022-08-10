#Author: Casey Moroney
#Date Created: 8/8/2019
#Last Updated: 8/3/2022
#Description: Script to scrape auto-data website and pull year/make/model and specifications

#Import necessary libraries
from bs4 import BeautifulSoup
import re
import ssl
from datetime import datetime
ssl._create_default_https_context = ssl._create_unverified_context
import pandas as pd
from requests import get

homeUrl = "https://www.auto-data.net/en"
homeResponse = get(homeUrl)
homeSoup = BeautifulSoup(homeResponse.text, 'html.parser')

# Build array of brand pages
baseUrl = "https://www.auto-data.net"


def get_make_pages():
    makes = homeSoup.find_all('a', class_='marki_blok')
    make_pages = []

    for make in makes:
        make_page = make.attrs['href']
        make_pages.append(baseUrl + make_page)

    return make_pages


def get_model_pages(make_pages):
    model_pages = []

    for index, make in enumerate(make_pages):
        make_page_response = get(make)
        model_soup = BeautifulSoup(make_page_response.text, 'html.parser')
        models = model_soup.find_all('a', class_='modeli')
        print(f"Getting model pages for {index+1} of {len(make_pages)} brands...")

        for model in models:
            model_page = model.attrs['href']
            model_pages.append(baseUrl + model_page)

    return model_pages

def get_generation_pages(model_pages):
    gen_pages = []
    print("\n Fetching generations \n")
    for index, page in enumerate(model_pages):
        if index % 10 == 0:
            ts = datetime.now()
            print(f"{ts} - Getting model pages {index+1} of {len(model_pages)}...")  # prints progress message
        model_page_response = get(page)
        generation_soup = BeautifulSoup(model_page_response.text, 'html.parser')

        # Generations can have class = "l green" or "l red"
        # TODO: l green seems to be current models, need to verify and account for this in output dataset
        generations = generation_soup.find_all('tr', {"class" : re.compile('f l.*')})

        for gen in generations:
            gen_page = gen.a['href']
            gen_pages.append(baseUrl + gen_page)

    print("\n Generation fetch complete.\n")
    return gen_pages


def get_trim_pages(gen_pages):
    trim_pages = []
    for index, page in enumerate(gen_pages):
        if index % 10 == 0:
            ts = datetime.now()
            print(f"{ts} - Fetching modifications for generation {index+1} of {len(gen_pages)}")
        trim_response = get(page)
        trim_soup = BeautifulSoup(trim_response.text, 'html.parser')
        trims = trim_soup.find_all('tr', {"class": re.compile('i l.*')})

        for trim in trims:
            trim_page = trim.find_all('a')[0].attrs['href']
            trim_pages.append(baseUrl + trim_page)

    print(f"Finished fetching vehicle trim data.\n")
    return trim_pages


def get_spec_data(gen_pages):
    df = pd.DataFrame()
    before = datetime.now()
    n_pages = len(gen_pages)

    for index, gen_page in enumerate(gen_pages):
        if index % 100 == 0:
            print(f"Fetching data for car number {index+1}")
            ts = datetime.now()
            diff = ts - before
            diff_min = diff.seconds/60
            min_per_rec = diff_min/(index+1)
            min_remain = min_per_rec * (n_pages-index+1)
            print(f"Scipt has been running for {diff_min} minutes. Estimated time remaining (min): {min_remain}")
        response = get(gen_page)
        html_soup = BeautifulSoup(response.text, 'html.parser')

        spec_dict = {"title": html_soup.find('h1').text, "description": html_soup.table.caption.h3.text}
        attributes = html_soup.findAll('tr')
        re_pattern = re.compile("\?")

        for att in attributes:
            match = re_pattern.search(att.th.text)
            if att.td and att.th and not match:
                spec = att.td.text
                spec_name = att.th.text
                spec_dict[str(spec_name)] = spec

        if len(df) == 0:
            df = pd.DataFrame(columns=spec_dict.keys(),
                              data=[spec_dict.values()])
        else:
            new_row = pd.DataFrame(columns=spec_dict.keys(),
                                   data=[spec_dict.values()])
            df = pd.concat([df, new_row])

    print("Finished fetching specification data.")
    return df


def main():
    makes = get_make_pages()
    makes.to_csv('makes.csv', encoding='utf-8', index=False)

    models = get_model_pages(makes)
    models.to_csv('models.csv', encoding='utf-8', index=False)

    generations = get_generation_pages(models[0:5])
    generations.to_csv('generations.csv', encoding='utf-8', index=False)

    trims = get_trim_pages(generations)
    trims.to_csv('trims.csv', encoding='utf-8', index=False)

    specs = get_spec_data(trims)
    specs.to_csv('full_data_raw.csv', encoding='utf-8', index=False)


main()
