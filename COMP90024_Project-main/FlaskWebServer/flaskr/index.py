# Part of COMP90024 Project Team members are
# Ziyuan Xiao (940448)
# Pengyu Mu(890756)
# Dechao Sun (980546)
# Seehoi Chow(980301)
# Yuexin Li (959634)

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.fetchCouchDB import get_db
DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
HOURS = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17',
         '18', '19', '20', '21', '22', '23']

CITIES = ["Sydney",
          "Melbourne",
          "Brisbane",
          "Perth (WA)",
          "Adelaide"]

bp = Blueprint('main', __name__, url_prefix='/main')

@bp.route('/index', methods=['GET', 'POST'])
def index():
    welcome_db = get_db('scenario_1')
    log_db = get_db('update_log')
    covid_data = welcome_db['covid_data']
    state_population = []
    for city,population in zip(covid_data['Unnamed: 0'].values(), covid_data['Population(state)'].values()):
        state_population.append({'id': city, 'value':str(population)})
    data = {
        'state_population': state_population,
        'update_time': log_db['update_time']['time']
    }
    return render_template('index.html', data=data)


@bp.route('/welcome_page', methods=['GET', 'POST'])
def welcome_page():
    welcome_db = get_db('scenario_1')
    covid_data = welcome_db['covid_data']
    log_db = get_db('update_log')
    data = {
        'state_name': list(covid_data['Unnamed: 0']),
        'population': list(covid_data['Population(state)']),
        'update_time': log_db['update_time']['time']
    }

    return render_template('welcome-Page.html', data=data)


@bp.route('/scenario_1', methods=['GET', 'POST'])
def scenario_1():
    scenario_1_db = get_db('scenario_1')
    # Total number of tweet mentioned COVID-19.
    tweet_mentions = scenario_1_db['ct_attention_covid']
    tweet_mentions_per_1000 = scenario_1_db['covid_tweet_in_ct']
    covid_data = scenario_1_db['covid_data']
    tweet_mentions_per_1000_value = list(tweet_mentions_per_1000.values())[2:]
    tweet_mentions_per_1000_value = [round(value, 2) for value in tweet_mentions_per_1000_value]
    infection_100_key = list(covid_data['gcc_name'].values())
    infection_100_value = list(covid_data['Infection_rate'].values())
    infection_100_value = [round(value, 2) for value in infection_100_value]
    vaccination_100_value = list(covid_data['Vaccine complete'].values())
    vaccination_100_value = [round(value, 2) for value in vaccination_100_value]

    data = {
        'tweet_mentions_key': list(tweet_mentions.keys())[2:],
        'tweet_mentions_value': list(tweet_mentions.values())[2:],

        'tweet_mentions_per_1000_key': list(tweet_mentions_per_1000.keys())[2:],
        'tweet_mentions_per_1000_value': tweet_mentions_per_1000_value,

        'infection_100_key': infection_100_key,
        'infection_100_value': infection_100_value,

        'vaccination_100_key': infection_100_key,
        'vaccination_100_value': vaccination_100_value
    }
    return render_template('Scenario-1.html', data=data)


@bp.route('/scenario_2', methods=['GET', 'POST'])
def scenario_2():
    covid_db = get_db('scenario_1')
    covid_data = covid_db['covid_data']
    scenario_2_db = get_db('scenario_2')
    num_tweet_ct = scenario_2_db['num_tweet_ct']

    def days_extraction(days_dict):
        res = []
        for day in DAYS:
            if day in days_dict:
                res.append(days_dict[day])
            else:
                res.append(0)
        return res

    def hour_extraction(hour_dict):
        res = []
        for hour in HOURS:
            if hour in hour_dict:
                res.append(hour_dict[hour])
            else:
                res.append(0)
        return res


    Melbourne_tweet_days = scenario_2_db['day_of_week Melbourne']
    Melbourne_tweet_days = days_extraction(Melbourne_tweet_days)

    Sydney_tweet_days = scenario_2_db['day_of_week Sydney']
    Sydney_tweet_days = days_extraction(Sydney_tweet_days)

    Brisbane_tweet_days = scenario_2_db['day_of_week Brisbane']
    Brisbane_tweet_days = days_extraction(Brisbane_tweet_days)

    Adelaide_tweet_days = scenario_2_db['day_of_week Adelaide']
    Adelaide_tweet_days = days_extraction(Adelaide_tweet_days)

    Perth_tweet_days = scenario_2_db['day_of_week Perth (WA)']
    Perth_tweet_days = days_extraction(Perth_tweet_days)

    Melbourne_tweet_hours = scenario_2_db['time_of_tweet Melbourne']
    Melbourne_tweet_hours = hour_extraction(Melbourne_tweet_hours)

    Sydney_tweet_hours = scenario_2_db['time_of_tweet Sydney']
    Sydney_tweet_hours = hour_extraction(Sydney_tweet_hours)

    Brisbane_tweet_hours = scenario_2_db['time_of_tweet Brisbane']
    Brisbane_tweet_hours = hour_extraction(Brisbane_tweet_hours)

    Adelaide_tweet_hours = scenario_2_db['time_of_tweet Adelaide']
    Adelaide_tweet_hours = hour_extraction(Adelaide_tweet_hours)

    Perth_tweet_hours = scenario_2_db['time_of_tweet Perth (WA)']
    Perth_tweet_hours = hour_extraction(Perth_tweet_hours)

    Melbourne_tweet_words_days = scenario_2_db['text_word_count_at_different_day Melbourne']['mean']
    Melbourne_tweet_words_days = days_extraction(Melbourne_tweet_words_days)
    Melbourne_tweet_words_days = [round(value, 2) for value in Melbourne_tweet_words_days]

    Sydney_tweet_words_days = scenario_2_db['text_word_count_at_different_day Sydney']['mean']
    Sydney_tweet_words_days = days_extraction(Sydney_tweet_words_days)
    Sydney_tweet_words_days = [round(value, 2) for value in Sydney_tweet_words_days]

    Brisbane_tweet_words_days = scenario_2_db['text_word_count_at_different_day Brisbane']['mean']
    Brisbane_tweet_words_days = days_extraction(Brisbane_tweet_words_days)
    Brisbane_tweet_words_days = [round(value, 2) for value in Brisbane_tweet_words_days]

    Adelaide_tweet_words_days = scenario_2_db['text_word_count_at_different_day Adelaide']['mean']
    Adelaide_tweet_words_days = days_extraction(Adelaide_tweet_words_days)
    Adelaide_tweet_words_days = [round(value, 2) for value in Adelaide_tweet_words_days]

    Perth_tweet_words_days = scenario_2_db['text_word_count_at_different_day Perth (WA)']['mean']
    Perth_tweet_words_days = days_extraction(Perth_tweet_words_days)
    Perth_tweet_words_days = [round(value, 2) for value in Perth_tweet_words_days]


    Melbourne_tweet_words_hours = scenario_2_db['text_word_count_at_different_time Melbourne']['mean']
    Melbourne_tweet_words_hours = hour_extraction(Melbourne_tweet_words_hours)
    Melbourne_tweet_words_hours = [round(value, 2) for value in Melbourne_tweet_words_hours]

    Sydney_tweet_words_hours = scenario_2_db['text_word_count_at_different_time Sydney']['mean']
    Sydney_tweet_words_hours = hour_extraction(Sydney_tweet_words_hours)
    Sydney_tweet_words_hours = [round(value, 2) for value in Sydney_tweet_words_hours]

    Brisbane_tweet_words_hours = scenario_2_db['text_word_count_at_different_time Brisbane']['mean']
    Brisbane_tweet_words_hours = hour_extraction(Brisbane_tweet_words_hours)
    Brisbane_tweet_words_hours = [round(value, 2) for value in Brisbane_tweet_words_hours]

    Adelaide_tweet_words_hours= scenario_2_db['text_word_count_at_different_time Adelaide']['mean']
    Adelaide_tweet_words_hours = hour_extraction(Adelaide_tweet_words_hours)
    Adelaide_tweet_words_hours = [round(value, 2) for value in Adelaide_tweet_words_hours]

    Perth_tweet_words_hours = scenario_2_db['text_word_count_at_different_time Perth (WA)']['mean']
    Perth_tweet_words_hours = hour_extraction(Perth_tweet_words_hours)
    Perth_tweet_words_hours = [round(value, 2) for value in Perth_tweet_words_hours]


    data = {
        'population_city_name': list(covid_data['gcc_name'].values()),
        'population': list(covid_data['Population(state)'].values()),

        'num_tweet_ct_key': list(num_tweet_ct.keys())[2:],
        'num_tweet_ct_value': list(num_tweet_ct.values())[2:],

        'Melbourne_tweet_days': Melbourne_tweet_days,
        'Adelaide_tweet_days': Adelaide_tweet_days,
        'Sydney_tweet_days': Sydney_tweet_days,
        'Brisbane_tweet_days': Brisbane_tweet_days,
        'Perth_tweet_days': Perth_tweet_days,

        'Melbourne_tweet_hours': Melbourne_tweet_hours,
        'Adelaide_tweet_hours': Adelaide_tweet_hours,
        'Sydney_tweet_hours': Sydney_tweet_hours,
        'Brisbane_tweet_hours': Brisbane_tweet_hours,
        'Perth_tweet_hours': Perth_tweet_hours,

        'Melbourne_tweet_words_days': Melbourne_tweet_words_days,
        'Adelaide_tweet_words_days': Adelaide_tweet_words_days,
        'Sydney_tweet_words_days': Sydney_tweet_words_days,
        'Brisbane_tweet_words_days': Brisbane_tweet_words_days,
        'Perth_tweet_words_days': Perth_tweet_words_days,

        'Melbourne_tweet_words_hours': Melbourne_tweet_words_hours,
        'Adelaide_tweet_words_hours': Adelaide_tweet_words_hours,
        'Sydney_tweet_words_hours': Sydney_tweet_words_hours,
        'Brisbane_tweet_words_hours': Brisbane_tweet_words_hours,
        'Perth_tweet_words_hours': Perth_tweet_words_hours,
    }
    return render_template('Scenario-2.html', data=data)


@bp.route('/scenario_3', methods=['GET', 'POST'])
def scenario_3():
    scenario_3_db = get_db('scenario_3')
    table_name = ['text_sentiment_Sydney', 'text_sentiment_Melbourne',
                  'text_sentiment_Brisbane', 'text_sentiment_Perth','text_sentiment_Adelaide',]

    happiness_values = []
    sadness_values = []
    angry_values = []

    for table_name in table_name:
        table = scenario_3_db[table_name]
        happiness_values.append(round(table['Happy']['mean'], 3))
        sadness_values.append(round(table['Sad']['mean'], 3))
        angry_values.append(round(table['Angry']['mean'], 3))
    data = {
        'happiness_values': happiness_values,
        'sadness_values': sadness_values,
        'angry_values': angry_values
    }
    return render_template('Scenario-3.html', data=data)


@bp.route('/scenario_4', methods=['GET', 'POST'])
def scenario_4():
    scenario_4_db = get_db('scenario_4')
    unemployment_value = list(scenario_4_db['change_in_unemployment_rate'].values())[2:]
    unemployment_value_youth = list(scenario_4_db['change_in_youth_employment_rate'].values())[2:]
    data = {
        'unemployment_value': [round(rate * 100, 1) for rate in unemployment_value],
        'unemployment_value_youth': [round(rate * 100, 1) for rate in unemployment_value_youth]

    }
    return render_template('Scenario-4.html', data=data)
