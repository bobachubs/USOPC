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
data.replace("Melanie De jesus dos santos", "Melanie Jesus santos", inplace=True) #special case

# replaced England with Britain
data['Country'].replace("ENG", "GBR", inplace=True) #both GBR and ENG should be GBR
#print(data["Apparatus"].unique())
data['Apparatus'].replace("hb", "HB", inplace=True) #hb should be HB for consistency

# qualifying countries from the 51st and 52nd FIG World Champs, exclusing USA
world_data_2023 = data[(data['Competition'] == '2023 52nd FIG Artistic Gymnastics World Championships')]
qual_countries_w = ['CHN', 'BRA', 'ITA', 'NED', 'FRA', 'JPN', 'AUS', 'ROU', 'KOR', 'GBR', 'CAN']
qual_countries_m = ['CHN', 'GBR', 'GER', 'JPN', 'BRA', 'ITA', 'CAN', 'SUI', 'ESP', 'TUR', 'NED']

qual_athletes_w = []
qual_athletes_m = []

# getting teams of 5 for the other 11 countries
# looping through every country that qualified for women's comp and taking the
# top for out of 5
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

# Only US has VT instead of VT1 or VT2 for quals, change it
us_data.loc[(us_data['Round'] == 'qual') & (us_data['Apparatus'] == 'VT'), 'Apparatus'] = 'VT1'


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

# Only US has VT instead of VT1 or VT2 for quals, change it 
print(data[(data["Country"] == 'USA') & (data["Round"]=='qual') & (data["Gender"]=='w')]["Apparatus"].unique())

us_data.loc[(us_data['Round'] == 'qual') & (us_data['Apparatus'] == 'VT'), 'Apparatus'] = 'VT1'

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

#######################################################################################################################

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

# output qual_dict for individual AA
# {athlete: {app: (score)}}
def make_indiv_AA_dict(app_indiv, teams_data, athletes_36):
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
  team_AA = dict()
  for country in teams_data["Country"].unique():
      team_AA[country] = dict()
      for athlete in teams_data["FullName"].unique():
          team_AA[country][athlete] = dict()
          for app in app_medals:
              score = app_medals[app][athlete]
              team_AA[c][athlete][app] = score
  return team_AA

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

#######################################################################################################################

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

def sim_qual(curr_combo, us_data, country_data, rem_data, gender):
    if gender == 'w':
        apps = ['FX', 'BB', 'UB', 'VT1', 'VT2']
    else:
        apps = ['FX', 'PH', 'PB', 'HB', 'SR', 'VT1', 'VT2']
    us_team = us_data[us_data["FullName"].isin(curr_combo)]
    teams_data = pd.concat([country_data, us_team])
    app_dict = dict()
    app_indiv = dict()
    athletes_VT1 = None
    athlete_36 = None
    for app in apps:
        app_dict[app] = dict()
        # loop through all the unique athletes
        for athlete in teams_data["FullName"].unique():
            app_dict[app][athlete] = get_qual_score(teams_data, athlete, app)

        # 36 random individuals
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
                    app_dict['VT'][athlete] = (np.mean((vt1_score,vt2_score)), np.mean((d1_score,d2_score)), np.mean((e1_score,e2_score)), country)
                del app_dict['VT1']
                del app_dict['VT2']
                app = 'VT'
        app_scores_dict = dict()
        for athlete, scores in app_scores_dict:
            app_scores_dict[athlete] = {"Score": scores[0],
                                        "D_Score": scores[1],
                                        "E_Score": scores[2],
                                        "Country": scores[3]}
        app_indiv[app] = app_scores_dict

        indiv_AA = make_indiv_AA_dict(app_indiv, teams_data, athlete_36)
        team_AA = make_team_AA_dict(app_indiv, teams_data)
    return team_AA, indiv_AA, app_indiv


#######################################################################################################################
# Finals

def sim_team_AA(curr_combo, qual_dict, us_data, country_data, rem_data, gender):
  return

def sim_indiv_AA(curr_combo, qual_dict, us_data, country_data, rem_data, gender):
  return

def sim_indiv_app(curr_combo, qual_dict, us_data, country_data, rem_data, gender):
    if gender == 'w':
        apps = ['FX', 'BB', 'UB', 'VT']
    else:
        apps = ['FX', 'PH', 'PB', 'HB', 'SR', 'VT']

    country_counts = dict()
    app_quals = dict()
    for app in apps:
        app_scores = sorted(qual_dict[app].items(), key=lambda item: (item[1][0]), reverse=True)
        selected_scores = []
        for athlete, scores in app_scores.items():
            country = scores[3]
            if len(selected_scores) < 8:
                country_counts[country] = country_counts.get(country, 0) + 1
                if country_counts[country] < 3:
                    selected_scores = selected_scores.append(athlete)
    app_quals[app] = selected_scores

    finals_athletes = []

    for app in app_quals:
        for athlete in app_quals[app]:
            finals_athletes.append(athlete)

    finals_data = pd.concat([country_data, us])
    return
#######################################################################################################################
# simulate Individual AA
# sum scores across apparatus, top 24 qualify
def sim_qual_indiv_AA(qual_data, apps):

    country_data, rem_data, us_data = qual_data
    teams_data = pd.concat([country_data, us_data])

    athlete_dict = dict()

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
    # print(sorted(athlete_scores_sum.items(), key=lambda item: item[1]['Score'], reverse=True))
    top_24 = sorted(athlete_scores_sum.items(), key=lambda item: item[1]['Score'], reverse=True)[:24]
    return top_24

#######################################################################################################################
# The top 8 teams in advance based on the sum of the top 3 out of 4 scores on each apparatus
def sim_qual_team_AA(qual_data, apps):

    country_data, rem_data, us_data = qual_data
    teams_data = pd.concat([country_data, us_data])

    team_dict = dict()

    # print(rem_data[(rem_data["Country"]=='GBR') & (rem_data["Apparatus"] == 'VT')])
    for country in teams_data["Country"].unique():
        team_dict[country] = dict()
        team_data = teams_data[teams_data["Country"] == country]
        for athlete in team_data["FullName"].unique():
            team_dict[country][athlete] = dict()
            for app in apps:
                score, e_score, d_score, country = get_qual_score(pd.concat([teams_data, rem_data]), athlete, app)
                print(country, athlete, app)
                print(get_qual_score(teams_data, athlete, app)  )
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

us_team = ["Simone Biles", "Skye Blakely", "Jordan Chiles", "Shilese Jones", "Joscelyn Roberson"]

#######################################################################################################################
# Wrappers
def count_medals(res_team_AA, res_indiv_AA, res_indiv_app):
    return


def sim_all(curr_combo, us_data, country_data, rem_data, gender):
    #curr_medals = 0
    #for i in range 10000:
    # store qualifying round data
    qual_res = sim_qual(curr_combo, us_data, country_data, rem_data, gender)
    # simulate finals and count medals won by team USA players in each event
    res_team_AA = sim_team_AA(curr_combo, qual_res[0], us_data, country_data, rem_data, gender)
    res_indiv_AA = sim_indiv_AA(curr_combo, qual_res[1], us_data, country_data, rem_data, gender)
    res_indiv_app = sim_indiv_app(curr_combo, qual_res[2], us_data, country_data, rem_data, gender)
    curr_medals += count_medals(res_team_AA, res_indiv_AA, res_indiv_app)
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
  w_res = sim_wrapper('w')
  m_res = sim_wrapper('m')
  return(w_res, m_res)

overall_results = greatest_wrapper_of_all()
print(f"Women's Team: {overall_results[0][0]}")
print(f"Women's Medals: {overall_results[0][1]}")
print(f"Men's Team: {overall_results[1][0]}")
print(f"Men's Medals: {overall_results[1][1]}")
    

#######################################################################################################################
# sim_indiv_app((qual_country_data, rem_data, us_data), 'w', us_team)
# sim_indiv_AA((qual_country_data, rem_data, us_data), 'w', us_team)
# sim_team_AA((qual_country_data, rem_data, us_data), 'w', us_team)


