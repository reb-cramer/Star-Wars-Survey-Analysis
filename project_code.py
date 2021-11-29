# %%
import pandas as pd
import altair as alt
import numpy as np

url = 'https://raw.githubusercontent.com/fivethirtyeight/data/master/star-wars-survey/StarWars.csv'

# Separates the data into 2 environments for easier manipulation
dat_cols = pd.read_csv(url, encoding = "ISO-8859-1", nrows = 1).melt()
dat = pd.read_csv(url, encoding = "ISO-8859-1", skiprows =2, header = None )

# %%
# Dictionary that replaces long column names with better column names
variables_replace = {
    'Which of the following Star Wars films have you seen\\? Please select all that apply\\.':'seen',
    'Please rank the Star Wars films in order of preference with 1 being your favorite film in the franchise and 6 being your least favorite film.':'rank',
    'Please state whether you view the following characters favorably, unfavorably, or are unfamiliar with him/her.':'view',
    'Do you consider yourself to be a fan of the Star Trek franchise\\?':'star_trek_fan',
    'Do you consider yourself to be a fan of the Expanded Universe\\?\x8cæ':'expanded_fan',
    'Are you familiar with the Expanded Universe\\?':'know_expanded',
    'Have you seen any of the 6 films in the Star Wars franchise\\?':'seen_any',
    'Do you consider yourself to be a fan of the Star Wars film franchise\\?':'star_wars_fans',
    'Which character shot first\\?':'shot_first',
    r'Unnamed: \d{1,2}':np.nan,
    ' ':'_',
}

values_replace = {
    'Response':'',
    'Star Wars: Episode ':'',
    ' ':'_'
}

# Replaces column names with values in the dictionaries, and concatonates two columns into one
dat_cols_use = (dat_cols
    .assign(
        value_replace = lambda x:  x.value.str.strip().replace(values_replace, regex=True),
        variable_replace = lambda x: x.variable.str.strip().replace(variables_replace, regex=True)
    )
    .fillna(method = 'ffill')
    .fillna(value = "")
    .assign(column_names = lambda x: x.variable_replace.str.cat(x.value_replace, sep = "__").str.strip('__').str.lower())
    )

# Adds columns as columns to the rest of the dataset
dat.columns = dat_cols_use.column_names.to_list()
# %%
dat.columns
# %%
# Queries out all the instances of responses of "yes" to seen_any
work_data = dat.query('seen_any == "Yes"')

work_data
# %%
# Queries out all those who said they had seen a movie and then selected at least one movie they had seen--provides information needed for the first chart
chart_1_data = work_data.query('seen__i__the_phantom_menace == seen__i__the_phantom_menace or seen__ii__attack_of_the_clones == seen__ii__attack_of_the_clones or seen__iii__revenge_of_the_sith == seen__iii__revenge_of_the_sith or seen__iv__a_new_hope == seen__iv__a_new_hope or seen__v_the_empire_strikes_back == seen__v_the_empire_strikes_back or seen__vi_return_of_the_jedi == seen__vi_return_of_the_jedi')

chart_1_data

# Calculates the number of rows in the new dataframe--this represents the number of people who will be represented in the next chart
# Needed for calculation of percentage and for summary for GQ3
index = chart_1_data.index
number_of_rows = len(index)
print(number_of_rows)
# %%
# Filters out relevant data
chart_1_data = chart_1_data.filter(regex = 'seen__i__the_phantom_menace|seen__ii__attack_of_the_clones|seen__iii__revenge_of_the_sith|seen__iv__a_new_hope|seen__v_the_empire_strikes_back|seen__vi_return_of_the_jedi')

# Assigns new one-hot-encoded columns to who has and hasn't seen a film. Those who have are marked as a 1, and those who haven't are marked as a 0
chart_1_data = chart_1_data.assign(seen__i__number = lambda x: np.where((x.seen__i__the_phantom_menace == x.seen__i__the_phantom_menace), 1, 0)) 
chart_1_data = chart_1_data.assign(seen__ii__number = lambda x: np.where((x.seen__ii__attack_of_the_clones == x.seen__ii__attack_of_the_clones), 1, 0))
chart_1_data = chart_1_data.assign(seen__iii__number = lambda x: np.where((x.seen__iii__revenge_of_the_sith == x.seen__iii__revenge_of_the_sith), 1, 0))
chart_1_data = chart_1_data.assign(seen__iv__number = lambda x: np.where((x.seen__iv__a_new_hope == x.seen__iv__a_new_hope), 1, 0))
chart_1_data = chart_1_data.assign(seen__v__number = lambda x: np.where((x.seen__v_the_empire_strikes_back == x.seen__v_the_empire_strikes_back), 1, 0))
chart_1_data = chart_1_data.assign(seen__vi__number = lambda x: np.where((x.seen__vi_return_of_the_jedi == x.seen__vi_return_of_the_jedi), 1, 0))
# Gives us the number of rows in the dataframe
chart_1_data = chart_1_data.assign(row_count = lambda x: 1)

# Creates new dataframe based on the information in the new dataframe rows, which will create the chart
new_dataframe = pd.DataFrame({'movies': ['The Phantom Menace', 'Attack of the Clones', 'Revenge of the Sith', 'A New Hope', 'The Empire Strikes Back', 'Return of the Jedi'], 'have_seen': [chart_1_data['seen__i__number'].sum(), chart_1_data['seen__ii__number'].sum(), chart_1_data['seen__iii__number'].sum(), chart_1_data['seen__iv__number'].sum(), chart_1_data['seen__v__number'].sum(), chart_1_data['seen__vi__number'].sum()], 'row_count': [chart_1_data['row_count'].sum(), chart_1_data['row_count'].sum(), chart_1_data['row_count'].sum(), chart_1_data['row_count'].sum(), chart_1_data['row_count'].sum(), chart_1_data['row_count'].sum()]})

# Assigns key information (proportion of people who have seen the film) to new column in new dataframe
new_dataframe = new_dataframe.assign(proportion_seen = lambda x: x.have_seen / x.row_count)

# Creates a chart to display information in new dataframe
chart_1 = (alt.Chart(new_dataframe)
    .encode(
    alt.X('proportion_seen', axis=alt.Axis(format='.0%'), title = 'Percentage of Respondents who Saw Each Movie'),
    alt.Y('movies', sort=['The Phantom Menace', 'Attack of the Clones', 'Revenge of the Sith', 'A New Hope', 'The Empire Strikes Back', 'Return of the Jedi'], title = 'Movies'))
    .mark_bar()
    .properties(
        title={
            'text': ['Which \'Star Wars\' Movies Have You Seen?'], 
            'subtitle': ['Of 835 respondents who have seen any film'],
        }
    )
)

# Adds the percentage markings next to the bars on the chart
text = chart_1.mark_text(
    align = 'left',
    baseline = 'middle', 
    dx = 3).encode(
    text = alt.Text('proportion_seen:Q', format = '.0%')
)

chart_1 + text
# %% 
# Queries all respondents who reported that they watched all 6 films; information needed for second chart
chart_2_data = work_data.query('seen__i__the_phantom_menace == seen__i__the_phantom_menace and seen__ii__attack_of_the_clones == seen__ii__attack_of_the_clones and seen__iii__revenge_of_the_sith == seen__iii__revenge_of_the_sith and seen__iv__a_new_hope == seen__iv__a_new_hope and seen__v_the_empire_strikes_back == seen__v_the_empire_strikes_back and seen__vi_return_of_the_jedi == seen__vi_return_of_the_jedi')

chart_2_data

# Calculates the number of rows in the new dataframe--this represents the number of people who will be represented in the next chart
# Needed for calculation of percentage and for summary for GQ3
index = chart_2_data.index
number_of_rows = len(index)
print(number_of_rows)
# %%
chart_2_data = chart_2_data.filter(regex = 'rank__i__the_phantom_menace|rank__ii__attack_of_the_clones|rank__iii__revenge_of_the_sith|rank__iv__a_new_hope|rank__v_the_empire_strikes_back|rank__vi_return_of_the_jedi')

# Assigns new one-hot-encoded columns to who has and hasn't rated a film the highest. Those who have are marked as a 1, and those who haven't are marked as a 0
chart_2_data = chart_2_data.assign(highest_rank_i = lambda x: np.where(x.rank__i__the_phantom_menace == 1.0, 1, 0))
chart_2_data = chart_2_data.assign(highest_rank_ii = lambda x: np.where(x.rank__ii__attack_of_the_clones == 1.0, 1, 0))
chart_2_data = chart_2_data.assign(highest_rank_iii = lambda x: np.where(x.rank__iii__revenge_of_the_sith == 1.0, 1, 0))
chart_2_data = chart_2_data.assign(highest_rank_iv = lambda x: np.where(x.rank__iv__a_new_hope == 1.0, 1, 0))
chart_2_data = chart_2_data.assign(highest_rank_v = lambda x: np.where(x.rank__v_the_empire_strikes_back == 1.0, 1, 0))
chart_2_data = chart_2_data.assign(highest_rank_vi = lambda x: np.where(x.rank__vi_return_of_the_jedi == 1.0, 1, 0))
# Gives us the number of rows in the dataframe
chart_2_data = chart_2_data.assign(row_count = lambda x: 1)

# Creates new dataframe based on the information in the new dataframe rows, which will create the chart
new_dataframe = pd.DataFrame({'movies': ['The Phantom Menace', 'Attack of the Clones', 'Revenge of the Sith', 'A New Hope', 'The Empire Strikes Back', 'Return of the Jedi'], 'highest_rank': [chart_2_data['highest_rank_i'].sum(), chart_2_data['highest_rank_ii'].sum(), chart_2_data['highest_rank_iii'].sum(), chart_2_data['highest_rank_iv'].sum(), chart_2_data['highest_rank_v'].sum(), chart_2_data['highest_rank_vi'].sum()], 'row_count': [chart_2_data['row_count'].sum(), chart_2_data['row_count'].sum(), chart_2_data['row_count'].sum(), chart_2_data['row_count'].sum(), chart_2_data['row_count'].sum(), chart_2_data['row_count'].sum()]})

# Assigns key information (proportion of people who rated each film the highest) to new column in new dataframe
new_dataframe = new_dataframe.assign(hr_proportion = lambda x: x.highest_rank / x.row_count)

# Creates a chart to display information in new dataframe
chart_2 = (alt.Chart(new_dataframe)
    .encode(
    alt.X('hr_proportion', axis=alt.Axis(format='.0%'), title = 'Percentage of Respondents who Rated Each Movie the Highest'),
    alt.Y('movies', sort=['The Phantom Menace', 'Attack of the Clones', 'Revenge of the Sith', 'A New Hope', 'The Empire Strikes Back', 'Return of the Jedi'], title = 'Movies'))
    .mark_bar()
    .properties(
        title={
            'text': ['What\'s the Best \'Star Wars\' Movie?'], 
            'subtitle': ['Of 471 respondents who have seen all 6 films'],
        }
    )
)

# Adds the percentage markings next to the bars on the chart
text = chart_2.mark_text(
    align = 'left',
    baseline = 'middle', 
    dx = 3).encode(
    text = alt.Text('hr_proportion:Q', format = '.0%')
)

chart_2 + text
# %%
# New age column
age = (dat.age
    .str.replace('18-29', '18')
    .str.replace('30-44', '30')
    .str.replace('45-60', '45')
    .str.replace('> 60', '60')
    .astype('float'))
# %%
# New education column
education = (dat.education
    .str.replace('Less than high school degree', '9')
    .str.replace('High school degree', '12')
    .str.replace('Some college or Associate degree', '14')
    .str.replace('Bachelor degree', '16')
    .str.replace('Graduate degree', '20')
    .astype('float'))
# %%
# New household_income column (income_num.income_min)
income_num = (dat.household_income
    .str.split("-", expand = True)
    .rename(columns = {0: 'income_min', 1: 'income_max'})
    .apply(lambda x: x.str.replace("\$|,|\+", ""))
    .astype('float'))
# %%
# Drops all columns that have been factorized
dat = dat.drop(dat.filter(regex = 'age|education|household_income').columns, axis = 1)
# %%
# One-hot-encodes all data in dataframe
dat = pd.get_dummies(dat)
# %%
# Adds back in the factorized columns
dat = dat.assign(age = age)
dat = dat.assign(education = education)
dat = dat.assign(household_income = income_num.income_min)

dat
# %%
# Creates a new target column-finalizes the data for machine learning
dat = dat.assign(more_than_50k = lambda x: np.where(x.household_income >= 50000, 1, 0))

dat = dat.fillna(-1)
dat
# %%
from sklearn.model_selection import train_test_split

# Delineates feature and target variables. 
features = dat.drop(dat.filter(regex = 'more_than_50k|household_income').columns, axis = 1)
target = dat.filter(regex = 'more_than_50k')

# Sets up data train/test splits
train_data, test_data, train_targets, test_targets = train_test_split(features, target, test_size=.3)
# %%
from sklearn.naive_bayes import GaussianNB

# Fits to the GaussianNB classifier.
classifier = GaussianNB()
classifier.fit(train_data, train_targets)
# %%
from sklearn.tree import DecisionTreeClassifier

# Fits to the DecisionTreeClassifier classifier.
classifier = DecisionTreeClassifier(max_depth=5)
classifier.fit(train_data, train_targets)
# %%
from sklearn.ensemble import RandomForestClassifier

# Fits to the RandomForestClassifier classifier
classifier = RandomForestClassifier(criterion='entropy', max_depth=7)
classifier.fit(train_data, train_targets)
# %%
from sklearn import metrics

# Uses fitted classifier on test data, and displays results
targets_predict = classifier.predict(test_data)
print(metrics.classification_report(test_targets, targets_predict))
# %%
