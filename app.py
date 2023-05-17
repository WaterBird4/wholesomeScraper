# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

app = Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

# ########################################################
# IMPORT DATA ############################################
# ########################################################
import os
import time

files = os.listdir()
all_files = [x for x in files if str(x).startswith('all_data_')]
assert len(all_files) > 0

file_dates = {}

for val in all_files:
    filename = str(val)
    filedate = os.path.getmtime(val)
    file_dates[filename] = filedate

use_file = max(zip(file_dates.values(), file_dates.keys()))[1]

df = pd.read_csv(use_file)
# COMBINE DATE AND TIME AND CHANGE TO DATETIME OBJECT
df['filetime'] = df['filetime'].astype(str)
df.loc[df['filetime'] == '0', 'filetime'] = '0000'
df['dt'] = df['filedate'] + '-' + df['filetime']
df['dt'] = pd.to_datetime(df['dt'], format='%m-%d-%Y-%H%M')
# ADD DAY, DAY OF WEEK, WEEK, MONTH AND YEAR COLUMNS
df['day'] = df['dt'].dt.day
df['month'] = df['dt'].dt.month
df['day_of_week'] = df['dt'].dt.day_name()
df['week'] = df['dt'].dt.isocalendar().week
df['year'] = df['dt'].dt.year


# FILTER OUT EMPTY CELLS
df = df.loc[df['Strain Type'].notna()].copy()
# CHANGE FLOAT VALUES TO FLOAT OBJECTS
df.loc[df['Total THC'].notna(), 'Total THC'] = df.apply(lambda row: str(row['Total THC']).rsplit('%')[0], axis=1)
df['Total THC'] = df['Total THC'].astype(float)

df.loc[df['Total CBD'].notna(), 'Total CBD'] = df.apply(lambda row: str(row['Total CBD']).rsplit('%')[0], axis=1)
df['Total CBD'] = df['Total CBD'].astype(float)

df.loc[df['THCa'].notna(), 'THCa'] = df.apply(lambda row: str(row['THCa']).rsplit('%')[0], axis=1)
df['THCa'] = df['THCa'].astype(float)

df.loc[df['CBDa'].notna(), 'CBDa'] = df.apply(lambda row: str(row['CBDa']).rsplit('%')[0], axis=1)
df['CBDa'] = df['CBDa'].astype(float)

df.loc[df['Total CBN'].notna(), 'Total CBN'] = df.apply(lambda row: str(row['Total CBN']).rsplit('%')[0], axis=1)
df['Total CBN'] = df['Total CBN'].astype(float)

df.loc[df['Total CBG'].notna(), 'Total CBG'] = df.apply(lambda row: str(row['Total CBG']).rsplit('%')[0], axis=1)
df['Total CBG'] = df['Total CBG'].astype(float)

df.loc[df['Total CBC'].notna(), 'Total CBC'] = df.apply(lambda row: str(row['Total CBC']).rsplit('%')[0], axis=1)
df['Total CBC'] = df['Total CBC'].astype(float)

# THC LEVEL LABELS 
thc_bins = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond']

df['thc_bins'] = pd.qcut(df['Total THC'], q=5, labels=thc_bins)


# RESET INDEX
df.reset_index(inplace=True, drop=True)

# #######################################################
# EXAMPLE GRAPH: COUNTS BY STRAIN & DATE ################
# #######################################################
data_dict = {}
for g in df.groupby('dt'):
    strains = g[1].groupby('Strain Type').count()['filename'].index.tolist()
    counts = g[1].groupby('Strain Type').count()['filename'].values.tolist()
    data_dict[g[0]] = [strains, counts]

data = []
for k in data_dict.keys():
    temp = {}
    temp['type'] = 'bar'
    temp['name'] = str(k)
    temp['x'] = list(data_dict.get(k))[0]
    temp['y'] = list(data_dict.get(k))[1]
    data.append(temp)


fig2 = {'data': data, 'layout': {'title': 'Count Strains by Date'}}

# #######################################################
# SCATTER PLOT ##########################################
# #######################################################

df2 = df[['product_name', 'Strain Type', 'THCa', 'Total THC', 'CBDa', 'Total CBD', 'Total CBG', 'Total CBC', 'Total CBN']]
df2['duplicate'] = df2.duplicated(keep='last').copy()
df2 = df2.loc[df2['duplicate'] == False]
df2.reset_index(inplace=True, drop=True)


import plotly.express as px

colorscales = px.colors.named_colorscales()

fig3 = px.scatter(df2, x="Total THC", y="Total CBD", color="Total THC",color_continuous_scale=colorscales[-1])

# #######################################################
# VINTAGE REPORT ######################################## 
# #######################################################

df2.loc[df2['Total THC'].notna(), 'Total THC'] = df2.apply(lambda row: str(row['Total THC']).rsplit('%')[0], axis=1)
df2['Total THC'] = df2['Total THC'].astype(float)

df2['THC BINS'] = pd.qcut(df2['Total THC'], q=5, labels=thc_bins)

fig4 = px.pie(df2, values='Total THC', names='THC BINS', hole=0.3)
# #######################################################
# FACET PLOT ############################################
# #######################################################

fig5 = px.bar(df, x='thc_bins', y='Strain Type', color='thc_bins', barmode='group', facet_row='week', facet_col='thc_bins')


# #######################################################
# APP ###################################################
# #######################################################

app.layout = html.Div(children=[
    html.H1(children='I am a wizard!'),

    html.Div(children='''
        Count of strains available at various dates and times
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig2
    ),
    html.Div(children='''
        Total THC to Total CBD
    '''),
    dcc.Graph(
        id='Scatter Graph',
        figure=fig3
    ),
    html.Div(children='''
        Distribution of THC content in all strains available
    '''),
    dcc.Graph(
        id='Thc Bins',
        figure=fig4
    ),
    dcc.Graph(
        id='facet_plot',
        figure=fig5
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
