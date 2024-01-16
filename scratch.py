# import pandas as pd
# import numpy as np

# data = pd.read_csv("distinct_apps_sim.csv")
# men = ['Stephen Nedoroscik', 'Curran Phillips', 'Brody Malone', 'Paul Juda', 'Brandon Briones', 'Vitaliy Guimaraes', 'Frederick Richard', 'Khoi Young', 'Asher Hong', 'Connor Mccool']
# print(data[data["FullName"] == 'Stephen Nedoroscik'])

# def avg(m):
#     d = data[data["FullName"] == m]
#     return d.iloc[:,4:501].mean().mean()

# for m in men:
#     print(avg(m))

# ('Curran Phillips', 'Brody Malone', 'Paul Juda', 'Frederick Richard') 6.96

# ('Stephen Nedoroscik', 'Curran Phillips', 'Brody Malone', 'Paul Juda')
# ('Stephen Nedoroscik', 'Curran Phillips', 'Brody Malone', 'Khoi Young')
# ('Curran Phillips', 'Brody Malone', 'Paul Juda', 'Khoi Young')
# ('Curran Phillips', 'Brody Malone', 'Paul Juda', 'Asher Hong')
# ('Curran Phillips', 'Brody Malone', 'Frederick Richard', 'Khoi Young')
# ('Curran Phillips', 'Brody Malone', 'Vitaliy Guimaraes', 'Frederick Richard')

import pandas as pd
import numpy as np
from itertools import combinations
import matplotlib.pyplot as plt

og_data = pd.read_csv('preprocess.csv')
data = pd.read_csv('distinct_apps_sim.csv')

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

# # Men and women athletes we are assuming to go to the olympics for our simulation
# qual_country_data = data[(data["FullName"].isin(qual_athletes_w) |
#                           data["FullName"].isin(qual_athletes_m))]

#######################################################################################################################
# USA top athletes contenders
us_data = data[(data["Country"] == 'USA')]
# top 10 women:

USA_athletes_w = og_data[(og_data["Country"]=='USA') & (og_data["Gender"] == 'w')]['FullName'].unique()
#print(USA_athletes_w)

USA_athletes_scores_w = og_data[(og_data["Country"]=='USA') & (og_data["Gender"] == 'w')]
USA_athletes_w = USA_athletes_scores_w.groupby('FullName')['Score'].mean().nlargest(10).index

qual_USA_w = list(USA_athletes_w)

# top 10 men:

USA_athletes_m = og_data[(og_data["Country"]=='USA') & (og_data["Gender"] == 'm')]['FullName'].unique()
#print(USA_athletes_m)


USA_athletes_scores_m = og_data[(og_data["Country"]=='USA') & (og_data["Gender"] == 'm')]
USA_athletes_m = USA_athletes_scores_m.groupby('FullName')['Score'].mean().nlargest(10).index

qual_USA_m = list(USA_athletes_m)

#######################################################################################################################

# dictionary for individual 36 athletes
athletes_36_w = {}

# find individual AA qualifiers by criteria 3 from Germany, Mexico, and Hungary
ger_w = og_data[(og_data["Country"]=='GER') & (og_data["Gender"] == 'w')]
mex_w = og_data[(og_data["Country"]=='MEX') & (og_data["Gender"] == 'w')]
hun_w = og_data[(og_data["Country"]=='HUN') & (og_data["Gender"] == 'w')]
crit_3_w = []
crit_3_w += list(ger_w.groupby('FullName')['Score'].mean().nlargest(1).index)
crit_3_w += list(mex_w.groupby('FullName')['Score'].mean().nlargest(1).index)
crit_3_w += list(hun_w.groupby('FullName')['Score'].mean().nlargest(1).index)

# store in AA list in dictionary
athletes_36_w['AA'] = crit_3_w

# store individual AA qualifiers by cirteria 4
athletes_36_w['AA'] += ['Kaylia Nemour', 'Pauline Schaefer betz', 'Alexa Moreno',
                      'Filipa Martins', 'Aleah Finnegan', "Bettina Lili Czifra",
                      'Alba Petisco', 'Anna Lashchevska', 'Lena Bickel',
                      'Hillary Heron', 'Caitlin Rooskrantz', 'Sona Artamonova',
                      'Lihie Raz', 'Lucija Hribar']

# store inidividual apps by criteria 5
athletes_36_w['VT1'] = ['Csenge Maria Bacskay']
athletes_36_w['VT2'] = ['Csenge Maria Bacskay']
athletes_36_w['UB'] = ['Ahtziri Sandoval']
athletes_36_w['BB'] = ['Ana Perez']
athletes_36_w['FX'] = ['Sarah Voss']

rem_og_data = og_data[((~og_data["Country"].isin(qual_countries_w)) &
                (~og_data["Country"].isin(qual_countries_m)) &
                (og_data["Country"] != 'USA'))]

# finding individual app qualifiers by criteria 6
vt_ind_w = rem_og_data[(rem_og_data["Apparatus"]=='VT') & (rem_og_data["Gender"] == 'w')]
athletes_36_w['VT1'] += list(vt_ind_w.groupby('FullName')['Score'].mean().nlargest(2).index)

athletes_36_w['VT2'] += list(vt_ind_w.groupby('FullName')['Score'].mean().nlargest(2).index)

ub_ind_w = rem_og_data[(rem_og_data["Apparatus"]=='UB') & (rem_og_data["Gender"] == 'w')]
athletes_36_w['UB'] += list(ub_ind_w.groupby('FullName')['Score'].mean().nlargest(2).index)

bb_ind_w = rem_og_data[(rem_og_data["Apparatus"]=='BB') & (rem_og_data["Gender"] == 'w')]
athletes_36_w['BB'] += list(bb_ind_w.groupby('FullName')['Score'].mean().nlargest(2).index)

fx_ind_w = rem_og_data[(rem_og_data["Apparatus"]=='FX') & (rem_og_data["Gender"] == 'w')]
athletes_36_w['FX'] += list(fx_ind_w.groupby('FullName')['Score'].mean().nlargest(2).index)

# host country place
athletes_36_w['AA'] += ['Rifda Irfanaluthfi']


# finding individual AA qualifiers by criteria 7 + universality place --> 5 spots
# 1 person who already qualified

athletes_36_w['AA'] += ['Luisa Blanco']

qual_indivs_w = athletes_36_w['AA'] + athletes_36_w['VT1'] + athletes_36_w['UB'] + athletes_36_w['BB'] + athletes_36_w['FX']

# find countries that already qualified
qual_countries_w += ['USA']
for athlete in qual_indivs_w:
  athlete_country = og_data[og_data['FullName'] == athlete]["Country"].iloc[0]
  if athlete_country not in qual_countries_w:
    qual_countries_w.append(athlete_country)

# remove those countries
temp_data_w = og_data.copy()
temp_data_w = temp_data_w[(temp_data_w['Gender'] == 'w')]


for c in qual_countries_w:
  indexes = temp_data_w.index[temp_data_w["Country"] == c].tolist()
  temp_data_w.drop(indexes, axis = 0,inplace=True)

rem_aths_w = list(temp_data_w.groupby('FullName')['Score'].mean().nlargest(5).index)

athletes_36_w['AA'] += rem_aths_w

ahthletes_36_w_names = qual_indivs_w + rem_aths_w

#######################################################################################################################

# dictionary for individual 36 athletes
athletes_36_m = {}

# find individual AA qualifiers by criteria 3 from Brazil, Korean, Belgium
bra_m = og_data[(og_data["Country"]=='BRA') & (og_data["Gender"] == 'm')]
kor_m = og_data[(og_data["Country"]=='KOR') & (og_data["Gender"] == 'm')]
bel_m = og_data[(og_data["Country"]=='BEL') & (og_data["Gender"] == 'm')]
crit_3_m = []
crit_3_m += list(bra_m.groupby('FullName')['Score'].mean().nlargest(1).index)
crit_3_m += list(kor_m.groupby('FullName')['Score'].mean().nlargest(1).index)
crit_3_m += list(bel_m.groupby('FullName')['Score'].mean().nlargest(1).index)

# store in AA list in dictionary
athletes_36_m['AA'] = crit_3_m

# store individual AA qualifiers by cirteria 4
athletes_36_m['AA'] += ['Milad Karimi', 'Artem Dolgopyat', 'Artur Davtyan',
                        'Krisztofer Meszaros', 'Junho Lee', 'Diogo Soares',
                        'Luka Van den keybus', 'Andrei Muntean']

# store inidividual apps by criteria 5
athletes_36_m['FX'] = ['Carlos Edriel Yulo']
athletes_36_m['PH'] = ['Mc Rhys Clenaghan']
athletes_36_m['SR'] = ['Eleftherios Petrounias']
athletes_36_m['VT1'] = ['Kevin Penev']
athletes_36_m['VT2'] = ['Kevin Penev']
athletes_36_m['PB'] = ['Noah Kuavita']
athletes_36_m['HB'] = ['Tin Srbic']

# finding individual app qualifiers by criteria 6
vt_ind_m = rem_og_data[(rem_og_data["Apparatus"]=='VT') & (rem_og_data["Gender"] == 'm')]
athletes_36_m['VT1'] += list(vt_ind_m.groupby('FullName')['Score'].mean().nlargest(2).index)
athletes_36_m['VT2'] += list(vt_ind_m.groupby('FullName')['Score'].mean().nlargest(2).index)

pb_ind_m = rem_og_data[(rem_og_data["Apparatus"]=='PB') & (rem_og_data["Gender"] == 'm')]
athletes_36_m['PB'] += list(pb_ind_m.groupby('FullName')['Score'].mean().nlargest(2).index)

hb_ind_m = rem_og_data[(rem_og_data["Apparatus"]=='HB') & (rem_og_data["Gender"] == 'm')]
athletes_36_m['HB'] += list(hb_ind_m.groupby('FullName')['Score'].mean().nlargest(2).index)

fx_ind_m = rem_og_data[(rem_og_data["Apparatus"]=='FX') & (rem_og_data["Gender"] == 'm')]
athletes_36_m['FX'] += list(fx_ind_m.groupby('FullName')['Score'].mean().nlargest(2).index)

sr_ind_m = rem_og_data[(rem_og_data["Apparatus"]=='SR') & (rem_og_data["Gender"] == 'm')]
athletes_36_m['SR'] += list(sr_ind_m.groupby('FullName')['Score'].mean().nlargest(2).index)

ph_ind_m = rem_og_data[(rem_og_data["Apparatus"]=='PH') & (rem_og_data["Gender"] == 'm')]
athletes_36_m['PH'] += list(ph_ind_m.groupby('FullName')['Score'].mean().nlargest(2).index)

# host country place
france_info = og_data[(og_data["Country"] == 'FRA') & (og_data['Gender'] == 'm')]
athletes_36_m['AA'] += list(france_info.groupby('FullName')['Score'].mean().nlargest(1).index)



# finding individual AA qualifiers by criteria 7 + universality place --> 5 spots
# 1 person who already qualified
athletes_36_m['AA'] += ['Audrys Nin']

qual_indivs_m = athletes_36_m['AA'] + athletes_36_m['VT1'] + athletes_36_m['HB'] + athletes_36_m['PB'] + athletes_36_m['FX']
qual_indivs_m += athletes_36_m['PH'] + athletes_36_m['SR']

# find countries that already qualified
qual_countries_m += ['USA']
for athlete in qual_indivs_m:
#   print(athlete)
  athlete_country = og_data[og_data['FullName'] == athlete]["Country"].iloc[0]
  if athlete_country not in qual_countries_m:
    qual_countries_m.append(athlete_country)

# remove those countries
temp_data_m = og_data.copy()
temp_data_m = temp_data_m[(temp_data_m['Gender'] == 'm')]


for c in qual_countries_m:
  indexes = temp_data_m.index[temp_data_m["Country"] == c].tolist()
  temp_data_m.drop(indexes, axis = 0,inplace=True)

rem_aths_m = list(temp_data_m.groupby('FullName')['Score'].mean().nlargest(5).index)

athletes_36_m['AA'] += rem_aths_m

ahthletes_36_m_names = qual_indivs_m + rem_aths_m

#######################################################################################################################

# sample from an athlete's history n times for an apparatus in a round

def sample_country(country_data):
    row = data.sample(1)
    sim_i = np.random.randint(1, 501)
    score = row[f'sim_{sim_i}'].iloc[0]
    return score

#######################################################################################################################

# retrieve athlete score from lmer data with index sim_i

def get_score(data, athlete, app):
    sim_i = np.random.randint(1, 501)
    athlete_app_data = data[(data['FullName'] == athlete)
                            & (data['Apparatus'] == app)]
    athlete_country = data[data['FullName'] == athlete]["Country"].iloc[0]
    if athlete_app_data.empty:
        # draw from country's distribution if no data exists
        country_app_data = data[(data["Country"] == athlete_country) & (
            data['Apparatus'] == app)]
        if len(country_app_data) > 0:
            athlete_app_round_score = sample_country(country_app_data)
        else:
            athlete_app_round_score = 0
    else:
        athlete_app_round_score = athlete_app_data[f'sim_{sim_i}'].iloc[0]
    return (athlete_app_round_score, athlete_country)

#######################################################################################################################

# input of app_indiv
# {FX: {athlete1: {score: _, d_score: _, e_score: _, country:_}, athlete2: {scores}, ...}, UB {athlete1: {scores}, ...}, ...}
# output qual_dict for individual AA
# {athlete1: {app1: {score: _, d_score: _, e_score: _}, app2: {scores}, ..}, athlete2: {...}}


def make_indiv_AA_dict(app_indiv, teams_names, indiv_rem_qual_names):
    app_indiv['VT'] = app_indiv['VT1']
    athletes = teams_names + indiv_rem_qual_names
    AA_dict = dict()
    for athlete in athletes:
        athlete_dict = dict()
        for app in app_indiv:
            if not app == 'VT1':
                app_data = app_indiv[app][athlete]
                athlete_dict[app] = app_data
                AA_dict[athlete] = athlete_dict
    return AA_dict


# output for team AA
# {country: {athlete: {app: (score)}}}
def make_team_AA_dict(app_indiv, teams_names):
    app_indiv['VT'] = app_indiv['VT1']
    teams_data = data[data["FullName"].isin(teams_names)]
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
    return team_AA

#######################################################################################################################


def sim_qual(curr_combo, data, gender):
    # VT1 counts for individual_AA and team_AA
    # VT1 and VT2 count for indiv_App, averaged
    # pg 43/171
    # https://www.gymnastics.sport/publicdir/rules/files/en_2022-2024%20WAG%20COP.pdf

    # determine relevant apparatuses
    if gender == 'w':
        apps = ['FX', 'BB', 'UB', 'VT1', 'VT2']
        athletes_36 = athletes_36_w
        athlete_36_names = ahthletes_36_w_names
        qual_country_names = qual_athletes_w
    else:
        apps = ['FX', 'PH', 'PB', 'HB', 'SR', 'VT1', 'VT2']
        athletes_36 = athletes_36_m
        athlete_36_names = ahthletes_36_m_names
        qual_country_names = qual_athletes_m

    # get team names
    teams_names = list(curr_combo) + qual_country_names
    teams_data =  data[data['FullName'].isin(teams_names)]
    app_dict = dict()  # dictionary to track results for each app
    app_indiv = dict()  # track each athlete's performance
    indiv_rem_qual_names = []

    # sampling for qualifying teams

    for app in apps:
        app_dict[app] = dict()
        # loop through all the unique athletes
        for athlete in teams_data["FullName"].unique():
          # sample from merged VT
            if app == 'VT1' or app == 'VT2':
                app_dict[app][athlete] = get_score(data, athlete, 'VT')
            else:
                app_dict[app][athlete] = get_score(data, athlete, app)

        # sampling for 36 individuals
        app_scores_dict = dict()
        # qualifiers for each apparatus
        for athlete in athletes_36[app]:
            if app == 'VT1' or app == 'VT2':
                app_dict[app][athlete] = get_score(data, athlete, 'VT')
            else:
                app_dict[app][athlete] = get_score(data, athlete, app)
        # qualifiers for AA
        for athlete in athletes_36['AA']:
            indiv_rem_qual_names.append(athlete)
            if app == 'VT1' or app == 'VT2':
                app_dict[app][athlete] = get_score(data, athlete, 'VT')
            else:
                app_dict[app][athlete] = get_score(data, athlete, app)
        if app == 'VT2':
            app_dict['VT'] = dict()
            for athlete in app_dict['VT2']:
                vt1_score, country = app_dict['VT1'][athlete]
                vt2_score, country = app_dict['VT2'][athlete]
                app_dict['VT'][athlete] = (np.mean((vt1_score, vt2_score)), country) 
        for athlete, scores in app_dict[app].items():
            app_scores_dict[athlete] = {"Score": scores[0], 
                                        "Country": scores[1]}
        app_indiv[app] = app_scores_dict
    indiv_AA = make_indiv_AA_dict(app_indiv, teams_names, indiv_rem_qual_names)
    team_AA = make_team_AA_dict(app_indiv, teams_names)
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
    sorted_athletes = sorted(athlete_scores_sum.items(), key=lambda item: item[1]["Score"], reverse=True)
    country_counts = dict()
    final_athletes = []
    for athlete, score in sorted_athletes:
        country = score["Country"]
        if len(final_athletes) < n:
            country_counts[country] = country_counts.get(country, 0) + 1
            if country_counts[country] < 3:
                final_athletes.append(athlete)
    return final_athletes


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
        countries_scores[country] = sum(
            country_total.values())  # find team AA score

    # select the 8 teams with the highest team AA scores
    countries_scores = dict(sorted(countries_scores.items(),
                                   key=lambda item: item[1], reverse=True)[:n])
    advance_team_AA = dict()  # for the teams that advance, get the top 3 athletes
    for country in countries_scores:
        advance_team_AA[country] = list(all_countries_totals[country])

    # {Country 1: [ath1, ath2, ath3], ... , Country 8: [...]}
    return advance_team_AA


#######################################################################################################################
# Finals

def sim_indiv_app_final(indiv_app_qual, data, gender):
    # outputs a winning dictionary of each apparatus and the winning scores of of each athlete for that app
    if gender == 'w':
        apps = ['FX', 'BB', 'UB', 'VT1', 'VT2']
    else:
        apps = ['FX', 'PH', 'PB', 'HB', 'SR', 'VT1', 'VT2']

    # get top 8 from qualifications first
    final_athletes = advance_indiv_app(indiv_app_qual, 8)

    # {FX: [ath1, ath2, ..., ath8], ... VT: [...]}

    app_dict = dict()
    indiv_app_final = dict()

    for app in apps:
        app_dict[app] = dict()
        # loop through all the unique athletes
        if app == 'VT1' or app == 'VT2':
            athletes = final_athletes['VT']
        else:
            athletes = final_athletes[app]
        for athlete in athletes:
            if app == 'VT1' or app == 'VT2':
                app_dict[app][athlete] = get_score(data, athlete, 'VT')
            else:
                app_dict[app][athlete] = get_score(data, athlete, app)
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


def sim_indiv_AA_final(indiv_AA_qual, data, gender):
    # outputs a dictionary of winning athletes and a tuple of their score sums
    if gender == 'w':
        apps = ['FX', 'BB', 'UB', 'VT']
    else:
        apps = ['FX', 'PH', 'PB', 'HB', 'SR', 'VT']

    # get top 24 from qualifications first
    final_athletes = advance_indiv_AA(indiv_AA_qual, 24)

    athlete_dict = dict()

    for athlete in final_athletes:
        athlete_dict[athlete] = dict()
        for app in apps:
            score, country = get_score(data, athlete, app)
            athlete_dict[athlete][app] = {'Score': score,
                                          "Country": country}

    winners_list = advance_indiv_AA(athlete_dict, 3)

    return winners_list


def sim_team_AA_final(team_AA_qual, data, gender):
    # outputs a list of countries
    if gender == 'w':
        apps = ['FX', 'BB', 'UB', 'VT1']
    else:
        apps = ['FX', 'PH', 'PB', 'HB', 'SR', 'VT1']

    # {Country 1: [ath1, ath2, ath3], ... Country 8: [...]}
    final_teams = advance_team_AA(team_AA_qual, 8)

    # simulate these individuals for the advancing countries again

    team_dict = dict()

    for country in final_teams:
        team_dict[country] = dict()
        for athlete in final_teams[country]:
            team_dict[country][athlete] = dict()
            for app in apps:
                if app == 'VT1':
                    scores = get_score(data, athlete, 'VT')
                else:
                    scores = get_score(data, athlete, app)
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
    weighted_medal_count = 0
    #medal_count = 0

    for app in res_indiv_app:
        athletes = res_indiv_app[app]
        for athlete in curr_combo:
            if athlete in athletes:
                medal_index = athletes.index(athlete)
                #medal_count += 1
                weighted_medal_count += 3 - medal_index
    x = weighted_medal_count
    for athlete in res_indiv_AA:
        if athlete in curr_combo:
            medal_index = res_indiv_AA.index(athlete)
            weighted_medal_count += 3 - medal_index
    y = weighted_medal_count - x
    countries = list(res_team_AA.keys())
    # Get the index of the country in the list and calculate the weighted score
    if 'USA' in countries:
        index = countries.index('USA')
        weighted_medal_count += 3 - index
    z = weighted_medal_count - x - y
    return x, y, z, weighted_medal_count


def sim_all(curr_combo, data, gender):
    data = data[data["Gender"] == gender]
    curr_medals = []
    indiv_app_medals_list = []
    indiv_aa_medals_list = []
    team_aa_medals_list = []
    for i in range(100):
        # store qualifying round data
        indiv_app_qual, indiv_AA_qual, team_AA_qual = sim_qual(curr_combo, data, gender)
        # simulate finals and count medals won by team USA players in each event

        res_indiv_app = sim_indiv_app_final(indiv_app_qual, data, gender)

        res_indiv_AA = sim_indiv_AA_final(indiv_AA_qual, data, gender)

        res_team_AA = sim_team_AA_final(team_AA_qual, data, gender)

        x, y, z, curr = (count_medals(res_indiv_app,
                                    res_indiv_AA, res_team_AA, curr_combo))
        indiv_app_medals_list.append(x)
        indiv_aa_medals_list.append(y)
        team_aa_medals_list.append(z)    
        curr_medals.append(curr)

    # curr_medals /= 100  # average medals for curr combo
    return [(np.mean(indiv_app_medals_list), np.mean(indiv_aa_medals_list), np.mean(team_aa_medals_list), np.mean(curr_medals)),
            [np.std(indiv_app_medals_list)/10, np.std(indiv_aa_medals_list)/10, np.std(team_aa_medals_list)/10, np.std(curr_medals)/10]]

team1 = ["Simone Biles", "Skye Blakely", "Jordan Chiles", "Shilese Jones"]
team2 = ['Simone Biles', 'Shilese Jones', 'Jade Carey', 'Konnor Mcclain']

[(indiv_app_medal_count, indiv_aa_medal_count, team_aa_medal_count, total), errors] = sim_all(team1, data, "w")
# [(indiv_app_medal_count, indiv_aa_medal_count, team_aa_medal_count, total), errors] = sim_all(team2, data, "w")

# Plotting
categories = ['Indiv App', 'Indiv AA', 'Team AA', 'Total']
medal_counts = [indiv_app_medal_count, indiv_aa_medal_count, team_aa_medal_count, total]
plt.bar(categories, medal_counts, color=['blue', 'green', 'orange', 'red'], yerr=errors, capsize=5)
plt.xlabel('Medal Categories')
plt.ylabel('Number of Medals')
plt.title('Medal Breakdown for Optimal Team (Simone Biles, Shilese Jones, Jade Carey, Konnor Mcclain)')
plt.show()


def greatest_wrapper_of_all():

    (w_results, w_medals) = sim_wrapper('w')
    print(f"Women's Team: {w_results}")
    print(f"Women's Medals: {w_medals}")

    (m_results, m_medals) = sim_wrapper('m')
    print(f"Men's Team: {m_results}")
    print(f"Men's Medals: {m_medals}")
    return


# womens: ['Simone Biles', 'Shilese Jones', 'Jade Carey', 'Konnor Mcclain']
# mens: 
#####################################################################################################################

greatest_wrapper_of_all()
