import pandas as pd
import numpy as np
from itertools import combinations
import matplotlib.pyplot as plt

# Preprocessing
################################################################################################

raw_data = pd.read_csv("data_2022_2023.csv")

data = raw_data
data['LastName'] = data['LastName'].str.lower().str.capitalize()
# combine first and last name
data['FullName'] = data['FirstName'] + ' ' + data['LastName']

# special case for French gymast entered under two different names
data.replace("Melanie De jesus dos santos", "Melanie Jesus santos", inplace=True)

data['Country'].replace("ENG", "GBR", inplace=True) #both GBR and ENG should be GBR

data['Apparatus'].replace("hb", "HB", inplace=True) #hb should be HB for consistency

data['Apparatus'].replace("VT1", "VT", inplace=True) #VT1 and VT2 now VT
data['Apparatus'].replace("VT2", "VT", inplace=True) #VT1 and VT2 now VT


# qualifying countries from the 51st and 52nd FIG World Champs, exclusing USA
world_data_2023 = data[(data['Competition'] == '2023 52nd FIG Artistic Gymnastics World Championships')]
qual_countries_w = ['CHN', 'BRA', 'ITA', 'NED', 'FRA', 'JPN', 'AUS', 'ROU', 'KOR', 'GBR', 'CAN']
qual_countries_m = ['CHN', 'GBR', 'GER', 'JPN', 'BRA', 'ITA', 'CAN', 'SUI', 'ESP', 'TUR', 'NED']

qual_athletes_w = []
qual_athletes_m = []

# getting teams of 5 for the other 11 countries
# looping through every country that qualified for women's comp and taking the top 4/5
for c in qual_countries_w:
  # unique athletes from country
    athletes = world_data_2023[(world_data_2023["Country"]==c) & (world_data_2023["Gender"] == 'w')]['FullName'].unique()
    if len(athletes) > 4:
      # filtering for athletes from the country that won --> all scores
      # getting mean and taking top 4
        athletes_scores = world_data_2023[(world_data_2023["Country"]==c) & (world_data_2023["Gender"] == 'w')]
        athletes = athletes_scores.groupby('FullName')['Score'].mean().nlargest(4).index
    qual_athletes_w += list(athletes)

for c in qual_countries_m:
    athletes = world_data_2023[(world_data_2023["Country"]==c) & (world_data_2023["Gender"] == 'm')]['FullName'].unique()
    if len(athletes) > 4:
        athletes_scores = world_data_2023[(world_data_2023["Country"]==c) & (world_data_2023["Gender"] == 'm')]
        athletes = athletes_scores.groupby('FullName')['Score'].mean().nlargest(4).index
    qual_athletes_m += list(athletes)

# removing all rows with no name or no score
data = data.dropna(subset=['FullName', 'Score'])
# unique columns to keep
data = data[['Gender', 'Country', 'Round', 'Apparatus', 'D_Score', 'E_Score', 'Score', 'FullName']]
data = data.drop_duplicates()

# Men and women athletes we are assuming to go to the olympics for our simulation
qual_country_data = data[(data["FullName"].isin(qual_athletes_w) |
                data["FullName"].isin(qual_athletes_m))]

# now the mutually exclusive set of data excluding qualifying teams for simulating remaining 36 for each gender
rem_data = data[((~data["Country"].isin(qual_countries_w)) &
                (~data["Country"].isin(qual_countries_m)) &
                (data["Country"] != 'USA'))]
# USA athletes
us_data = data[(data["Country"] == 'USA')]

data = data.dropna(subset=['FullName', 'Score'])
data = data[['Gender', 'Country', 'Round', 'Apparatus', 'D_Score', 'E_Score', 'Score', 'FullName']]
data = data.drop_duplicates()

qual_country_data = data[(data["FullName"].isin(qual_athletes_w) |
                data["FullName"].isin(qual_athletes_m))]

# now the mutually exclusive set of data excluding qualifying teams for simulating remaining 36 for each gender

rem_data = data[((~data["Country"].isin(qual_countries_w)) &
                (~data["Country"].isin(qual_countries_m)) &
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
    return (score, d_score, e_score, country)

#######################################################################################################################

# output qual_dict for individual AA
# {athlete: {app: (score)}}
def make_indiv_AA_dict(app_indiv, teams_data, athletes_36):
    app_indiv['VT'] = app_indiv['VT1']
    del app_indiv['VT1']
    teams_unique = teams_data['FullName'].unique()
    athletes = np.concat([teams_unique, athletes_36])
    AA_dict = dict()
    for athlete in athletes:
        athlete_dict = dict()
        for app in app_indiv:
            data = app_indiv[app][athlete]
            athlete_dict[app] = data
            AA_dict[athlete] = athlete_dict
    return AA_dict


# trying team AA
# {country: {athlete: {app: (score)}}}
def make_team_AA_dict(app_indiv, teams_data):
    app_indiv['VT'] = app_indiv['VT1']
    del app_indiv['VT1']
    team_AA = dict()
    for country in teams_data["Country"].unique():
        team_AA[country] = dict()
        for athlete in teams_data["FullName"].unique():
            team_AA[country][athlete] = dict()
            for app in app_indiv:
                score = app_indiv[app][athlete]
                team_AA[c][athlete][app] = score
    return team_AA



#######################################################################################################################

def get_score(data, athlete, app):
    athlete_app_data = data[(data['FullName'] == athlete) & (data['Apparatus'] == app)]
    # NOTE: athlete_app_round_scores: app_score, d_score, e_score
    if athlete_app_data.empty:
        # draw from country's distribution if no data exists
        athlete_country = data[(data["FullName"] == athlete)]["Country"].iloc[0]
        country_app_data = data[(data["Country"] == athlete_country) & (data['Apparatus'] == app)]
        if len(country_app_data) > 0:
            athlete_app_round_scores = sample_history(country_app_data)
        else:
            athlete_app_round_scores = (0, 0, 0, "None")
    else:
        athlete_app_round_scores = sample_history(athlete_app_data)
    return athlete_app_round_scores

#######################################################################################################################

def sim_qual(curr_combo, us_data, country_data, rem_data, gender):
    #VT1 counts for individual_AA and team_AA
    # VT1 and VT2 count for indiv_App, averaged
    # pg 43/171
    # https://www.gymnastics.sport/publicdir/rules/files/en_2022-2024%20WAG%20COP.pdf

    if gender == 'w':
        apps = ['FX', 'BB', 'UB', 'VT1', 'VT2']
    else:
        apps = ['FX', 'PH', 'PB', 'HB', 'SR', 'VT1', 'VT2']

    us_team = us_data[us_data["FullName"].isin(curr_combo)]
    teams_data = pd.concat([country_data, us_team])
    app_dict = dict()
    app_indiv = dict()
    athletes_VT1 = None
    athletes_36 = None
    for app in apps:
        app_dict[app] = dict()
        # loop through all the unique athletes
        for athlete in teams_data["FullName"].unique():
            app_dict[app][athlete] = get_score(teams_data, athlete, app)

        # 36 random individuals
        athletes_36 = np.random.shuffle(rem_data["FullName"].unique())[:36]
        for i in range(36):
            athlete = athletes_36[i]
            if app == 'VT1':
                athletes_VT1.append(athlete)
            if app == 'VT2':
                app_dict[app][athletes_VT1[i]] = get_score(rem_data, athletes_VT1[i], app)
            else:
                app_dict[app][athlete] = get_score(rem_data, athlete, app)
        if app == 'VT1': continue
        if app == 'VT2':
            app_dict['VT'] = dict()
            for athlete in app_dict['VT2']:
                vt1_score, d1_score, e1_score, country = app_dict['VT1'][athlete]
                vt2_score, d2_score, e2_score, country = app_dict['VT2'][athlete]
                app_dict['VT'][athlete] = (np.mean((vt1_score,vt2_score)), np.mean((d1_score,d2_score)), np.mean((e1_score,e2_score)), country)
            del app_dict['VT2']
            app = 'VT'
        app_scores_dict = dict()
        for athlete, scores in app_dict:
            app_scores_dict[athlete] = {"Score": scores[0],
                                        "D_Score": scores[1],
                                        "E_Score": scores[2],
                                        "Country": scores[3]}
        app_indiv[app] = app_scores_dict

    indiv_AA = make_indiv_AA_dict(app_indiv, teams_data, athletes_36)
    team_AA = make_team_AA_dict(app_indiv, teams_data)

    del app_indiv['VT1']

    return app_indiv, indiv_AA, team_AA

#######################################################################################################################

# given indiv_app scores, return back the n athletes who advanced, max 2/country
def advance_indiv_app(indiv_app_scores, n):
    # {FX: {athlete1: (scores), athlete2: (scores), ...}, UB {athlete1: (scores), ...}, ...}
    country_counts = dict()
    app_quals = dict()
    for app in indiv_app_scores:
        app_scores = sorted(indiv_app_scores[app].items(), key=lambda item: (item[1][0]), reverse=True)
        selected_scores = dict()
        for athlete, scores in app_scores:
            country = scores[3]
            if len(selected_scores) < n:
                country_counts[country] = country_counts.get(country, 0) + 1
                if country_counts[country] < 3:
                    selected_scores = selected_scores.append(athlete)
        app_quals[app] = selected_scores
    
    final_athletes = []

    for app in app_quals:
        for athlete in app_quals[app]:
            final_athletes.append(athlete)

    return app_quals, athletes

def advance_indiv_AA(indiv_AA_scores, n):
    # {athlete1: {FX: (scores), UB: (scores), ...}, athlete2: {FX: (scores), UB: scores), ...}, ...}
    country_counts = dict()
    
    # sum scores across apparatus for each athlete
    athlete_scores_sum = dict()
    for athlete, scores in indiv_AA_scores.items():
        total_scores = {'Score': 0,
                        'E_Score': 0,
                        'D_Score': 0,
                        'Country': indiv_AA_scores[athlete]['FX']['Country']}
        for _, app_scores in scores.items():
            # sort by top 3
            # FIX THIS AND DO TOP 3/4 Scores
            total_scores['Score'] += app_scores['Score']
            total_scores['E_Score'] += app_scores['E_Score']
            total_scores['D_Score'] += app_scores['D_Score']

        athlete_scores_sum[athlete] = total_scores

    # {athlete1: (scores_sum, d_sum, e_sum, Country), athlete2.....}
    sorted_athletes = sorted(athlete_scores_sum.items(), key=lambda item: item[1][0], reverse=True)
    
    country_counts = dict()
    athlete_advance = dict()
    final_athletes = []
    for athlete in sorted_athletes:
        country = sorted_athletes[athlete][3]
        if len(athlete_advance) < n:
            country_counts = country_counts.get(country, 0) + 1
            if country_counts[country] < 3:
                athlete_advance[athlete] = sorted_athletes[athlete]
                final_athletes.append(athlete)

    return athlete_advance, final_athletes

def advance_team_AA(team_AA_scores, n):
    # {country1: {athlete1: {app1: (scores), app2: (scores), ...}, athlete2: {app1: (scores), app2: (scores), ...}}, country2:, ...}
                                  
    country_scores_sum = dict()
    for country, athletes in team_AA_scores.items():
        country_total = {'Score': 0,
                        'E_Score': 0,
                        'D_Score': 0,
                        'Country': country}        
        for athlete, app in athletes.items():
            for app, app_scores in app.items():
                country_total['Score'] += app_scores['Score']
                country_total['E_Score'] += app_scores['E_Score']
                country_total['D_Score'] += app_scores['D_Score']
        country_scores_sum[country] = (country_total['Score'], country_total['E_Score'], country_total['D_Score'], country_total['Country'])

    # {country1: (scores_sum, d_sum, e_sum, country1), country2: (scores_sum, d_sum, e_sum, country2)}
    sorted_teams = sorted(country_scores_sum.items(), key=lambda item: item[1][0], reverse=True)[:n]
    # return top n countries/teams
    teams_advance = [country for country in sorted_teams]

    return teams_advance
#######################################################################################################################
# Finals

def sim_indiv_app_final(curr_combo, indiv_app_qual, us_data, country_data, rem_data, gender):
    # outputs a winning dictionary of each apparatus and the winning scores of of each athlete for that app
    if gender == 'w':
        apps = ['FX', 'BB', 'UB', 'VT1', 'VT2']
    else:
        apps = ['FX', 'PH', 'PB', 'HB', 'SR', 'VT1', 'VT2']

    # get top 8 from qualifications first
    _, final_athletes = advance_indiv_app(indiv_app_qual, 8)

    # repeat simulation for the finalists
    us_team = us_data[us_data["FullName"].isin(curr_combo)]
    data_all = pd.concat([country_data, us_team, rem_data])
    finals_data = data_all[data_all["FullName"].isin(final_athletes)]

    app_dict = dict()
    indiv_app_final = dict()
    
    for app in apps:
        app_dict[app] = dict()
        # loop through all the unique athletes
        for athlete in finals_data["FullName"].unique():
            app_dict[app][athlete] = get_score(data_all, athlete, app)
            
        if app == 'VT1': continue
        if app == 'VT2':
            app_dict['VT'] = dict()
            for athlete in app_dict['VT2']:
                vt1_score, d1_score, e1_score, country = app_dict['VT1'][athlete]
                vt2_score, d2_score, e2_score, country = app_dict['VT2'][athlete]
                app_dict['VT'][athlete] = (np.mean((vt1_score,vt2_score)), np.mean((d1_score,d2_score)), np.mean((e1_score,e2_score)), country)
            del app_dict['VT2']
            app = 'VT'
        app_scores_dict = dict()
        for athlete, scores in app_dict:
            app_scores_dict[athlete] = {"Score": scores[0],
                                        "D_Score": scores[1],
                                        "E_Score": scores[2],
                                        "Country": scores[3]}
        indiv_app_final[app] = app_scores_dict

    
    winning_dict, _ = advance_indiv_app(indiv_app_final, 3)

    return winning_dict

def sim_indiv_AA_final(curr_combo, indiv_AA_qual, us_data, country_data, rem_data, gender):
    # outputs a dictionary of winning athletes and a tuple of their score sums
    if gender == 'w':
        apps = ['FX', 'BB', 'UB', 'VT']
    else:
        apps = ['FX', 'PH', 'PB', 'HB', 'SR', 'VT']
    
    # get top 24 from qualifications first
    _, final_athletes = advance_indiv_AA(indiv_AA_qual, 24)   

    # simulate these individuals again
    us_team = us_data[us_data["FullName"].isin(curr_combo)]
    data_all = pd.concat([country_data, us_team, rem_data])
    finals_data = data_all[data_all["FullName"].isin(final_athletes)]

    athlete_dict = dict()

    for athlete in finals_data["FullName"].unique():
        athlete_dict[athlete] = dict()
        for app in apps:
            score, e_score, d_score, country = get_score(data_all, athlete, app)
            athlete_dict[athlete][app] = {'Score': score,
                                            "E_Score": e_score,
                                            "D_Score": d_score,
                                            "Country": country}    
    
    winning_dict, _ = advance_indiv_AA(athlete_dict, 8)
    
    return winning_dict

def sim_team_AA_final(curr_combo, team_AA_qual, us_data, country_data, rem_data, gender):
    # outputs a list of countries

    if gender == 'w':
        apps = ['FX', 'BB', 'UB', 'VT']
    else:
        apps = ['FX', 'PH', 'PB', 'HB', 'SR', 'VT']

    # list of top 8 countries
    final_teams = advance_team_AA(team_AA_qual, 8)

    # simulate these individuals for the advancing countries again
    us_team = us_data[us_data["FullName"].isin(curr_combo)]
    data_all = pd.concat([country_data, us_team, rem_data])
    finals_data = data_all[data_all["Country"].isin(final_teams)]

    team_dict = dict()

    for country in finals_data["Country"].unique():
        team_dict[country] = dict()
        team_data = finals_data[finals_data["Country"] == country]
        for athlete in team_data["FullName"].unique():
            team_dict[country][athlete] = dict()
            for app in apps:
                score, e_score, d_score, country = get_score(data_all, athlete, app)
                # print(country, athlete, app)
                # print(get_score(finals_data, athlete, app)  )
                team_dict[country][athlete][app] = {'Score': score,
                                                    "E_Score": e_score,
                                                    "D_Score": d_score,
                                                    "Country": country}
                
    # final countries
    final_countries = advance_team_AA(team_AA_qual, 3)

    return final_countries

#######################################################################################################################

us_team = ["Simone Biles", "Skye Blakely", "Jordan Chiles", "Shilese Jones", "Joscelyn Roberson"]

#######################################################################################################################
# Wrappers
def count_medals(res_indiv_app, res_indiv_AA, res_team_AA, curr_combo):
    # 
    return


def sim_all(curr_combo, us_data, country_data, rem_data, gender):
    #curr_medals = 0
    #for i in range 10000:
    # store qualifying round data
    indiv_app_qual, indiv_AA_qual, team_AA_qual = sim_qual(curr_combo, us_data, country_data, rem_data, gender)
    # simulate finals and count medals won by team USA players in each event
    res_indiv_app = sim_indiv_app_final(curr_combo, indiv_app_qual, us_data, country_data, rem_data, gender)
    res_indiv_AA = sim_indiv_AA_final(curr_combo, indiv_AA_qual, us_data, country_data, rem_data, gender)
    res_team_AA = sim_team_AA_final(curr_combo, team_AA_qual, us_data, country_data, rem_data, gender)
    curr_medals += count_medals(res_indiv_app, res_indiv_AA, res_team_AA, curr_combo)
    #curr_medals /= 10000 # average medals for curr combo
    return curr_medals


def sim_wrapper(gender):
    unique_athletes = us_data['FullName'].unique()
    combos_list = combinations(unique_athletes, 4)
    max_medals = 0
    max_combo = None
    for curr_combo in combos_list:
        curr_medals = sim_all(curr_combo, us_data, qual_country_data, rem_data, gender)
        if curr_medals > max_medals:
            max_medals = curr_medals
            max_combo = curr_combo
    return(max_combo, max_medals)

def greatest_wrapper_of_all():
    w_results = sim_wrapper('w')
    m_results = sim_wrapper('m')
    print(f"Women's Team: {w_results[0][0]}")
    print(f"Women's Medals: {w_results[0][1]}")
    print(f"Men's Team: {m_results[1][0]}")
    print(f"Men's Medals: {m_results[1][1]}")
    return

greatest_wrapper_of_all()

#######################################################################################################################
# sim_indiv_app((qual_country_data, rem_data, us_data), 'w', us_team)
# sim_indiv_AA((qual_country_data, rem_data, us_data), 'w', us_team)
# sim_team_AA((qual_country_data, rem_data, us_data), 'w', us_team)


