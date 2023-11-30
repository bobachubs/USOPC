import pandas as pd
import numpy as np
import random
import statistics
from itertools import combinations

# How would your recommended team differ if you are trying to maximize total medal count, gold medals, or a weighted medal count?
# First total

# preprocessing
data = pd.read_csv("data_2022_2023.csv")
# print(len(data))
# print(data.head())
# '2022 51st FIG Artistic Gymnastics World Championships'
# '2023 52nd FIG Artistic Gymnastics World Championships'

# join first and last names


data['LastName'] = data['LastName'].str.lower().str.capitalize()
data['FullName'] = data['FirstName'] + ' ' + data['LastName']
data.replace("Melanie De jesus dos santos", "Melanie Jesus santos", inplace=True)

(data['Competition'] == '2022 51st FIG Artistic Gymnastics World Championships')
world_data = data[(data['Competition'] == '2023 52nd FIG Artistic Gymnastics World Championships')]
qual_countries_w = ['CHN', 'BRA', 'ITA', 'NED', 'FRA', 'JPN', 'AUS', 'ROU', 'KOR', 'USA', 'GBR', 'CAN']
qual_countries_m = ['USA', 'CHN', 'GBR', 'GER', 'JPN', 'BRA', 'ITA', 'CAN', 'SUI', 'ESP', 'TUR', 'NED']

qual_athletes_w = []
qual_athletes_m = []
for c in qual_countries_w:
    athletes = world_data[(world_data["Country"]==c) & (world_data["Gender"] == 'w')]['FullName'].unique()
    if len(athletes) > 5: 
        athletes_scores = world_data[(world_data["Country"]==c) & (world_data["Gender"] == 'w')]
        athletes = athletes_scores.groupby('FullName')['Score'].mean().nlargest(5).index
        # print(athletes)
    qual_athletes_w += list(athletes)

for c in qual_countries_m:
    athletes = world_data[(world_data["Country"]==c) & (world_data["Gender"] == 'm')]['FullName'].unique()
    if len(athletes) > 5: 
        athletes_scores = world_data[(world_data["Country"]==c) & (world_data["Gender"] == 'm')]
        athletes = athletes_scores.groupby('FullName')['Score'].mean().nlargest(5).index
        # print(athletes)
    qual_athletes_m += list(athletes)

print(qual_athletes_w)
print(qual_athletes_m)

data = data.dropna(subset=['FullName', 'Score'])
data = data[['Gender', 'Country', 'Round', 'Apparatus', 'Rank', 'Score', 'FullName']]

data = data.drop_duplicates()
# print(data[(data["Round"]=="qual") & (data["Gender"] == 'w')]["Apparatus"].unique())

qual_data = data[(data["FullName"].isin(qual_athletes_w) | 
                  data["FullName"].isin(qual_athletes_m))]

# now the mutually exclusive set of data exclusing qualifying teams for simulating remaining 36 for each gender

rem_data = data[((~data["FullName"].isin(qual_athletes_w)) & 
                 (~data["FullName"].isin(qual_athletes_m)) & 
                  (data["Country"] != 'USA'))]

us_data = data[(data["Country"] == 'USA')]


def sample_history(athlete_data, n):
    past_scores = list(athlete_data)
    samples = random.choices(past_scores, k=n)
    return statistics.mean(samples)

# get the top 10 most likely candidates given a Country by taking the average median of their likely apparatus scores
# question: 
# def get_candidates(data, gender, Country):
#     athlete_scores = dict()
#     data = data[(data['Gender'] == gender) & (data["Country"] == Country)]
#     athletes = data['FullName'].unique()
#     apps = data['Apparatus'].unique()
#     for athlete in athletes:
#         athlete_scores[athlete] = dict()
#         for app in apps:
#             app_data = data[(data["Apparatus"] == app) & (data["FullName"] == athlete)]
#             if app_data.empty:
#                 # draw from country's distribution if no data exists
#                 athlete_country = data[(data["FullName"] == athlete)]["Country"].iloc[0]
#                 country_app_data = data[(data["Country"] == athlete_country) & (data['Apparatus'] == app)]
#                 if len(country_app_data) > 0: 
#                     app_score = sample_history(country_app_data["Score"], 100)
#             elif len(app_data) == 1:
#                 app_score = app_data['Score'].iloc[0]
#             else:
#                 app_score = statistics.median(app_data["Score"])
#             athlete_scores[athlete][app] = app_score
    
#     athlete_avg_scores = dict()
#     for athlete, app in athlete_scores.items():
#         avg_score = sum(app.values())/len(app)
#         athlete_avg_scores[athlete] = avg_score
    
#     top_ten = sorted(athlete_avg_scores.items(), key=lambda x: x[1], reverse=True)[:10]

#     return [athlete for athlete,_ in top_ten]

# top_candidates_w = []
# for country in data["Country"].unique():
#     top_candidates_w += get_candidates(data, 'w', country)

# VT1 or VT2, higher one taken
# TODO: take 4/5
def simulate_individual(data, gender, us_candidates):
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
                        athlete_app_round_score = sample_history(country_app_data["Score"], 1)
                    else:
                        athlete_app_round_score = 0
                elif len(athlete_app_round_data) == 1:
                    athlete_app_round_score = athlete_app_round_data['Score'].iloc[0]
                else:
                    athlete_app_round_score = sample_history(athlete_app_round_data['Score'], 1)
                    
                app_dict[app][round][athlete] = athlete_app_round_score

            if round == "qual":
                # sum VT1 and VT2 if individual apparatus for qual
                if app == 'VT1': continue
                if app == 'VT2':
                    app_dict['VT'] = dict()
                    app_dict['VT'][round] = dict()
                    for athlete in app_dict['VT2'][round]:
                        vt1_score = app_dict['VT1'][round][athlete]
                        vt2_score = app_dict['VT2'][round][athlete]
                        app_dict['VT'][round][athlete] = vt1_score + vt2_score
                    del app_dict['VT1']
                    del app_dict['VT2']
                    app = 'VT'
                app_scores = sorted(app_dict[app][round].items(), key=lambda item: item[1], reverse=True)[:8]
                athlete_pass = [athlete for (athlete, _) in app_scores]
                data_copy.loc[~data_copy['FullName'].isin(athlete_pass), 'Include'] = 0
                # print(data_copy[data_copy["Include"] == 1]["FullName"].unique())
                # print(app, app_scores)
            if round == "final":
                # TODO: max 2 per country, break ties (off chance everyone ties for the same place, break by difficulty then execution)
                if app == 'VT1': continue
                app_scores = sorted(app_dict[app][round].items(), key=lambda item: item[1], reverse=True)[:3]
                # athlete_pass = [athlete for (athlete, _) in app_scores]
                # data_copy.loc[~data_copy['FullName'].isin(athlete_pass), 'Include'] = 0
                app_scores_country = [(t[0], t[1], (round_data[round_data["FullName"] == t[0]]["Country"].iloc[0])) for t in app_scores]
                app_medals[app] = app_scores_country
                # print(app, app_scores)
    return app_medals
    return count_medals(app_medals, athlete_combo)


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

# athlete_candidates_women = get_candidates(data, 'w', 'USA')

# print(list(combinations(athlete_candidates_women, 5)))

print(simulate_individual(data, 'w', None))

# print(data[data['FullName'] == 'Dildora Aripova'])

# print(data[(data["Apparatus"] == "VT1") & (data["Round"]=="final")])
