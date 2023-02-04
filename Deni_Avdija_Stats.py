# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 16:51:13 2022

@author: Yehuda Yungstein yehudayu@gmail.com
"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import nba_api
from nba_api.stats.endpoints import playercareerstats
import matplotlib.pyplot as plt

######################## All years career stats ########################
@st.cache
def get_career_df():
    
    # Set the base URL for the NBA Stats API
    base_url = "https://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=PerGame&Scope=S&Season=2020-21&SeasonType=Regular%20Season&StatCategory=PTS"
    r = requests.get(base_url, ).json()
    table_headers = r['resultSet']['headers'] # headers for df
    df_colums = ['Year'] + table_headers
    df = pd.DataFrame(columns=df_colums)

    years = ['2020-21','2021-22','2022-23']
    for year in years:
      api_url= "https://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=PerGame&Scope=S&Season="+year+"&SeasonType=Regular%20Season&StatCategory=PTS"
      r = requests.get(api_url).json()
      df1= pd.DataFrame(r['resultSet']['rowSet'],columns = table_headers)
      df2 = pd.DataFrame({'Year':[year for i in range(len(df1))]})
      df3 = pd.concat([df2,df1],axis=1)
      df = pd.concat([df,df3],axis=0)

    df = df[['Year', 'RANK', 'PLAYER', 'TEAM', 'GP',
           'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
           'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PTS',
           'EFF']]

    # Deni data:
    career_df = df[df['PLAYER']=='Deni Avdija'].reset_index(drop=True)
    career_df = career_df.set_index('Year')
    # round the df:
    career_df = career_df.round(3)
    return career_df

career_df = get_career_df()

######################## inter-annual data ########################
@st.cache
def read_data(path):
    df = pd.read_csv(path)
    # skip first col
    df = df[df.columns[1:]]
    # Convert Minute column to int:
    df['MIN'] = df['MIN'].str.split(':').str[0].str.split('.').str[0].astype(int)
    
    return df

# Create df for every season:
path_20 = "Deni_2020-21.csv"
path_21 = "Deni_2021-22.csv"
path_22 = "Deni_2022-23_1-50.csv"

df_2020 = read_data(path_20)
df_2021 = read_data(path_21)
df_2022 = read_data(path_22)


######################## Streamlit  ########################

# Deni Avdija Statistics App
st.title("Deni Avdija Statistics App")
st.markdown("----")

# Seasonal Stats
st.header("Seasonal Stats")
st.dataframe(career_df.style.format(subset=career_df.columns[4:], formatter="{:.3f}"))

# Choose column and present bar plot
columns = career_df.columns[4:].tolist()
selected_column = st.selectbox("Select parameter", columns, key="1")
fig = px.bar(career_df, x=career_df.index, y=selected_column, width=700)
fig.update_traces(marker_color="#00265B")
fig.update_layout(font=dict(size=18))
st.plotly_chart(fig)

# Per Game Stats
st.header("Per Game Stats")

season_dict = {'2020-21': df_2020, '2021-22': df_2021, '2022-23': df_2022}
selected_season = st.selectbox("Select Season", list(season_dict.keys()), key="3")
df = season_dict[selected_season]
df = df[df.columns[1:]]
# select the last column (Date)
last_col = df.columns[-1]
# use indexing to rearrange the columns
df = df[[last_col]+list(df.columns[:-1])]
# use the index to reverse the rows order
df = df.iloc[::-1]
# Present the df
st.dataframe(df)

# User choose X-axis parameter
columns2 = df.columns
selected_column2 = st.selectbox("Select x-axis parameter (optional)", columns2, key="4", index=columns2.get_loc('DATE'))

# User choose column to present in graph
columns1 = df.columns
selected_column1 = st.selectbox("Select Y-axis parameter", columns1, key="5")

fig, ax = plt.subplots()
ax.plot(df[selected_column2], df[selected_column1],color="#00265B")
ax.scatter(df[selected_column2], df[selected_column1],color = "#C6CFD5")
ax.set_xlabel(selected_column2)
ax.set_ylabel(selected_column1)
# ax.set_title('Graph of Y-axis vs X-axis')
# Set x-ticks every 5 samples
plt.xticks(np.arange(0, len(df), 5), rotation=90)
# Add background of horizontal grid
ax.grid(axis='y', linestyle='--', alpha=0.5)


st.pyplot(fig)

# Rolling average
rolling = st.slider("Rolling avg value", 1, 10, 1)
chart = st.line_chart(df[selected_column1].rolling(rolling).mean())

# User select the last k games
k = st.slider("Select the last k games", 1, len(df), len(df))
df_k = df.iloc[-k:, :]

# User choose two columns to display in graph
columns = df_k.columns
selected_column_x = st.selectbox("Select X-axis parameter", columns)
selected_column_y = st.selectbox("Select Y-axis parameter", columns, index=columns.get_loc('DATE'))

fig, ax = plt.subplots()
ax.plot(df_k[selected_column_x], df_k[selected_column_y],color = '#E41134')
ax.scatter(df_k[selected_column_x], df_k[selected_column_y],color = "#C6CFD5")
ax.set_xlabel(selected_column_x)
ax.set_ylabel(selected_column_y)
ax.set_title(f'{selected_column_y} (last {k} games)')
plt.xticks(rotation=90)

# Add background of horizontal grid
ax.grid(axis='y', linestyle='--', alpha=0.5)

st.pyplot(fig)

# Add the average:
st.dataframe(df_k.describe().iloc[1].T)

