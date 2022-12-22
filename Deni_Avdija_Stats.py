# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 16:51:13 2022

@author: Yehuda Yungstein yehudayu@gmail.com
"""
import streamlit as st
#@st.cache
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import nba_api
# every year avg data:
from nba_api.stats.endpoints import playercareerstats
import matplotlib.pyplot as plt



######################## All years career stats ########################

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
career_df = career_df.round(2)

######################## Every game stats ########################
def read_data(path):
    df = pd.read_csv(path)
    # skip first col
    df = df[df.columns[1:]]
    
    return df

# Create df for every season:
path_20 = "C:\downloads_py\Streamlit\Deni_Avdija_Stats_app\Deni_2020-21.csv"
path_21 = "C:\downloads_py\Streamlit\Deni_Avdija_Stats_app\Deni_2021-22.csv"
path_22 = "C:\downloads_py\Streamlit\Deni_Avdija_Stats_app\Deni_2022-23_1-32.csv"

df_2020 = read_data(path_20)
df_2021 = read_data(path_21)
df_2022 = read_data(path_22)

# Add update data from 22/12/2022:

######################## Streamlit  ########################

#### Seasonal stats####
new_title = '<p style="font-family:sans-serif;text-align: center; color:magenta; font-size: 50px;font-weight:bold"> Deni Avdija Statistics App</p>'
st.markdown(new_title, unsafe_allow_html=True)
st.markdown('''
            ----
            ''')
st.header('Seasonal Stats')
#st.table(career_df.style.format({"E": "{:.2f}"}))
st.dataframe(career_df.style.format(subset=career_df.columns[4:], formatter="{:.2f}"))

# Choosecolumn and present bar plot:
columns = career_df.columns[4:].tolist()
selected_column = st.selectbox("Select parameter", columns,key="1")
fig = px.bar(career_df, x=career_df.index, y=selected_column,width=700)
fig.update_traces(marker_color='#FF00FF')
fig.update_layout(font=dict(size=18))
st.plotly_chart(fig)

#### Per Game stats####
st.header('Per Game Stats')

season_dict = {'2020-21':df_2020,'2021-22':df_2021,'2022-23':df_2022}
selected_season = st.selectbox("Select Season", list(season_dict.keys()),key="3")
# Present df by the dict
df = season_dict[selected_season]
st.dataframe(df)
# user choose column to present in graph:
columns1 = df.columns[3:]
selected_column1 = st.selectbox("Select parameter", columns1,key="4")
# Create a line plot
chart = st.line_chart(data =df, x='DATE',y=selected_column1)
# Rolling average:
rolling = st.slider('Rolling Avg value',1, 10, 1)
chart = st.line_chart(df[selected_column1].rolling(rolling).mean())