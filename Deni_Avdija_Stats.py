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
path_22 = "Deni_2022-23_1-52.csv"

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

# User choose X-axis parameter
columns2 = df.columns
selected_column2 = st.selectbox("Select x-axis parameter (optional)", columns2, key="4", index=columns2.get_loc('DATE'))

# User choose column to present in graph
columns1 = df.columns
selected_column1 = st.selectbox("Select Y-axis parameter", columns1, key="5", index=columns2.get_loc('PTS'))

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
#rolling = st.slider("Rolling avg value", 1, 10, 1)
#chart = st.line_chart(df[selected_column1].rolling(rolling).mean())

# User select the last k games
k = st.slider("Select the last k games", 1, len(df), 5)
df_k = df.iloc[-k:, :]

# User choose two columns to display in graph
columns = df_k.columns
selected_column_y = st.selectbox("Select Y-axis parameter", columns, index=columns.get_loc('PTS'))


col1, col2 = st.columns([3, 1])

fig, ax = plt.subplots()
ax.plot(df_k['DATE'], df_k[selected_column_y],color = '#E41134')
ax.scatter(df_k['DATE'], df_k[selected_column_y],color = "#C6CFD5")
ax.set_xlabel('Date')
ax.set_title(f'{selected_column_y} (last {k} games)')
ax.set_ylabel(selected_column_y)
plt.xticks(rotation=90)

# Add background of horizontal grid
ax.grid(axis='y', linestyle='--', alpha=0.5)
col1.pyplot(fig)

# Add the average:

# st.dataframe(df_k.describe().iloc[1])
# st.table(df_k.describe().iloc[1].T)
# col2.subheader("A narrow column with the data")
col2.subheader("Means")
col2.table(df_k.describe().iloc[1])


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

