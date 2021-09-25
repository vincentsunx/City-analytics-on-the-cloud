# Part of COMP90024 Project Team members are
# Ziyuan Xiao (940448)
# Pengyu Mu(890756)
# Dechao Sun (980546)
# Seehoi Chow(980301)
# Yuexin Li (959634)

import numpy as np
import pandas as pd
import text2emotion as te
import couchdb
import time
import random
from datetime import datetime

random.seed(42)
MASTER_NODE_URL = 'http://admin:admin@172.26.128.217:5984/'
'''
Load tweets
'''
def run():
    server = couchdb.Server(MASTER_NODE_URL)
    all_tweets_db = server["all_tweet"]
    rows = all_tweets_db.view('_all_docs', include_docs=True)
    tw = [row['doc'] for row in rows]
    all_tweet = pd.DataFrame(tw)

    new_tweets_db = server["new_tweet"]
    rows = new_tweets_db.view('_all_docs', include_docs=True)
    tw = [row['doc'] for row in rows]
    new_tweet = pd.DataFrame(tw)
    print('load tweets finished')
    '''
    Preprocessing
    '''
    all_tweet = all_tweet.dropna(subset=['created_at', 'box', 'city'])
    all_tweet = all_tweet.reset_index(drop=True)
    new_tweet = new_tweet.dropna(subset=['created_at', 'box', 'city'])
    new_tweet = new_tweet.reset_index(drop=True)


    # For 'all_tweet' date, add a new column 'day_of_week' to indicate what day is today
    def extract_all_tweet_date(tweet_data):
        all_tweet_date = []
        all_tweet_time = []

        for i in range(tweet_data.shape[0]):

            # if not data_time:
            data_time = str(tweet_data['created_at'][i])
            all_tweet_time.append(data_time[11:13])

            if data_time[9] == '6':
                all_tweet_date.append('Thur')

            if data_time[9] == '7':
                all_tweet_date.append('Fri')

            if data_time[9] == '8':
                all_tweet_date.append('Sat')

            if data_time[9] == '9':
                all_tweet_date.append('Sun')

            if data_time[9] == '0':
                all_tweet_date.append('Mon')

        tweet_data['time_of_tweet'] = all_tweet_time
        tweet_data['day_of_week'] = all_tweet_date


    # For 'new_tweet' date, add a new column 'day_of_week' to indicate what day is today
    # and 'time_of_tweet' to indicate the time of tweet in Greenwich time zone.
    def extract_new_tweet_date(tweet_data):
        all_tweet_date = []
        all_tweet_time = []

        for i in range(tweet_data.shape[0]):
            data_time = str(tweet_data['created_at'][i])
            city = str(tweet_data['city'][i])
            if city == 'Perth (WA)':
                real_time = int(data_time[11:13]) + 8
                all_tweet_time.append(str(real_time))
            elif city == 'Adelaide':
                real_time = int(data_time[11:13]) + 9
                all_tweet_time.append(str(real_time))
            else:
                real_time = int(data_time[11:13]) + 10
                all_tweet_time.append(str(real_time))
            all_tweet_date.append(data_time[:3])

        tweet_data['time_of_tweet'] = all_tweet_time
        tweet_data['day_of_week'] = all_tweet_date


    extract_all_tweet_date(all_tweet)
    extract_new_tweet_date(new_tweet)

    tweet = pd.concat([all_tweet, new_tweet], ignore_index=True)

    # Replace the tweet with 'suburb' name by its greater capital city name
    # For those tweet with suburb name, replaced by its greater city name by comparing the coordinates.
    city = ['Sydney', 'Melbourne', 'Brisbane', 'Perth (WA)', 'Adelaide']
    bbox = {
        "Sydney": [149.971885992, -34.33117400499998, 151.63054702400007, -32.99606922499993],
        "Melbourne": [144.33363404800002, -38.50298801599996, 145.8784120140001, -37.17509899299995],
        "Brisbane": [152.07339276400012, -28.363962911999977, 153.54670756200005, -26.452339004999942],
        "Adelaide": [138.435645001, -35.350296029999974, 139.04403010400003, -34.50022530299998],
        "Perth (WA)": [115.617614368, -32.675715325, 116.239023008, -31.6244855145]
    }


    def tweet_data_5_ct(tweet):
        for i in range(tweet.shape[0]):
            tw = tweet.iloc[i, :]
            # allocate city name by which greater city it belongs
            if tw['city'] not in city:
                cor = str(tw['box']).split()
                if cor == ['nan']:
                    continue

                x_low = cor[0][3:-1]
                x_high = cor[2][1:-1]
                y_low = cor[1][:-2]
                y_high = cor[5][:-2]

                # check if the coordinate locates within the range
                for ct in bbox:
                    if (float(x_low) >= bbox[ct][0]) and (float(x_high) <= bbox[ct][2]) and (
                            float(y_low) >= bbox[ct][1]) and (float(y_high) <= bbox[ct][3]):
                        tweet.iloc[i, -4] = ct
        return tweet


    tweet = tweet_data_5_ct(tweet)
    # deleting the tweet that is not in the range
    tweet = tweet[tweet['city'].isin(city)]
    tweet = tweet.reset_index()
    ct_tweet_count = tweet['city'].value_counts()
    print('preprocessing finished')
    '''
    Scenario 1 The frequency of people tweeting about 'covid-19' in different cities. and How does people's attention to 
    covid-19 on twitter correlate to the real covid-19 situation in different cities?
    
    Output:
    ct_attention_covid: twitter related to covid for different cities
    covid_tweet_in_ct: number of covid related tweet per 1000 tweet in different cities
    covid_data: real covid data
    '''
    # a list of covid related words
    covid_lst = ['covid', 'corona', 'coronavirus', 'covid-19 vaccine', 'covid vaccine',
                 'pandemic', 'covid-19', 'covid-19 vaccination', 'coronavirus pandemic']
    # a dict of how many tweet contains covid-related words in different cities
    ct_attention_covid = {'Sydney': 0, 'Melbourne': 0, 'Brisbane': 0, 'Perth (WA)': 0, 'Adelaide': 0}
    # count the number of covid realated words appear in the 'text' in different cities
    for i in range(tweet.shape[0]):
        tw = tweet.iloc[i, :]
        ct = tw['city']
        for i in covid_lst:
            if i in str(tw['text']).lower():
                ct_attention_covid[ct] += 1

    # covid_tweet_in_ct: number of covid related tweet per 1000 tweet in different cities
    covid_tweet_syd = ct_attention_covid['Sydney'] / ct_tweet_count['Sydney'] * 1000
    covid_tweet_melb = ct_attention_covid['Melbourne'] / ct_tweet_count['Melbourne'] * 1000
    covid_tweet_brisbane = ct_attention_covid['Brisbane'] / ct_tweet_count['Brisbane'] * 1000
    covid_tweet_perth = ct_attention_covid['Perth (WA)'] / ct_tweet_count['Perth (WA)'] * 1000
    covid_tweet_adelaide = ct_attention_covid['Adelaide'] / ct_tweet_count['Adelaide'] * 1000
    # number of covid related tweet per 1000 tweet in different cities
    covid_tweet_in_ct = {'Sydney': covid_tweet_syd, 'Melbourne': covid_tweet_melb, 'Brisbane': covid_tweet_brisbane,
                         'Perth (WA)': covid_tweet_perth, 'Adelaide': covid_tweet_adelaide}

    covid_data = pd.read_csv("covid_data.csv")
    # The number of people who is/was infected within 100 people in this state.
    covid_data['Infection_rate'] = covid_data['Total cases'] / covid_data['Population(state)'] * 100

    # The number of people who die for covid within 100 infected people in this state.
    covid_data['Death_rate'] = covid_data['Total lives lost'] / covid_data['Total cases'] * 100

    # The number of people who complete 2 doese vaccination within 100 people in this state.
    covid_data['Vaccine complete'] = covid_data['Total doses administered(until 2021-05-15)'] / covid_data[
        'Total doses needed'] * 100

    try:
        server.create("scenario_1")
    except couchdb.http.PreconditionFailed:
        pass

    scenario_1_db = server['scenario_1']
    try:
        scenario_1_db['ct_attention_covid'] = ct_attention_covid
    except couchdb.http.ResourceConflict:
        scenario_1_db.delete(scenario_1_db['ct_attention_covid'])
        scenario_1_db['ct_attention_covid'] = ct_attention_covid
    try:
        scenario_1_db['covid_tweet_in_ct'] = covid_tweet_in_ct
    except couchdb.http.ResourceConflict:
        scenario_1_db.delete(scenario_1_db['covid_tweet_in_ct'])
        scenario_1_db['covid_tweet_in_ct'] = covid_tweet_in_ct
    try:
        scenario_1_db['covid_data'] = covid_data.to_dict()
    except couchdb.http.ResourceConflict:
        scenario_1_db.delete(scenario_1_db['covid_data'])
        scenario_1_db['covid_data'] = covid_data.to_dict()

    print('Scenario 1 finished')
    '''
    Scenario 2: People's twetting behaviours.
    Output:
    num_tweet_ct: tweets count for every city
    text_len_ct： tweets length for every city
    word_count_ct: tweets average words for every city
    time_of_tweet: tweet number counts for every hour
    text_len_at_different_time: tweet average length for every hour
    text_word_count_at_different_time: tweet word counts for every hour
    text_word_count_at_different_day: tweet word counts for days of week
    text_len_at_different_day: tweet length for days of week
    
    '''
    num_tweet_syd = int(ct_tweet_count['Sydney'])
    num_tweet_melb = int(ct_tweet_count['Melbourne'])
    num_tweet_brisbane = int(ct_tweet_count['Brisbane'])
    num_tweet_perth = int(ct_tweet_count['Perth (WA)'])
    num_tweet_adelaide = int(ct_tweet_count['Adelaide'])
    num_tweet_ct = {'Sydney': num_tweet_syd, 'Melbourne': num_tweet_melb, 'Brisbane': num_tweet_brisbane,
                    'Perth (WA)': num_tweet_perth, 'Adelaide': num_tweet_adelaide}


    population = covid_data['Population(greater capital city)']
    num_tweet_syd = ct_tweet_count['Sydney'] / population[0] * 1000
    num_tweet_melb = ct_tweet_count['Melbourne'] / population[1] * 1000
    num_tweet_brisbane = ct_tweet_count['Brisbane'] / population[2] * 1000
    num_tweet_perth = ct_tweet_count['Perth (WA)'] / population[3] * 1000
    num_tweet_adelaide = ct_tweet_count['Adelaide'] / population[4] * 1000
    num_tweet_ct_1000 = {'Sydney': num_tweet_syd, 'Melbourne': num_tweet_melb, 'Brisbane': num_tweet_brisbane,
                    'Perth (WA)': num_tweet_perth, 'Adelaide': num_tweet_adelaide}

    tweet['text_len'] = tweet['text'].str.len()
    tweet_text_len = tweet.groupby(['city'])['text_len'].sum()
    text_len_syd = tweet_text_len['Sydney'] / ct_tweet_count['Sydney']
    text_len_melb = tweet_text_len['Melbourne'] / ct_tweet_count['Melbourne']
    text_len_brisbane = tweet_text_len['Brisbane'] / ct_tweet_count['Brisbane']
    text_len_perth = tweet_text_len['Perth (WA)'] / ct_tweet_count['Perth (WA)']
    text_len_adelaide = tweet_text_len['Adelaide'] / ct_tweet_count['Adelaide']
    text_len_ct = {'Sydney': text_len_syd, 'Melbourne': text_len_melb, 'Brisbane': text_len_brisbane,
                   'Perth (WA)': text_len_perth, 'Adelaide': text_len_adelaide}

    tweet['text_word_count'] = tweet['text'].str.count(' ') + 1
    tweet_word_count = tweet.groupby(['city'])['text_word_count'].sum()
    word_count_syd = tweet_word_count['Sydney']/ct_tweet_count['Sydney']
    word_count_melb = tweet_word_count['Melbourne']/ct_tweet_count['Melbourne']
    word_count_brisbane = tweet_word_count['Brisbane']/ct_tweet_count['Brisbane']
    word_count_perth = tweet_word_count['Perth (WA)']/ct_tweet_count['Perth (WA)']
    word_count_adelaide = tweet_word_count['Adelaide']/ct_tweet_count['Adelaide']
    word_count_ct = {'Sydney': word_count_syd, 'Melbourne':word_count_melb ,'Brisbane':word_count_brisbane,
                     'Perth (WA)':word_count_perth, 'Adelaide':word_count_adelaide}

    # outputs
    time_of_tweet = tweet.groupby(['city','time_of_tweet']).size()
    # text_len_at_different_time = tweet.groupby(['city', 'time_of_tweet'])['text_len'].describe()[['count', 'mean']]
    text_word_count_at_different_time = tweet.groupby(['city', 'time_of_tweet'])['text_word_count'].describe()[['count', 'mean']]
    day_of_week = tweet.groupby(['city', 'day_of_week']).size()
    text_word_count_at_different_day = tweet.groupby(['city', 'day_of_week'])['text_word_count'].describe()[['count', 'mean']]
    # text_len_at_different_day = tweet.groupby(['city', 'day_of_week'])['text_len'].describe()[['count','mean']]

    try:
        server.create("scenario_2")
    except couchdb.http.PreconditionFailed:
        pass


    scenario_2_db = server['scenario_2']



    try:
        scenario_2_db['num_tweet_ct'] = num_tweet_ct
    except couchdb.http.ResourceConflict:
        scenario_2_db.delete(scenario_2_db['num_tweet_ct'])
        scenario_2_db['num_tweet_ct'] = num_tweet_ct

    try:
        scenario_2_db['num_tweet_ct_per_1000'] = num_tweet_ct_1000
    except couchdb.http.ResourceConflict:
        scenario_2_db.delete(scenario_2_db['num_tweet_ct_per_1000'])
        scenario_2_db['num_tweet_ct_per_1000'] = num_tweet_ct_1000

    try:
        scenario_2_db['word_count_ct'] = word_count_ct
    except couchdb.http.ResourceConflict:
        scenario_2_db.delete(scenario_2_db['word_count_ct'])
        scenario_2_db['word_count_ct'] = word_count_ct
    for c in city:
        try:
            scenario_2_db['time_of_tweet' + ' ' + c] = time_of_tweet[c].to_dict()
        except couchdb.http.ResourceConflict:
            scenario_2_db.delete(scenario_2_db['time_of_tweet' + ' ' + c])
            scenario_2_db['time_of_tweet' + ' ' + c] = time_of_tweet[c].to_dict()

        try:
            scenario_2_db['text_word_count_at_different_time' + ' ' + c] = text_word_count_at_different_time.loc[c].to_dict()
        except couchdb.http.ResourceConflict:
            scenario_2_db.delete(scenario_2_db['text_word_count_at_different_time' + ' ' + c])
            scenario_2_db['text_word_count_at_different_time' + ' ' + c] = text_word_count_at_different_time.loc[c].to_dict()

        try:
            scenario_2_db['day_of_week' + ' ' + c] = day_of_week.loc[c].to_dict()
        except couchdb.http.ResourceConflict:
            scenario_2_db.delete(scenario_2_db['day_of_week' + ' ' + c])
            scenario_2_db['day_of_week' + ' ' + c] = day_of_week.loc[c].to_dict()

        try:
            scenario_2_db['text_word_count_at_different_day' + ' ' + c] = text_word_count_at_different_day.loc[c].to_dict()
        except couchdb.http.ResourceConflict:
            scenario_2_db.delete(scenario_2_db['text_word_count_at_different_day' + ' ' + c])
            scenario_2_db['text_word_count_at_different_day' + ' ' + c] = text_word_count_at_different_day.loc[c].to_dict()

    print('Scenario 2 finished')


    '''
    Scenario 3: Find the happiest city by sentiment analysis
    
    Output
    '''
    
    Sydney_index_lst = tweet[tweet['city'] == 'Sydney'].sample(2000).index
    Adelaide_index_lst = tweet[tweet['city'] == 'Adelaide'].sample(2000).index
    Brisbane_index_lst = tweet[tweet['city'] == 'Brisbane'].sample(2000).index
    Melbourne_index_lst = tweet[tweet['city'] == 'Melbourne'].sample(2000).index
    Perth_index_lst = tweet[tweet['city'] == 'Perth (WA)'].sample(2000).index

    text_sentiment_Sydney = pd.DataFrame()
    text_sentiment_Sydney['text_sentiment'] = tweet.iloc[Sydney_index_lst, 4].apply(te.get_emotion)
    text_sentiment_Sydney = text_sentiment_Sydney['text_sentiment'].apply(pd.Series)

    text_sentiment_Adelaide = pd.DataFrame()
    text_sentiment_Adelaide['text_sentiment'] = tweet.iloc[Adelaide_index_lst, 4].apply(te.get_emotion)
    text_sentiment_Adelaide = text_sentiment_Adelaide['text_sentiment'].apply(pd.Series)

    text_sentiment_Brisbane = pd.DataFrame()
    text_sentiment_Brisbane['text_sentiment'] = tweet.iloc[Brisbane_index_lst, 4].apply(te.get_emotion)
    text_sentiment_Brisbane = text_sentiment_Brisbane['text_sentiment'].apply(pd.Series)

    text_sentiment_Melbourne = pd.DataFrame()
    text_sentiment_Melbourne['text_sentiment'] = tweet.iloc[Melbourne_index_lst, 4].apply(te.get_emotion)
    text_sentiment_Melbourne = text_sentiment_Melbourne['text_sentiment'].apply(pd.Series)

    text_sentiment_Perth = pd.DataFrame()
    text_sentiment_Perth['text_sentiment'] = tweet.iloc[Perth_index_lst, 4].apply(te.get_emotion)
    text_sentiment_Perth = text_sentiment_Perth['text_sentiment'].apply(pd.Series)

    try:
        server.create("scenario_3")
    except couchdb.http.PreconditionFailed:
        pass

    scenario_3_db = server['scenario_3']

    try:
        scenario_3_db['text_sentiment_Sydney'] = text_sentiment_Sydney.describe().to_dict()
    except couchdb.http.ResourceConflict:
        scenario_3_db.delete(scenario_3_db['text_sentiment_Sydney'])
        scenario_3_db['text_sentiment_Sydney'] = text_sentiment_Sydney.describe().to_dict()

    try:
        scenario_3_db['text_sentiment_Adelaide'] = text_sentiment_Adelaide.describe().to_dict()
    except couchdb.http.ResourceConflict:
        scenario_3_db.delete(scenario_3_db['text_sentiment_Adelaide'])
        scenario_3_db['text_sentiment_Adelaide'] = text_sentiment_Adelaide.describe().to_dict()

    try:
        scenario_3_db['text_sentiment_Brisbane'] = text_sentiment_Brisbane.describe().to_dict()
    except couchdb.http.ResourceConflict:
        scenario_3_db.delete(scenario_3_db['text_sentiment_Brisbane'])
        scenario_3_db['text_sentiment_Brisbane'] = text_sentiment_Brisbane.describe().to_dict()

    try:
        scenario_3_db['text_sentiment_Melbourne'] = text_sentiment_Melbourne.describe().to_dict()
    except couchdb.http.ResourceConflict:
        scenario_3_db.delete(scenario_3_db['text_sentiment_Melbourne'])
        scenario_3_db['text_sentiment_Melbourne'] = text_sentiment_Melbourne.describe().to_dict()

    try:
        scenario_3_db['text_sentiment_Perth'] = text_sentiment_Perth.describe().to_dict()
    except couchdb.http.ResourceConflict:
        scenario_3_db.delete(scenario_3_db['text_sentiment_Perth'])
        scenario_3_db['text_sentiment_Perth'] = text_sentiment_Perth.describe().to_dict()

    print('Scenario 3 finished')
    '''
    Scenario 4: Does COVID-19 influence the labour market and people's emotion?
    
    Output
    '''

    labour_market_2018 = pd.read_csv("Labour Market 2018.csv")
    labour_market_2020 = pd.read_csv("Labour Market 2020.csv")
    change_in_unemployment_rate = (labour_market_2020['unemployment_rate(15+)']-labour_market_2018['unemployment_rate(15+)'])/labour_market_2018['unemployment_rate(15+)']
    change_in_youth_employment_rate = (labour_market_2020['youth_employment_rate_15_24']-labour_market_2018['youth_employment_rate_15_24'])/labour_market_2018['youth_employment_rate_15_24']

    try:
        server.create("scenario_4")
    except couchdb.http.PreconditionFailed:
        pass
    scenario_4_db = server['scenario_4']

    try:
        scenario_4_db['change_in_unemployment_rate'] = change_in_unemployment_rate.to_dict()
    except couchdb.http.ResourceConflict:
        scenario_4_db.delete(scenario_4_db['change_in_unemployment_rate'])
        scenario_4_db['change_in_unemployment_rate'] = change_in_unemployment_rate.to_dict()

    try:
        scenario_4_db['change_in_youth_employment_rate'] = change_in_youth_employment_rate.to_dict()
    except couchdb.http.ResourceConflict:
        scenario_4_db.delete(scenario_4_db['change_in_youth_employment_rate'])
        scenario_4_db['change_in_youth_employment_rate'] = change_in_youth_employment_rate.to_dict()

    print('Scenario 4 finished')

    try:
        server.create("update_log")
    except couchdb.http.PreconditionFailed:
        pass
    log_db = server['update_log']
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    try:
        log_db['update_time'] = {'time': dt_string}
    except couchdb.http.ResourceConflict:
        log_db.delete(log_db['update_time'])
        log_db['update_time'] = {'time': dt_string}


    print(f'data update finished {dt_string}')

# run every 30 minutes
if __name__ == '__main__':
    run()
    time.sleep(60*30)