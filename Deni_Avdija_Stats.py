# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 16:51:13 2022
"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import nba_api
from nba_api.stats.endpoints import playercareerstats

#cache requests
@st.cache(allow_output_mutation=True)
def get_seasonal_stats(season):
    api_url= "https://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=PerGame&Scope=S&Season=" + season + "&SeasonType=Regular%20Season&StatCategory=PTS"
    r = requests.get(api_url).json()
    table_headers = r['resultSet']['headers'] # headers for df
    df_colums = ['Year'] + table_headers
    df = pd.DataFrame(columns=df_colums)

    df1= pd.DataFrame(r['resultSet']['rowSet'],columns = table_headers)
    df2 = pd.DataFrame({'Year':[season for i in range(len(df1))]})
    df3 = pd.concat([df2,df1],axis=1)

    df = df3[['Year', 'RANK', 'PLAYER', 'TEAM', 'GP',
           'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
           'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PTS',
           'EFF']]

    return df

#get seasonal stats
years = ['2020-21','2021-22','2022-23']
df = pd.DataFrame(columns=['Year', 'RANK', 'PLAYER', 'TEAM', 'GP',
       'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
       'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PTS',
       'EFF'])

for year in years:
    df = pd.concat([df, get_seasonal_stats(year)], axis=0)

# Deni data:
career_df = df[df['PLAYER']=='Deni Avdija'].reset_index(drop=True)
career_df = career_df.set_index('Year')
# round the df:
career_df = career_df.round(3)

######################## Every game stats ########################
@st.cache
def read_data(path):
    df = pd.read_csv(path)
    df = df[df.columns[1:]]
    df['MIN'] = df['MIN'].str.split(':').str[0].str.split('.').str[0].astype(int)
    return df
