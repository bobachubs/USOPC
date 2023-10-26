import pandas as pd
import numpy as np
import random
import statistics

# How would your recommended team differ if you are trying to maximize total medal count, gold medals, or a weighted medal count?
# First total

# preprocessing
data = pd.read_csv("data_2022_2023.csv")
# print(data.head())

# join first and last names

data['LastName'] = data['LastName'].str.lower().str.capitalize()
data['FullName'] = data['FirstName'] + ' ' + data['LastName']
data = data.dropna(subset=['FullName', 'Score'])
data = data[['Gender', 'Country', 'Round', 'Apparatus', 'Rank', 'Score', 'FullName']]

print(data[(data["Round"]=="qual") & (data["Gender"] == 'w')]["Apparatus"].unique())

# VT1 or VT2, higher one taken
def simulate_individual(data, gender, athlete_combo):
    if gender == 'w':
        apps = ['FX', 'BB', 'UB', 'VT1', 'VT2']
        data = data[data['Gender'] == 'w']
    else:
        apps = ['FX', 'PH', 'PB', 'HB', 'SR', 'VT1', 'VT2']
        data = data[data['Gender'] == 'm']

    app_medals = dict()

    # all athletes qualify for now
    data['Include'] = np.ones(len(data)).astype(int)

    app_dict = dict()
    # for each apparatus
    for app in apps:
        data_copy = data.copy()
        app_dict[app] = dict()

        # for each round
        for round in ['qual', 'final']:
            # print(round)

            app_dict[app][round] = dict()
            round_data = data_copy[(data_copy['Round'] == round) & (data_copy['Include'] == 1)]
            # print(len(round_data["FullName"].unique()))

            # for each athlete competing in this apparatus round
            # consider weighting by country's distribution vs own distribution?
            for athlete in round_data['FullName'].unique():
                # print(athlete, app, round)
                athlete_app_round_data = round_data[(round_data['FullName'] == athlete) & (round_data['Apparatus'] == app)]
                if athlete_app_round_data.empty:
                    # draw from country's distribution if no data exists
                    athlete_country = round_data[(round_data["FullName"] == athlete)]["Country"].iloc[0]
                    country_app_data = round_data[(round_data["Country"] == athlete_country) & (round_data['Apparatus'] == app)]
                    if len(country_app_data) > 0: 
                        athlete_app_round_score = sample_history(country_app_data["Score"])
                    else:
                        athlete_app_round_score = 0
                elif len(athlete_app_round_data) == 1:
                    athlete_app_round_score = athlete_app_round_data['Score'].iloc[0]
                else:
                    athlete_app_round_score = sample_history(athlete_app_round_data['Score'])
                    
                app_dict[app][round][athlete] = athlete_app_round_score

            if round == "qual":
                app_scores = sorted(app_dict[app][round].items(), key=lambda item: item[1], reverse=True)[:8]
                athlete_pass = [athlete for (athlete, _) in app_scores]
                data_copy.loc[~data_copy['FullName'].isin(athlete_pass), 'Include'] = 0
                # print(data_copy[data_copy["Include"] == 1]["FullName"].unique())
                # print(app, app_scores)
            if round == "final":
                app_scores = sorted(app_dict[app][round].items(), key=lambda item: item[1], reverse=True)[:3]
                # athlete_pass = [athlete for (athlete, _) in app_scores]
                # data_copy.loc[~data_copy['FullName'].isin(athlete_pass), 'Include'] = 0
                app_scores_country = [(t[0], t[1], (round_data[round_data["FullName"] == t[0]]["Country"].iloc[0])) for t in app_scores]
                app_medals[app] = app_scores_country
                # print(app, app_scores)
    return app_medals
    # return count_medals(app_medals, athlete_combo)


def sample_history(athlete_data):
    past_scores = list(athlete_data)
    n = 1000
    samples = random.choices(past_scores, k=n)
    return statistics.mean(samples)

# how many medals? or which medals
# def count_medals(app_medals, athlete_combo):
#     print(app_medals)
#     total_medals = 0
#     merged_winners = [winner[0] for app in app_medals.values() for winner in app]
#     for athlete in athlete_combo:
#         total_medals += merged_winners.count(athlete)
#     # return f"{athlete_combo}: {total_medals} medals"
#     return total_medals

# print(country_medals)

print(simulate_individual(data, 'w', None))

# print(data[data['FullName'] == 'Dildora Aripova'])

# print(data[(data["Apparatus"] == "VT1") & (data["Round"]=="final")])

