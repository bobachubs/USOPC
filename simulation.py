import pandas as pd
import numpy as np
import random
import statistics
from itertools import combinations

raw_data = pd.read_csv("data_2022_2023.csv")

# Preprocessing
################################################################################################

data = raw_data
data['LastName'] = data['LastName'].str.lower().str.capitalize()
data['FullName'] = data['FirstName'] + ' ' + data['LastName']
data.replace("Melanie De jesus dos santos", "Melanie Jesus santos", inplace=True) #special case

world_data_2023 = data[(data['Competition'] == '2023 52nd FIG Artistic Gymnastics World Championships')]

# qualifying countries from the 51st and 52nd FIG World Champs, exclusing USA
qual_countries_w = ['CHN', 'BRA', 'ITA', 'NED', 'FRA', 'JPN', 'AUS', 'ROU', 'KOR', 'GBR', 'CAN']
qual_countries_m = ['CHN', 'GBR', 'GER', 'JPN', 'BRA', 'ITA', 'CAN', 'SUI', 'ESP', 'TUR', 'NED']

qual_athletes_w = []
qual_athletes_m = []

# getting teams of 5 for the other 11 countries
for c in qual_countries_w:
    athletes = world_data_2023[(world_data_2023["Country"]==c) & (world_data_2023["Gender"] == 'w')]['FullName'].unique()
    if len(athletes) > 4:
        athletes_scores = world_data_2023[(world_data_2023["Country"]==c) & (world_data_2023["Gender"] == 'w')]
        athletes = athletes_scores.groupby('FullName')['Score'].mean().nlargest(4).index
    qual_athletes_w += list(athletes)

for c in qual_countries_m:
    athletes = world_data_2023[(world_data_2023["Country"]==c) & (world_data_2023["Gender"] == 'm')]['FullName'].unique()
    if len(athletes) > 4:
        athletes_scores = world_data_2023[(world_data_2023["Country"]==c) & (world_data_2023["Gender"] == 'm')]
        athletes = athletes_scores.groupby('FullName')['Score'].mean().nlargest(4).index
    qual_athletes_m += list(athletes)

# print(qual_athletes_w, len(qual_athletes_w))
# print(qual_athletes_m, len(qual_athletes_m))

data = data.dropna(subset=['FullName', 'Score'])
data = data[['Gender', 'Country', 'Round', 'Apparatus', 'D_Score', 'E_Score', 'Score', 'FullName']]
data = data.drop_duplicates()

other_country_data = data[(data["FullName"].isin(qual_athletes_w) |
                data["FullName"].isin(qual_athletes_m))]

# now the mutually exclusive set of data excluding qualifying teams for simulating remaining 36 for each gender

rem_data = data[((~data["FullName"].isin(qual_athletes_w)) &
                (~data["FullName"].isin(qual_athletes_m)) &
                (data["Country"] != 'USA'))]

us_data = data[(data["Country"] == 'USA')]

#######################################################################################################################

# sample from an athlete's history n times for an apparatus in a round
def sample_history(data):
    row = data.sample(1)
    score = row['Score'].iloc[0]
    d_score = row['D_Score'].iloc[0]
    e_score = row['E_Score'].iloc[0]
    country = row["Country"].iloc[0]
    # if .isna(country): print(row)
    return (score, d_score, e_score, country)

def get_qual_score(qual_data, athlete, app):
    athlete_app_qual_data = qual_data[(qual_data['FullName'] == athlete) & (qual_data['Apparatus'] == app)]
    # NOTE: athlete_app_round_scores: app_score, d_score, e_score
    if athlete_app_qual_data.empty:
        # draw from country's distribution if no data exists
        athlete_country = qual_data[(qual_data["FullName"] == athlete)]["Country"].iloc[0]
        country_app_data = qual_data[(qual_data["Country"] == athlete_country) & (qual_data['Apparatus'] == app)]
        if len(country_app_data) > 0:
            athlete_app_round_scores = sample_history(country_app_data)
        else:
            athlete_app_round_scores = (0, 0, 0, "None")
    else:
        athlete_app_round_scores = sample_history(athlete_app_qual_data)
    return athlete_app_round_scores

#######################################################################################################################

def sim_qual_indiv_app(qual_data, apps):

    country_data, rem_data, us_data = qual_data
    teams_data = pd.concat([country_data, us_data])

    app_dict = dict()
    app_medals = dict()
    
    athletes_VT1 = []
    for app in apps:
        app_dict[app] = dict()
        for athlete in teams_data["FullName"].unique():
            app_dict[app][athlete] = get_qual_score(teams_data, athlete, app)
    
        athlete_36 = np.random.choice(rem_data["FullName"].unique(), 36)
        for i in range(36):
            athlete = athlete_36[i]
            if app == 'VT1':
                athletes_VT1.append(athlete)
            if app == 'VT2':
                app_dict[app][athletes_VT1[i]] = get_qual_score(rem_data, athletes_VT1[i], app)
            else:
                app_dict[app][athlete] = get_qual_score(rem_data, athlete, app)
            if app == 'VT1': continue
            if app == 'VT2':
                app_dict['VT'] = dict()
                for athlete in app_dict['VT2']:
                    vt1_score, d1_score, e1_score, country = app_dict['VT1'][athlete]
                    vt2_score, d2_score, e2_score, country = app_dict['VT2'][athlete]
                    app_dict['VT'][athlete] = (vt1_score+vt2_score, d1_score+d2_score, e1_score+e2_score, country)
                del app_dict['VT1']
                del app_dict['VT2']
                app = 'VT'
        app_scores = sorted(app_dict[app].items(), key=lambda item: item[1][0], reverse=True)[:8]
        # do tie stuff and max 2/country given sorted list of scores
        # {'FX': {'Ondine Achampong': (12.666, 5.3, 7.566, 'GBR'), 'Rebeca Andrade': (14.033, 6.1, 7.933, 'BRA')}, 'UB': {'Urara Ashikawa': (12.666, 4.5, 8.166, 'JPN'), 'Anonymous12': (9.433, 4.2, 5.733, 'FIN')}}

        #SHIVANI DO TIE STUFF HERE

        app_scores_dict = dict()
        for athlete, scores in app_scores:
            app_scores_dict[athlete] = {"Score": scores[0],
                                        "D_Score": scores[1],
                                        "E_Score": scores[2],
                                        "Country": scores[3]}
        app_medals[app] = app_scores_dict
    return app_medals

#######################################################################################################################
# simulate Individual AA
# sum scores across apparatus, top 24 qualify
def sim_qual_indiv_AA(qual_data, apps):

    country_data, rem_data, us_data = qual_data
    teams_data = pd.concat([country_data, us_data])

    athlete_dict = dict()
    app_medals = dict()

    for athlete in teams_data["FullName"].unique():
        athlete_dict[athlete] = dict()
        for app in apps:
            score, e_score, d_score, country = get_qual_score(teams_data, athlete, app)
            athlete_dict[athlete][app] = {'Score': score,
                                            "E_Score": e_score,
                                            "D_Score": d_score,
                                            "Country": country}


    athletes_36 = np.random.choice(rem_data["FullName"].unique(), 36)
    for athlete in athletes_36:
        athlete_dict[athlete] = dict()
        for app in apps:
            score, e_score, d_score, country = get_qual_score(rem_data, athlete, app)
            athlete_dict[athlete][app] = {'Score': score,
                                            "E_Score": e_score,
                                            "D_Score": d_score,
                                            "Country": country}
                                    
    athlete_scores_sum = dict()
    for athlete, scores in athlete_dict.items():
        total_scores = {'Score': 0,
                        'E_Score': 0,
                        'D_Score': 0,
                        'Country': athlete_dict[athlete]['FX']['Country']}
        for app, app_scores in scores.items():
            total_scores['Score'] += app_scores['Score']
            total_scores['E_Score'] += app_scores['E_Score']
            total_scores['D_Score'] += app_scores['D_Score']

        athlete_scores_sum[athlete] = total_scores

    top_24 = sorted(athlete_scores_sum.items(), key=lambda item: item[1]['Score'], reverse=True)[:24]
    return top_24

#######################################################################################################################
# The top 8 teams in advance based on the sum of the top 3 out of 4 scores on each apparatus
def sim_qual_team_AA(qual_data, apps):

    country_data, us_data = qual_data
    teams_data = pd.concat([country_data, us_data])

    team_dict = dict()
    app_medals = dict()

    for country in teams_data["Country"].unique():
        team_dict[country] = dict()
        team_data = teams_data[teams_data["Country"] == country]
    for athlete in team_data["FullName"].unique():
        team_dict[country][athlete] = dict()
    for app in apps:
        score, e_score, d_score, country = get_qual_score(country_data, athlete, app)
        team_dict[country][athlete][app] = {'Score': score,
                                        "E_Score": e_score,
                                        "D_Score": d_score,
                                        "Country": country}


                                    
    country_scores_sum = dict()
    for athlete, scores in team_dict.items():
        total_scores = {'Score': 0,
                        'E_Score': 0,
                        'D_Score': 0,
                        'Country': team_dict[athlete]['FX']['Country']}
        for app, app_scores in scores.items():
            total_scores['Score'] += app_scores['Score']
            total_scores['E_Score'] += app_scores['E_Score']
            total_scores['D_Score'] += app_scores['D_Score']

        # athlete_scores_sum[athlete] = total_scores

#   top_24 = sorted(athlete_scores_sum.items(), key=lambda item: item[1]['Score'], reverse=True)[:24]
#   return top_24

#######################################################################################################################

def sim_qual_round(data, apps, event):
    country_data, rem_data, us_data = data

    country_data_qual = country_data[country_data["Round"] == 'qual']
    rem_data_qual = rem_data[rem_data["Round"] == 'qual']
    us_data_qual = us_data[us_data["Round"] == 'qual']

    print(event)
    # take top 8
    if event == 'indiv_app':
        qual_results = sim_qual_indiv_app((country_data_qual, rem_data_qual, us_data_qual), apps)
    if event == 'indiv_AA':
        qual_results = sim_qual_indiv_AA((country_data_qual, rem_data_qual, us_data_qual), apps)
    if event == 'team_AA':
        qual_results = sim_qual_team_AA((country_data_qual, us_data_qual), apps)

    return qual_results

#######################################################################################################################

us_team = ["Simone Biles", "Skye Blakely", "Jordan Chiles", "Shilese Jones", "Joscelyn Roberson"]

#######################################################################################################################
# simulate individual apparatus finals
# data_all = (other_country, rem, us)
def sim_indiv_app(data_all, gender, us_team):
    country_data, rem_data, us_data = data_all

    us_athletes = us_data[us_data["FullName"].isin(us_team)].groupby('FullName')['Score'].mean().nlargest(4).index
    us_data = us_data[us_data["FullName"].isin(us_athletes)]
    country_data = country_data[country_data["Gender"] == gender]
    # name_mappings = dict([(name, f'Anonymous{idx}') for idx, name in enumerate(rem_data["FullName"].unique())])
    # rem_data["FullName"].replace(name_mappings, inplace=True)
    rem_data = rem_data[rem_data["Gender"] == gender]
    us_data = us_data[us_data["Gender"] == gender]

    if gender == 'w':
        apps = ['FX', 'BB', 'UB', 'VT1', 'VT2']
    else:
        apps = ['FX', 'PH', 'PB', 'HB', 'SR', 'VT1', 'VT2']
    
  # determine which athletes qualify for finals
  # final_data = advance_to_finals(qual_dict, gender, indiv_app)
  # simulate scores
    qual_results = sim_qual_round((country_data, rem_data, us_data), apps, 'indiv_app')
    print(qual_results)

sim_indiv_app((other_country_data, rem_data, us_data), 'w', us_team)

#######################################################################################################################


# simulate individual AA finals
def sim_indiv_AA(data_all, gender, us_team):
    country_data, rem_data, us_data = data_all

    us_athletes = us_data[us_data["FullName"].isin(us_team)].groupby('FullName')['Score'].mean().nlargest(4).index
    us_data = us_data[us_data["FullName"].isin(us_athletes)]
    country_data = country_data[country_data["Gender"] == gender]

    # name_mappings = dict([(name, f'Anonymous{idx}') for idx, name in enumerate(rem_data["FullName"].unique())])
    # rem_data["FullName"].replace(name_mappings, inplace=True)

    rem_data = rem_data[rem_data["Gender"] == gender]
    us_data = us_data[us_data["Gender"] == gender]

    if gender == 'w':
        apps = ['FX', 'BB', 'UB', 'VT']
    else:
        apps = ['FX', 'PH', 'PB', 'HB', 'SR', 'VT']

    qual_results = sim_qual_round((country_data, rem_data, us_data), apps, 'indiv_AA')
    print(qual_results)

# sim_indiv_AA((other_country_data, rem_data, us_data), 'w', us_team)

#######################################################################################################################

# simulate team AA finals
def sim_team_AA(data_all, gender, us_team):
  
    country_data, rem_data, us_data = data_all

    us_athletes = us_data[us_data["FullName"].isin(us_team)].groupby('FullName')['Score'].mean().nlargest(4).index
    us_data = us_data[us_data["FullName"].isin(us_athletes)]
    country_data = country_data[country_data["Gender"] == gender]
    # name_mappings = dict([(name, f'Anonymous{idx}') for idx, name in enumerate(rem_data["FullName"].unique())])
    # rem_data["FullName"].replace(name_mappings, inplace=True)
    rem_data = rem_data[rem_data["Gender"] == gender]
    us_data = us_data[us_data["Gender"] == gender]

    if gender == 'w':
        apps = ['FX', 'BB', 'UB', 'VT1', 'VT2']
    else:
        apps = ['FX', 'PH', 'PB', 'HB', 'SR', 'VT1', 'VT2']
        
    # determine which athletes qualify for finals
    # final_data = advance_to_finals(qual_dict, gender, indiv_app)
    # simulate scores
    qual_results = sim_qual_round((country_data, rem_data, us_data), apps, 'team_AA')
    print(qual_results)

#######################################################################################################################
