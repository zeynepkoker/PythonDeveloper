#### Author: Zeynep KOKER
#### e-mail: zeyneepkkr@gmail.com
#### github_link: https://github.com/zeynepkoker
#### Linkedin: https://www.linkedin.com/in/zeynep-koker/


import itertools
import matplotlib.pyplot as plt
import pandas as pd
import requests
from bs4 import BeautifulSoup
import pymongo
from datetime import datetime
from itertools import groupby
import logging


def Pagination(source_url, start_page_number, end_page_number):
    '''
    Pagination takes the main source URL, the starting page and the last page as string, integer and integer as input, respectively.
    It also saves the data as an Excel file for easy follow-up.
    !! If this code is changed on the front-end side of the main source code, there may be problems in its operation.
    :param source_url:
    :param start_page_number:
    :param end_page_number:
    :return: data which exactly same with database as array
    '''
    fail_count = 0
    success_count = 0
    start_time = datetime.now()

    collection_stats = db["stats"]
    logging.basicConfig(filename='logs.log', level=logging.INFO)
    post_class = 'post-link'
    final_matrix= []
    for i in range(start_page_number, end_page_number +1):
        url = f'{source_url}page/{start_page_number}/'
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding="utf-8")
            elements_with_class = soup.find_all('a', class_=post_class)
            for element in elements_with_class:
                each_url = element['href']
                try:
                    each_news,temp_matrix = eachNewsFromHTML(each_url)
                    collection_news.insert_one(each_news)
                    final_matrix.append(temp_matrix)
                    logging.info(f"Data loaded and Inserted to DB - {each_url}")
                    success_count += 1
                except Exception as e:
                    fail_count += 1
                    logging.error(f"Failed to retrieve the page. - {url}: {str(e)}")
        else:
            logging.error(f"Failed to retrieve the page. Status code: {response.status_code}")


    # These part is optional #
    df = pd.DataFrame(final_matrix)
    df.columns = ["url", "header", "summary", "text", "img_url_list", "publish_date", "update_date"]
    df.to_excel(excel_writer = "All_News.xlsx")
    # These part is optional #

    end_time = datetime.now()
    elapsed_time = (end_time - start_time).seconds
    start_time_without_seconds = start_time.strftime("%m/%d/%Y, %H:%M")

    stats = {
        "elapsed_time": elapsed_time,
        "count": success_count + fail_count,
        "date": start_time_without_seconds,
        "success_count": success_count,
        "fail_count": fail_count
    }
    try:
        collection_stats.insert_one(stats)
        logging.info(f"Stats data loaded and Inserted to DB")
    except Exception as e:
        logging.error(f"ERROR: Stats data could not loaded: {str(e)} ")

    frequentWordsFromAllNews(final_matrix)
    return final_matrix


def eachNewsFromHTML(each_url):
    '''
    This section goes to the detail page of each news from the data drawn as an array within each page.
    !! If this code is changed on the front-end side of the main source code, there may be problems in its operation.

    :param each_url:
    :return: dictionary element for compatible with MongoDB insert_one function and same data as array.
    '''

    header_class = 'single_title'
    img_url = 'data-src'
    img_class = 'onresim wp-post-image'
    date_class = 'tarih'
    content_class = 'yazi_icerik'
    summary_class = 'single_excerpt'
    each_response = requests.get(each_url)
    temp_matrix = []

    if each_response.status_code == 200:
        each_soup = BeautifulSoup(each_response.content, 'html.parser', from_encoding="utf-8")
        temp_matrix.append(each_url)
        header_name = each_soup.find('h1', class_=header_class).text
        temp_matrix.append(header_name)
        summary = each_soup.find('h2', class_=summary_class).text
        temp_matrix.append(summary)
        content = (each_soup.find('div', class_=content_class)).get_text()
        temp_matrix.append(content)
        img_url_list = [img[img_url] for img in each_soup.find_all(class_=img_class)]
        temp_matrix.append(img_url_list)
        date_name = each_soup.find_all('span', class_=date_class)

        posted_time = ""
        updated_time = ""

        for date_time in date_name:
            if 'Yayınlanma:' in date_time.text:
                posted_time = date_time.find('time')['datetime']
                temp_matrix.append(posted_time)
            else:
                updated_time = date_time.find('time')['datetime']
                temp_matrix.append(updated_time)

        each_news = {
                "url": each_url,
                "header": header_name,
                "summary": summary,
                "text": content,
                "img_url_list": img_url_list,
                "publish_date": posted_time,
                "update_date": updated_time,
                }

        return [each_news, temp_matrix]



def frequentWordsFromAllNews(final_matrix):

    '''
    It collects the words in the detailed articles of all news sites in one place and counts each one.
    This dictionary is kept as one of each word and increases by one each time they are mentioned in the news.
    Afterwards, these dictionary values were sorted from largest to smallest and the first 10 values were taken.

    :param final_matrix:
    :return: It returns three results to create a graph.
    '''

    try:
        collection_word_frequency = db["word_frequency"]
        total_dict = {}
        total_words = 0
        for i in range(0, len(final_matrix)):
            each_news_splitted = final_matrix[i][3].split()
            for each_words in each_news_splitted:
                total_words += 1
                if each_words not in total_dict:
                    total_dict[each_words] = 1
                else:
                    total_dict[each_words] = total_dict[each_words] + 1
        sorted_max_to_min = sorted(total_dict.items(), key=lambda x:x[1], reverse=True)
        sorted_max_to_min = dict(sorted_max_to_min)
        number_of_news = len(final_matrix)
        number_of_words = total_words

        most_frequent_ten_words = dict(itertools.islice(sorted_max_to_min.items(), 10))
        for key, value in most_frequent_ten_words.items():
            word_frequency = {
                "word": key,
                "count": int(value)
            }
            collection_word_frequency.insert_one(word_frequency)
        logging.info(f"Frequent Words analysis done and inserted to DB")
        return [most_frequent_ten_words, number_of_news, number_of_words]
    except Exception as e:
        logging.error(f"ERROR: Frequent Words could not analyzed {str(e)} ")


def Graphs(most_frequent_ten_words, number_of_news, number_of_words):
    '''
    This chart works with a dictionary and two integers using the results of frequentWordsFromAllNews.
    :param most_frequent_ten_words:
    :param number_of_news:
    :param number_of_words:
    :return:
    '''
    words = list(most_frequent_ten_words.keys())
    values = list(most_frequent_ten_words.values())

    fig, ax = plt.subplots()

    plt.bar(words, values, color ='maroon', width = 0.4)
    size_value = 12

    ax.text(0.75, 0.80, 'Total # of words: ' + str(number_of_words), horizontalalignment='right', verticalalignment='bottom', transform=ax.transAxes, fontsize=size_value)
    ax.text(0.75, 0.75, 'Total # of news: ' + str(number_of_news), horizontalalignment='right', verticalalignment='bottom', transform=ax.transAxes, fontsize=size_value)

    plt.xlabel("Most Ten Frequent Words", fontsize=size_value)
    plt.ylabel("Frequency of Words in News", fontsize=size_value)
    plt.title("Frequent Words from News", fontsize=size_value)
    plt.savefig('MostTenFrequentWordsGraph.png', bbox_inches='tight')


def UpdateDateSelectFromDB(collections_news):
    '''
    This function combines the update_dates in the data and prints them to the screen, one under the other.
    It uses the collection created in MongoDb as input.
    :param collections_news:
    :return:
    '''
    cursor = collections_news.find().sort("update_date")
    data = list(cursor)
    grouped_data = {key: list(group) for key, group in groupby(data, key=lambda x: x.get("update_date"))}

    for update_date, documents in grouped_data.items():
        print(f"\n Update Date: {update_date} ------- {len(documents)} Data / {len(data)} Total Data \n")
        for document in documents:
            print(document)
        print("\n")


def UpdateDateSelectFromDBWithSpesificTime(collections_news, spesific_time_input):
    '''
    This function prints the data and count values with the same update_time in the data according to the date given as a string (example format: "2023-12-4").

    It uses the collection created in MongoDb as input.
    :param collections_news:
    :param spesific_time_input:
    :return:
    '''
    spesific_time = spesific_time_input
    cursor = collections_news.find().sort(spesific_time)
    data = list(cursor)
    grouped_data = {key: list(group) for key, group in groupby(data, key=lambda x: x.get("update_date"))}

    print("All data with belong update_date:" + spesific_time)
    for update_date, documents in grouped_data.items():
        print(f"Update Date: {update_date} ------- {len(documents)} Data / {len(data)} Total Data ")
        for document in documents:
            print(document)
        print("\n")


if __name__ == "__main__":

    '''
    This is the main part of code...
    These are the example inputs for running the code...
    '''
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["zeynep_koker"]
    collection_news = db["news"]

    source_url = 'https://turkishnetworktimes.com/kategori/gundem/'
    start_page_number = 1
    end_page_number = 50

    final_matrix = Pagination(source_url, start_page_number, end_page_number)
    [most_frequent_ten_words, number_of_news, number_of_words] = frequentWordsFromAllNews(final_matrix)
    Graphs(most_frequent_ten_words, number_of_news, number_of_words)
    UpdateDateSelectFromDB(collection_news)
    UpdateDateSelectFromDBWithSpesificTime(collection_news, "2023-12-4")










