library(ggplot2)
library(dplyr)
library(lme4)
library(tidyverse)


data = read.csv("test.csv")

formula <- Score ~ (1|FullName) + (1|Country) + (1|Gender) + Apparatus
mixed_model <- lmer(formula, data = data)
# print(summary(mixed_model))

# ranef(mixed_model)


# simone_plays <- data %>%
#   filter(str_detect(FullName, "Simone Biles")) %>%
#   dplyr::select('Country', 'Apparatus', 'FullName') %>%
#   # Only get the unique combinations of the explanatory variables:
#   distinct()

distinct_players <- data %>%
  dplyr::select('Country', 'Apparatus', 'Gender', 'FullName') %>%
  distinct()

athlete_sim <- simulate(mixed_model, nsim = 500, newdata = distinct_players,
                            # Tell simulate to use the random effects!
                            re.form = NULL)

dim(athlete_sim)

athlete_sim_bound <- apply(athlete_sim, 2, #apply to each column
                               # use a function that takes the max of x and 0,
                               # and the min of x and +16
                               function(x) pmax(pmin(x, 16), 0))

dim(athlete_sim_bound)

distinct_apps = bind_cols(distinct_players, athlete_sim_bound)

distinct_apps_sim <- distinct_apps %>%
  pivot_longer(cols = sim_1:sim_100,
               names_to = "sim_index", values_to = "sim_value")

write_csv(distinct_apps,
          "distinct_apps_sim.csv")


