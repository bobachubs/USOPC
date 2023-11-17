# break ties
def tie_breaker(data, num_aths):
#   check for how many top players have the same scores
#   break ties by looking at E score first
#   break ties by look at D score first
#   filter data accordingly
  return data


# determine who wins --> might be able to include this in advance_to_finals
# if we use more conditionals and a boolean flag to toggle between finals and
# winners
def find_winners(results, gender, event):
  if gender == w: apps = [FX, ..., VT2] # womens apps
  else: apps [FX .... UB]  # mens apps
  if event == indiv_app:
    for app in apps:
    #   sort by decreasing score
    #   check if 3rd player and 4th player have same score. IF they do not then
    #   take the top 8 players. If they do have tie then call helper function to
    #   break tie.
  elif event == indiv_AA:
    # sum all scores for all apps
    # sort by decreasing score
    # check if 3rd player and 4th player have same score. If they do not then
    #   take the top 8 players. If they do have tie then call helper function to
    #   break tie.
  elif event == team_AA:
#     sum each athletes score
#     sum all scores for each country to get team AA score and store in sep dict
#    check if 3rd team and 4th team have same score. IF they do not then
#       take the top 3 teams. If they do have tie then call helper function to
#       break tie
  return winners


# determine who advances to the final round for a given event
def advance_to_finals(qual_dict, gender, event):
  if gender == w: apps = [FX, ..., VT2] # womens apps
  else: apps [ FX .... UB]  # mens apps
  if event == indiv_app:
    for app in apps:
      sort by decreasing score
      check if 7th player and 8th player have same score. IF they do not then
      take the top 8 players. Need to account for max 2/country. If they do have
      tie then call helper function to break tie.
  elif event == indiv_AA:
    sum all scores for all apps
    sort by decreasing score
    check if 24th player and 25th player have same score. IF they do not then
    take the top 24 players. Need to account for max 2/country. If they do have
    tie then call helper function to break tie.
  elif event == team_AA:
    sum each athletes score
    sum top 3 scores for each country to get team AA score and store in sep dict
    check if 7th team and 8th team have same score. IF they do not then take
      the top 8 teams. Need to account for max 3/country. If they do have tie
      then call helper function to break tie.
  return final_athletes


# used to simulate one round of the competition
def sim_round(gender, data): # what we have so far
  if gender == w: apps = [FX, ..., VT2] # womens apps
  else: apps [ FX .... UB]  # mens apps
  results = {} # to store simulation scores
  for app in app:
    for athlete in data:
      draw score from the player or country distribution
      store athlete name and score, D score, and E score into results
  return results


# simulate team AA finals
def sim_team_AA(combo, qual_dict, gender):
  # determine which athletes advance
  final_data = advance_to_finals(qual_dict, gender, team_AA)
  # simulate scores
  results = sim_round(gender, qual_dict)
  results = find_winners(results, gender, team_AA)
  medals = 0
  medals_dict = {}
  # store medals info in medals_dict for athletes in our combo
    for athlete in combo:
      medals_dict = create dictionary that has gold, silver, bronze, and medals
      as keys and stores how many of each are earned by team USA players
  return medals


# simulate individual AA finals
def dsim_inidiv_AA(combo, qual_dict, gender):
  # determine which athletes advance
  final_data = advance_to_finals(qual_dict, gender, indiv_AA)
  # simulate scores
  results = sim_round(gender, qual_dict)
  results = find_winners(results, gender, indiv_AA)
  medals = 0
  medals_dict = {}
  # store medals info in medals_dict for athletes in our combo
    for athlete in combo:
      medals_dict = create dictionary that has gold, silver, bronze, and medals
      as keys and stores how many of each are earned by team USA players
  return medals


# simulate individual apps finals
def sim_indiv_app(combo, qual_dict, gender):
  # determine which athletes advance
  final_data = advance_to_finals(qual_dict, gender, indiv_app)
  #simulate scores
  results = sim_round(gender, qual_dict)
  results = find_winners(results, gender, indiv_app)
  medals = 0
  medals_dict = {}
  # store medals info in medals_dict for athletes in our combo
    for athlete in combo:
      medals_dict = create dictionary that has gold, silver, bronze, and medals
      as keys and stores how many of each are earned by team USA players
  return medals




# main function to call our simulation
# pass in athletes
def sim_team(athlete 1, athlete 2, athlete 3, athlete 4, athlete 5, gender):
  combos = [........ list of combos of 4 athletes]
  top_aths = []
  max = 0
    for combo in combos:
    filter out USA athletes in data that are not in combo
    for i in range 10000:
    qual_dict = sim_round(gender, data) # store qualifying round data
    # simulate finals and count medals won by team USA players in each event
    medal_count = sim_indiv_app(combo, qual_dict, gender)["medal"] +
                  sim_indiv_AA(combo, qual_dict, gender)["medal"] +
                    sim_team_AA(combo, qual_dict, gender)["medal"]
    medal /= 1000
    # track highest avg. medal count and which 4 athletes produced it
    if medal_count > max: max = medal count, top_aths = combo
  print max
  print top_aths
  return max, top_aths


# TODO: data preprocessing: only keep USA athletes or teams of 4 for top 12
# countries and filter by gender
