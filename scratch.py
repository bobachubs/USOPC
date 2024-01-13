import pandas as pd
import numpy as np
from itertools import combinations
import matplotlib.pyplot as plt
import math

og_data = pd.read_csv('test.csv')
data = pd.read_csv('distinct_apps_sim2.csv')

# Country,Apparatus,Gender,FullName,sim_1,sim_2,sim_3, ...
# NOR,HB,m,Fredrik Aas,11.422621618293013,12.576161878469694,12.801027545101967,...

# qualifying countries from the 51st and 52nd FIG World Champs, excluding USA
world_data_2023 = og_data[(og_data['Competition'] ==
                        '2023 52nd FIG Artistic Gymnastics World Championships')]
qual_countries_w = ['CHN', 'BRA', 'ITA', 'NED',
                    'FRA', 'JPN', 'AUS', 'ROU', 'KOR', 'GBR', 'CAN']
qual_countries_m = ['CHN', 'GBR', 'GER', 'JPN',
                    'BRA', 'ITA', 'CAN', 'SUI', 'ESP', 'TUR', 'NED']

qual_athletes_w = []
qual_athletes_m = []

# getting teams of 5 for the other 11 qualifying countries listed above
# looping through every country that qualified for women's comp and taking the top 4/5
for c in qual_countries_w:
  # unique athletes from country
    athletes = world_data_2023[(world_data_2023["Country"] == c) & (
        world_data_2023["Gender"] == 'w')]['FullName'].unique()
    if len(athletes) > 4:
      # filtering for top 4 athletes from the country that won --> all scores
      # getting mean and taking top 4
        athletes_scores = world_data_2023[(world_data_2023["Country"] == c) & (
            world_data_2023["Gender"] == 'w')]
        athletes = athletes_scores.groupby(
            'FullName')['Score'].mean().nlargest(4).index
    qual_athletes_w += list(athletes)

# same as above but for mens
for c in qual_countries_m:
    athletes = world_data_2023[(world_data_2023["Country"] == c) & (
        world_data_2023["Gender"] == 'm')]['FullName'].unique()
    if len(athletes) > 4:
        athletes_scores = world_data_2023[(world_data_2023["Country"] == c) & (
            world_data_2023["Gender"] == 'm')]
        athletes = athletes_scores.groupby(
            'FullName')['Score'].mean().nlargest(4).index
    qual_athletes_m += list(athletes)

# Men and women athletes we are assuming to go to the olympics for our simulation
qual_country_data = data[(data["FullName"].isin(qual_athletes_w) |
                          data["FullName"].isin(qual_athletes_m))]

# now the mutually exclusive set of data excluding qualifying teams for simulating remaining 36 for each gender
rem_data = data[((~data["Country"].isin(qual_countries_w)) &
                (~data["Country"].isin(qual_countries_m)) &
                (data["Country"] != 'USA'))]
# USA athletes
us_data = data[(data["Country"] == 'USA')]

#######################################################################################################################

# sample from an athlete's history n times for an apparatus in a round

def sample_country(country_data, sim_i):
    row = data.sample(1)
    score = row[f'sim_{sim_i}'].iloc[0]
    return score

#######################################################################################################################

# retrieve athlete score from lmer data with index sim_i

def get_score(data, athlete, app, sim_i):
    athlete_app_data = data[(data['FullName'] == athlete)
                            & (data['Apparatus'] == app)]
    athlete_country = data[data['FullName'] == athlete]["Country"].iloc[0]
    if athlete_app_data.empty:
        # draw from country's distribution if no data exists
        country_app_data = data[(data["Country"] == athlete_country) & (
            data['Apparatus'] == app)]
        if len(country_app_data) > 0:
            athlete_app_round_score = sample_country(country_app_data, sim_i)
        else:
            # athlete_app_round_scores = (0, "None")
            athlete_app_round_score = 0
    else:
        athlete_app_round_score = athlete_app_data[f'sim_{sim_i}'].iloc[0]
    return (athlete_app_round_score, athlete_country)

#######################################################################################################################

# input of app_indiv
# {FX: {athlete1: {score: _, d_score: _, e_score: _, country:_}, athlete2: {scores}, ...}, UB {athlete1: {scores}, ...}, ...}
# output qual_dict for individual AA
# {athlete1: {app1: {score: _, d_score: _, e_score: _}, app2: {scores}, ..}, athlete2: {...}}


def make_indiv_AA_dict(app_indiv, teams_data, athletes_36):
    app_indiv['VT'] = app_indiv['VT1']
    teams_unique = teams_data['FullName'].unique()
    athletes = np.concatenate([teams_unique, athletes_36])
    AA_dict = dict()
    for athlete in athletes:
        athlete_dict = dict()
        for app in app_indiv:
            if not app == 'VT1':
                data = app_indiv[app][athlete]
                athlete_dict[app] = data
                AA_dict[athlete] = athlete_dict
    return AA_dict


# output for team AA
# {country: {athlete: {app: (score)}}}
def make_team_AA_dict(app_indiv, teams_data):
    app_indiv['VT'] = app_indiv['VT1']
    team_AA = dict()
    for country in teams_data["Country"].unique():
        team_AA[country] = dict()
        country_athletes = teams_data[(teams_data['Country'] == country)]
        for athlete in country_athletes["FullName"].unique():
            team_AA[country][athlete] = dict()
            for app in app_indiv:
                if not app == 'VT1':
                    score = app_indiv[app][athlete]
                    team_AA[country][athlete][app] = score
    # print("team", team_AA['GBR'].keys())
    return team_AA

#######################################################################################################################


def sim_qual(curr_combo, us_data, country_data, rem_data, gender, sim_i):
    # VT1 counts for individual_AA and team_AA
    # VT1 and VT2 count for indiv_App, averaged
    # pg 43/171
    # https://www.gymnastics.sport/publicdir/rules/files/en_2022-2024%20WAG%20COP.pdf

    # determine relevant apparatuses
    if gender == 'w':
        apps = ['FX', 'BB', 'UB', 'VT1', 'VT2']
    else:
        apps = ['FX', 'PH', 'PB', 'HB', 'SR', 'VT1', 'VT2']

    # get data on current USA team for sampling
    us_team = us_data[us_data["FullName"].isin(curr_combo)]
    # combine into big data frame
    teams_data = pd.concat([country_data, us_team])
    data_all = pd.concat([country_data, us_data, rem_data])
    app_dict = dict()  # dictionary to track results for each app
    app_indiv = dict()  # track each athlete's performance
    # athletes_VT1 = []
    athletes_36 = []

    # 36 random individuals
    rem_data = rem_data[(rem_data["Gender"] == gender)]
    athletes_36 = np.random.permutation(rem_data["FullName"].unique())[:36]

    # sampling for qualifying teams
    for app in apps:
        app_dict[app] = dict()
        # loop through all the unique athletes
        for athlete in teams_data["FullName"].unique():
          # sample from merged VT
            if app == 'VT1' or app == 'VT2':
                app_dict[app][athlete] = get_score(data_all, athlete, 'VT', sim_i)
            else:
                app_dict[app][athlete] = get_score(data_all, athlete, app, sim_i)

  # sampling for 36 individuals
        for i in range(36):
            athlete = athletes_36[i]
            # if app == 'VT1':
            #     athletes_VT1.append(athlete)
            #     app_dict[app][athlete] = get_score(rem_data, athlete, 'VT')
            # elif app == 'VT2':
            #     app_dict[app][athletes_VT1[i]] = get_score(rem_data, athletes_VT1[i], 'VT')
            if app == 'VT1' or app == 'VT2':
                app_dict[app][athlete] = get_score(rem_data, athlete, 'VT', sim_i)
                app_dict[app][athlete] = get_score(rem_data, athlete, 'VT', sim_i)
            else:
                app_dict[app][athlete] = get_score(rem_data, athlete, app, sim_i)
        if app == 'VT2':
            app_dict['VT'] = dict()
            for athlete in app_dict['VT2']:
                vt1_score, country = app_dict['VT1'][athlete]
                vt2_score, country = app_dict['VT2'][athlete]
                app_dict['VT'][athlete] = (np.mean((vt1_score, vt2_score)), country)
            del app_dict['VT2']
            app = 'VT'
        app_scores_dict = dict()
        for athlete, scores in app_dict[app].items():
            app_scores_dict[athlete] = {"Score": scores[0], 
                                        "Country": scores[1]}
        app_indiv[app] = app_scores_dict
    indiv_AA = make_indiv_AA_dict(app_indiv, teams_data, athletes_36)
    team_AA = make_team_AA_dict(app_indiv, teams_data)
    del app_indiv['VT1']

    return app_indiv, indiv_AA, team_AA

#######################################################################################################################
# Advancing
# given indiv_app scores, return back the 8 athletes who advanced, max 2/country
# for each app


def advance_indiv_app(indiv_app_scores, n):
    # {FX: {athlete1: {score: _, d_score: _, e_score: _, country:_}, athlete2: {scores}, ...}, UB {athlete1: {scores}, ...}, ...}
    app_quals = dict()
    for app in indiv_app_scores:
        country_counts = dict()
      # for the app, sort the scores in decreasing order
        app_scores = sorted(indiv_app_scores[app].items(), key=lambda item: (item[1]["Score"]), reverse=True)
        # print(app, app_scores)
        selected_scores = dict()
        for athlete, scores in app_scores:
            country = scores["Country"]
            if len(selected_scores) < n:
                country_counts[country] = country_counts.get(country, 0) + 1
                if country_counts[country] < 3:
                    selected_scores[athlete] = scores
        app_quals[app] = selected_scores

# returning dictionary where each app key stores a list of the athletes
# who qualified for that app's finals
# {FX: [ath1, ath2, ... , ath8], ... , BB: [...]}
    # final_athletes = []
    final_athletes = dict()
    for app in app_quals:
        final_athletes[app] = []
        for athlete in app_quals[app]:
            final_athletes[app].append(athlete)
    # return app_quals, final_athletes
    # print("final athletes", final_athletes)
    return final_athletes


def advance_indiv_AA(indiv_AA_scores, n):
    # {athlete1: {FX: {score:_, d_score: _, e_score:_, country_}, UB: {scores}, ...}, athlete2: {FX: {scores}, UB: {scores}, ...}, ...}
    country_counts = dict()

    # sum scores across apparatus for each athlete
    athlete_scores_sum = dict()
    for athlete, scores in indiv_AA_scores.items():
        total_scores = {'Score': 0,
                        'Country': indiv_AA_scores[athlete]['FX']['Country']}
        for _, app_scores in scores.items():
            total_scores['Score'] += app_scores['Score']

        athlete_scores_sum[athlete] = total_scores

    # input {athlete1: {scores_sum: _, d_sum: _, e_sum: _, Country: _}, athlete2.....}
    # sorted into [(athlete1, score_dict), (athlete2, score_dict)]
    sorted_athletes = sorted(athlete_scores_sum.items(
    ), key=lambda item: item[1]["Score"], reverse=True)
    country_counts = dict()
    # athlete_advance = dict()
    final_athletes = []
    for athlete, score in sorted_athletes:
        country = score["Country"]
        # if len(athlete_advance) < n:
        if len(final_athletes) < n:
            country_counts[country] = country_counts.get(country, 0) + 1
            if country_counts[country] < 3:
                # athlete_advance[athlete] = score
                final_athletes.append(athlete)
    # print("final athletes", final_athletes)
    return final_athletes

# def advance_team_AA(team_AA_scores, n):
#     # {country1: {athlete1: {app1: (scores), app2: (scores), ...}, athlete2: {app1: (scores), app2: (scores), ...}}, country2:, ...}
#     country_scores_sum = dict()
#     for country, athletes in team_AA_scores.items():
#         # sorted_athletes = sorted(athletes.items(), key=lambda item: item[1][0], reverse=True)[:n]
#         country_total = {'Score': 0,
#                         'D_Score': 0,
#                         'E_Score': 0,
#                         'Country': country}
#         for athlete, app in athletes.items():
#             for app, app_scores in app.items():
#                 country_total['Score'] += app_scores['Score']
#                 country_total['D_Score'] += app_scores['D_Score']
#                 country_total['E_Score'] += app_scores['E_Score']
#         country_scores_sum[country] = country_total

#     # {country1: (scores_sum, d_sum, e_sum, country1), country2: (scores_sum, d_sum, e_sum, country2)}
#     # sorted_teams = sorted(country_scores_sum.items(), key=lambda item: item[1][0], reverse=True)[:n]
#     # return top n countries/teams
#     teams_advance = [country for country in country_scores_sum]

#     return teams_advance


# find which 8 countries go to finals
def advance_team_AA(team_AA_scores, n):
    # {country1: {athlete1: {app1: (scores), app2: (scores), ...}, athlete2: {app1: (scores), app2: (scores), ...}}, country2:, ...}
    countries_scores = dict()  # scoring team AA score for all countries
    # for each country sum the individual scores to get the 4 AA scores
    all_countries_totals = dict()  # all the top 3 athletes from each team
    for country in team_AA_scores:
        countries_scores[country] = 0  # keeps track of countries team AA
        country_total = dict()  # AA scores for country's team
        # dict athletes and their indiv app scores
        country_info = team_AA_scores[country]
        # summing scores for all apps for one athlete
        for athlete, app in country_info.items():
            athlete_total = {'Score': 0,
                             'Country': country}
            for app, app_scores in app.items():
                athlete_total['Score'] += app_scores['Score']
            # store total AA scores of each athlete and sort to get the top 3
            country_total[athlete] = athlete_total['Score']
        country_total = dict(sorted(country_total.items(),
                                    key=lambda item: item[1], reverse=True)[:3])
        all_countries_totals[country] = country_total  # store top 3 athletes
        # if country == 'GBR': print("totals", country_total)
        countries_scores[country] = sum(
            country_total.values())  # find team AA score
    # print("scores", countries_scores)
    # select the 8 teams with the highest team AA scores
    countries_scores = dict(sorted(countries_scores.items(),
                                   key=lambda item: item[1], reverse=True)[:n])
    advance_team_AA = dict()  # for the teams that advance, get the top 3 athletes
    for country in countries_scores:
        # print("all total", all_countries_totals)
        advance_team_AA[country] = list(all_countries_totals[country])
    # {Country 1: [ath1, ath2, ath3], ... , Country 8: [...]}
    # print("advanced", advance_team_AA)
    return advance_team_AA


#######################################################################################################################
# Finals

def sim_indiv_app_final(curr_combo, indiv_app_qual, us_data, country_data, rem_data, gender, sim_i):
    # outputs a winning dictionary of each apparatus and the winning scores of of each athlete for that app
    if gender == 'w':
        apps = ['FX', 'BB', 'UB', 'VT1', 'VT2']
    else:
        apps = ['FX', 'PH', 'PB', 'HB', 'SR', 'VT1', 'VT2']

    # get top 8 from qualifications first
    final_athletes = advance_indiv_app(indiv_app_qual, 8)

    # {FX: [ath1, ath2, ..., ath8], ... VT: [...]}

    # repeat simulation for the finalists
    us_team = us_data[us_data["FullName"].isin(curr_combo)]
    data_all = pd.concat([country_data, us_team, rem_data])
    # finals_data = data_all[data_all["FullName"].isin(final_athletes)]

    app_dict = dict()
    indiv_app_final = dict()

    for app in apps:
        app_dict[app] = dict()
        # loop through all the unique athletes
        if app == 'VT1' or app == 'VT2':
            athletes = final_athletes['VT']
        else:
            athletes = final_athletes[app]
        # for athlete in finals_data["FullName"].unique():
        for athlete in athletes:
            if app == 'VT1' or app == 'VT2':
                app_dict[app][athlete] = get_score(data_all, athlete, 'VT', sim_i)
            else:
                app_dict[app][athlete] = get_score(data_all, athlete, app, sim_i)
        if app == 'VT2':
            app_dict['VT'] = dict()
            for athlete in app_dict['VT2']:
                vt1_score, country = app_dict['VT1'][athlete]
                vt2_score, country = app_dict['VT2'][athlete]
                app_dict['VT'][athlete] = (np.mean((vt1_score, vt2_score)), country)
            del app_dict['VT2']
            app = 'VT'
        app_scores_dict = dict()
        for athlete, scores in app_dict[app].items():
            app_scores_dict[athlete] = {"Score": scores[0], 
                                        "Country": scores[1]}
        indiv_app_final[app] = app_scores_dict

    winning_dict = advance_indiv_app(indiv_app_final, 3)

    del winning_dict['VT1']

    return winning_dict


def sim_indiv_AA_final(curr_combo, indiv_AA_qual, us_data, country_data, rem_data, gender, sim_i):
    # outputs a dictionary of winning athletes and a tuple of their score sums
    if gender == 'w':
        apps = ['FX', 'BB', 'UB', 'VT']
    else:
        apps = ['FX', 'PH', 'PB', 'HB', 'SR', 'VT']

    # get top 24 from qualifications first
    final_athletes = advance_indiv_AA(indiv_AA_qual, 24)

    # simulate these individuals again
    us_team = us_data[us_data["FullName"].isin(curr_combo)]
    data_all = pd.concat([country_data, us_team, rem_data])
    # finals_data = data_all[data_all["FullName"].isin(final_athletes)]

    athlete_dict = dict()

    for athlete in final_athletes:
        athlete_dict[athlete] = dict()
        for app in apps:
            score, country = get_score(data_all, athlete, app, sim_i)
            athlete_dict[athlete][app] = {'Score': score,
                                          "Country": country}

    winners_list = advance_indiv_AA(athlete_dict, 3)

    return winners_list


def sim_team_AA_final(curr_combo, team_AA_qual, us_data, country_data, rem_data, gender, sim_i):
    # outputs a list of countries

    if gender == 'w':
        apps = ['FX', 'BB', 'UB', 'VT1']
    else:
        apps = ['FX', 'PH', 'PB', 'HB', 'SR', 'VT1']

    # {Country 1: [ath1, ath2, ath3], ... Country 8: [...]}
    final_teams = advance_team_AA(team_AA_qual, 8)

    # simulate these individuals for the advancing countries again
    us_team = us_data[us_data["FullName"].isin(curr_combo)]
    data_all = pd.concat([country_data, us_team, rem_data])
    # finals_data = data_all[data_all["Country"].isin(final_teams)]

    team_dict = dict()

    for country in final_teams:
        team_dict[country] = dict()
        for athlete in final_teams[country]:
            team_dict[country][athlete] = dict()
            for app in apps:
                if app == 'VT1':
                    scores = get_score(data_all, athlete, 'VT', sim_i)
                else:
                    scores = get_score(data_all, athlete, app, sim_i)
                # print(country, athlete, app)
                team_dict[country][athlete][app] = {'Score': scores[0],
                                                    "Country": scores[1]}

    # final countries
    # output [(country1, (scores)), (country2, (Scores)), ...]
    final_countries = advance_team_AA(team_AA_qual, 3)

    return final_countries


#######################################################################################################################
# Wrappers
# Individual App Results
# {'FX': ['Simone Biles', 'Rebeca Andrade', 'Jessica Gadirova'], }
# #################
# Individual AA Results
# ['Simone Biles', 'Rebeca Andrade', 'Melanie Jesus santos']
# #################
# Team AA Results
# {'USA': ['Simone Biles', 'Skye Blakely', 'Jordan Chiles'],
def count_medals(res_indiv_app, res_indiv_AA, res_team_AA, curr_combo):
    medal_count = 0

    for app in res_indiv_app:
        athletes = res_indiv_app[app]
        for athlete in curr_combo:
            if athlete in athletes:
                medal_count += 1
    for athlete in res_indiv_AA:
        if athlete in curr_combo:
            medal_count += 1

    if 'USA' in res_team_AA:
        # get counts of 'USA' that appear in results vs doesn't, plot binary barplot
        medal_count += 1

    return medal_count


def sim_all(curr_combo, us_data, country_data, rem_data, gender):
    us_data = us_data[us_data["Gender"] == gender]
    country_data = country_data[country_data['Gender'] == gender]
    rem_data = rem_data[rem_data["Gender"] == gender]
    curr_medals = 0
    for i in range(100):
        sim_i = i+1
        # store qualifying round data
        indiv_app_qual, indiv_AA_qual, team_AA_qual = sim_qual(
            curr_combo, us_data, country_data, rem_data, gender, sim_i)
        # simulate finals and count medals won by team USA players in each event
        res_indiv_app = sim_indiv_app_final(
            curr_combo, indiv_app_qual, us_data, country_data, rem_data, gender, sim_i)
        # print("###################################################")
        # print("Individual App Results")
        # print(res_indiv_app)
        res_indiv_AA = sim_indiv_AA_final(
            curr_combo, indiv_AA_qual, us_data, country_data, rem_data, gender, sim_i)
        # print("###################################################")
        # print("Individual AA Results")
        # print(res_indiv_AA)
        res_team_AA = sim_team_AA_final(
            curr_combo, team_AA_qual, us_data, country_data, rem_data, gender, sim_i)
        # print("###################################################")
        # print("Team AA Results")
        # print(res_team_AA)
        curr_medals += count_medals(res_indiv_app,
                                    res_indiv_AA, res_team_AA, curr_combo)
    curr_medals /= 100  # average medals for curr combo
    return curr_medals

# def sim_wrapper(gender):
#     unique_athletes = us_data['FullName'].unique()
#     combos_list = combinations(unique_athletes, 4)
#     max_medals = 0
#     max_combo = None
#     for curr_combo in combos_list:
#         curr_medals = sim_all(curr_combo, us_data, qual_country_data, rem_data, gender)
#         if curr_medals > max_medals:
#             max_medals = curr_medals
#             max_combo = curr_combo
#     return(max_combo, max_medals)


def greatest_wrapper_of_all():
    for us_team_w in list((combinations(us_contenders, 4))):
        if 'Simone Biles' in us_team_w and 'Konnor Mcclain' in us_team_w:
            print(us_team_w)
            w_results = sim_all(us_team_w, us_data, qual_country_data, rem_data, 'w')
    # m_results = sim_all(us_team_m, us_data, qual_country_data, rem_data, 'm')
    # print(f"Women's Team: {w_results}")
            print(f"Women's Medals: {w_results}")
    # print(f"Men's Team: {m_results}")
    # print(f"Men's Medals: {m_results}")
    return


# us_team_w = ['Simone Biles', 'Shilese Jones', 'Jade Carey', 'Konnor Mcclain']
us_team_m = ['Shane Wiskus', 'Paul Juda', 'Yul Moldauer',
             'Frederick Richard', 'Donnell Whittenburg']

us_women = us_data[us_data["Gender"] == 'w']["FullName"].unique().tolist()

# ['Ciena Alipio' 'Leigh Anne elliott' 'Sydney Barros' 'Simone Biles'
#  'Skye Blakely' 'Charlotte Booth' 'Jade Carey' 'Dulcy Caylor'
#  'Jordan Chiles' 'Chloe Cho' 'Norah Christian' 'Adriana Consoli'
#  'Kayla Dicello' 'Amelia Disidore' 'Gabby Disidore' 'Skylar Draser'
#  'Amari Drayton' 'Jordis Eichman' 'Addison Fatta' 'eMjae Frazier'
#  'Karis German' 'Olivia Greaves' 'Madray Johnson' 'Shilese Jones'
#  'Katelyn Jong' 'Levi Jung-ruivivar' 'Avery King' 'Sunisa Lee' 'Myli Lew'
#  'Kaliya Lincoln' 'Lauren Little' 'Eveylynn Lowe' 'Nola Matthews'
#  'Nola Rhianne Matthews' 'Konnor Mcclain' 'Zoe Miller' 'Annalisa Milton'
#  'Malea Milton' 'Avery Moll' 'Kaylen Morgan' 'Elle Mueller' 'Ella Murphy'
#  'Marissa Neal' 'Brooke Pierson' 'Michelle Pineda' 'Christiane Popovich'
#  'Camryn Richardson' 'Joscelyn Roberson' 'Joscelyn Michelle Roberson'
#  'Katelyn Rosen' 'Ashlee Sullivan' 'Tiana Sumanasekera' 'Brynn Torry'
#  'Gabriella Van frayen' 'Paityn Walker' 'Leanne Wong' 'Kelise Woolford'
#  'Lexi Zeiss' 'Alicia Zhou']


us_contenders = ['Simone Biles', 'Shilese Jones',
                 'Skye Blakely', 'Jordan Chiles', 'Jade Carey',
                 'Kayla Dicello', 'Konnor Mcclain',
                 'Addison Fatta', 'Zoe Miller', 'Gabby Disidore']

# ('Simone Biles', 'Shilese Jones', 'Jade Carey', 'Konnor Mcclain')

# print(item for item in list(combinations(us_contenders, 4)) if 'Simone Biles' in item)
# print((us_data['FullName'].value_counts()))
greatest_wrapper_of_all()

#####################################################################################################################
# sim_indiv_app((qual_country_data, rem_data, us_data), 'w', us_team)
# sim_indiv_AA((qual_country_data, rem_data, us_data), 'w', us_team)
# sim_team_AA((qual_country_data, rem_data, us_data), 'w', us_team)

# us_team_w = ["Simone Biles", "Skye Blakely", "Jordan Chiles", "Shilese Jones"]
# us_team_m = ['Shane Wiskus', 'Paul Juda', 'Yul Moldauer', 'Frederick Richard', 'Donnell Whittenburg']
#######################################################################################################################

# sim_all(us_team_w, us_data, qual_country_data, rem_data, 'w')
# sim_all(us_team_m, us_data, qual_country_data, rem_data, 'm')
