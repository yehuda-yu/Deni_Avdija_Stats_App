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
import os
from PIL import Image
from nba_api.stats.endpoints import playercareerstats
import matplotlib.pyplot as plt

######################## All years career stats ########################
# Set configutation
url = "https://cdn.nba.com/headshots/nba/latest/1040x760/1630166.png"
response = requests.get(url)
script_directory = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(script_directory, 'favicon.png'), 'wb') as f:
    f.write(response.content)
icon = Image.open(os.path.join(script_directory, 'favicon.png'))
st.set_page_config("Deni Stats Explorer",icon)

@st.cache_data
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
@st.cache_data
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
path_22 = "Deni_2022-23.csv"

df_2020 = read_data(path_20)
df_2021 = read_data(path_21)
df_2022 = read_data(path_22)


######################## Streamlit  ########################

# Deni Avdija Statistics App
st.markdown('<img src=\"https://cdn.nba.com/headshots/nba/latest/1040x760/1630166.png" style=\"width:150px\"> ' , 
    unsafe_allow_html=True)
st.title("Deni Avdija Statistics App")
st.markdown("----")

# Seasonal Stats
st.header("Seasonal Stats")
st.dataframe(career_df.style.format(subset=career_df.columns[4:], formatter="{:.3f}"))

# Choose column and present bar plot
columns = career_df.columns[4:].tolist()
selected_column = st.selectbox("Select parameter", columns, key="1")
fig = px.bar(career_df, x=career_df.index, y=selected_column, width=700)
# fig.update_traces(marker_color="#00265B")
fig.update_traces(marker_color="#00265B", textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
fig.update_layout(font=dict(size=18))
st.plotly_chart(fig)

# Per Game Stats
st.header("Per Game Stats")

season_dict = {'2020-21': df_2020, '2021-22': df_2021, '2022-23': df_2022}
selected_season = st.selectbox("Select Season", list(season_dict.keys()), key="3",index=len(season_dict.keys())-1)
df = season_dict[selected_season]
df = df[df.columns[1:]].reset_index(drop=True)
# select the last column (Date)
last_col = df.columns[-1]
# use indexing to rearrange the columns
df = df[[last_col]+list(df.columns[:-1])]
# use the index to reverse the rows order
df = df.iloc[::-1]
# Present the df
st.dataframe(df)

# User choose column to present in graph
columns1 = df.columns
selected_column1 = st.selectbox("Select Y-axis parameter", columns1, key="5", index=columns1.get_loc('PTS'))

df['Game Number'] = df.index+1
selected_column2 = 'Game Number'

fig1 = px.line(df, selected_column2, y=selected_column1, markers=True,)
# Set the line color and width
fig1.update_traces(line_color='#d9295a', line_width=3)
# Set the marker color
fig1.update_traces(marker_color='#3f2646')
fig1.update_layout(xaxis_title='Game Number', yaxis_title=selected_column1)
# Set the x-axis tick mode, starting position, and step size
fig1.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=5, tickfont=dict(size=16)))
# Set the y-axis tick mode and number of ticks
fig1.update_layout(yaxis=dict(tickfont=dict(size=16)))
st.plotly_chart(fig1)

# Rolling average
#rolling = st.slider("Rolling avg value", 1, 10, 1)
#chart = st.line_chart(df[selected_column1].rolling(rolling).mean())

# User select the last k games
k = st.slider("Select the last k games", 1, len(df), 5)
df_k = df.iloc[-k:, :]

# User choose two columns to display in graph
columns = df_k.columns
selected_column_y = st.selectbox("Select Y-axis parameter", columns, index=columns.get_loc('PTS'))


fig2 = px.line(df_k, x='DATE', y=selected_column_y, markers=True,)
# Set the line color and width
fig2.update_traces(line_color='#d9295a', line_width=3)
# Set the marker color
fig2.update_traces(marker_color='#3f2646')
# Set the x-axis tick mode, starting position, and step size
fig2.update_layout(xaxis=dict(tickfont=dict(size=16)))
# Set the y-axis tick mode and number of ticks
fig2.update_layout(yaxis=dict(tickfont=dict(size=16)))
st.plotly_chart(fig2)

# Add the Stats:
st.subheader(f'Last {k} Games Stats')
idx = [1, 2, 3, -1]
df_table = df_k.describe().iloc[idx]
# select the column you want to move
selected_column = df_table[selected_column_y]

# drop the selected column from the original data frame
df_table = df_table.drop(selected_column_y, axis=1)

# get a list of the column names in the desired order
cols = df_table.columns.tolist()
cols = [selected_column_y] + cols

# concatenate the selected column and the original data frame to create a new data frame
df_table = pd.concat([selected_column, df_table], axis=1)

# assign the column names in the desired order
df_table = df_table[cols]
st.dataframe(df_table)





# Credits
st.markdown("**Developed by**: Yehuda Yungstein")

# Set symbols and links 
st.markdown(
    """
    <style>
        div[data-testid="column"]:nth-of-type(1)
        {
            text-align: right;
        } 

        div[data-testid="column"]:nth-of-type(2)
        {
            text-align: left;
        } 
    </style>
    """,unsafe_allow_html=True
)

col1, col2, = st.columns(2,gap = "small")

with col1:
      # URL of the image
      image_url = "https://img.icons8.com/small/256/new-post.png"
      # Mail URL
      mail_url = "mailto:yehudayu@gmail.com"
      st.write("<a href='" + mail_url + "'><img src='" + image_url + "' width='50' height='50'></a>", unsafe_allow_html=True)


with col2:
      # URL of the image
      image_url = "https://img.icons8.com/small/256/linkedin.png"
      # LinkedIn URL
      linkedin_url = "https://www.linkedin.com/in/yehuda-yungstein/"
      st.write("<a href='" + linkedin_url + "'><img src='" + image_url + "' width='50' height='50'></a>", unsafe_allow_html=True)

