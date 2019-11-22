# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 16:08:29 2019

@author: Jonas
"""

def MovAveTeam(df, stat, lngth):
    # Import the required python libraries
    import numpy as np
    import pandas as pd
    
    # Configure variables and results data frame
    stat_h, stat_a = stat + "_home", stat + "_away"
    rslt = pd.DataFrame(np.nan,
                        index=range(len(df)), 
                        columns=['home','away'])
    rslt['UID'] = df['UID']
    
    # Calculate the rolling for every team
    for i in sorted(df['home_team'].unique()):
    #for i in [1]:
        # Get conditions for the team being either home or away and retrieve
        # the related index
        team_cond = (df['home_team'] == i) | (df['away_team'] == i)
        index = df.index[team_cond].tolist()
        # Generate a temporary data frame to do the calculations in
        tmp = df[['UID',
                  'date_time',
                  'home_team',
                  'away_team',
                  stat_h,
                  stat_a]].loc[index].copy()
        # Sort by date
        tmp = tmp.sort_values(['date_time'], ascending=1)
        # Get conditions for teams being either home or away
        home_cond, away_cond = (tmp['home_team'] == i), (tmp['away_team'] == i)
        index_home = tmp.index[home_cond].tolist()
        index_away = tmp.index[away_cond].tolist()
        # Collect the desired stat in one column and calculate the rolling ave
        tmp[stat] = tmp[stat_h]*home_cond + tmp[stat_a]*away_cond
        tmp['MovA'] = tmp[stat].rolling(window=lngth).mean()
        # Shift the rolling average with one back to prevent data leakage
        tmp['MovA'] = tmp['MovA'].shift(periods=1)
        # Sort moving average in respective home or away columns
        tmp['home'], tmp['away'] = np.nan, np.nan
        tmp['home'].loc[index_home] = tmp['MovA'].loc[index_home]
        tmp['away'].loc[index_away] = tmp['MovA'].loc[index_away]
        
        # Sort both rslt and tmp to make sure the UIDs align
        tmp = tmp.sort_values(['UID'], ascending=1)
        rslt = rslt.sort_values(['UID'], ascending=1)
        
        # Fill the results data frame with the team specific moving average
        rslt = rslt.combine_first(tmp[['UID','home','away']])
        
    return rslt['home'], rslt['away']

def EloTeam(df, start_elo, K, lower_bound = 100):
    import numpy as np
    
    df = df.sort_values(['date_time'], ascending=1)
    df['elo_home'], df['elo_away'] = np.nan, np.nan
    df['home_win'] = (df['R_home'] >= df['R_away'])
    
    year = np.nan
    for j, row in df.iterrows():
        if row['date_time'].year != year:
            d = {i:start_elo for i in sorted(df['home_team'].unique())}
            year = row['date_time'].year
        
        home, away = row['home_team'], row['away_team']
        df.at[j,'elo_home'], df.at[j,'elo_away'] = d[home], d[away]
        prob = 1 / (1 + np.power(10, (d[home] - d[away]) / 400))
        
        chng = int(row['home_win'])-prob
        d[home] = max(d[home] + K * chng, lower_bound)
        d[away] = max(d[away] - K * chng, lower_bound)
        
    return df





# =============================================================================
# def EloTeam(df, start_elo, K):
#     import numpy as np
#     import math
#     import pandas as pd
#     
#     tmp = df.copy(deep = True).sort_values(['date_time'], ascending=1)
#     tmp['home_win'] = (tmp['R_home']>=tmp['R_away'])
#     tmp['home'], tmp['away'] = np.nan, np.nan
#     
#     USE A DICTIONARY TO SAVE ELO PER TEAM!!!
#     
#     d = {i:start_elo for i in sorted(df['home_team'].unique())}
#     
#     for i in sorted(tmp['home_team'].unique()):
#         for j, foo in tmp.iterrows():
#             if tmp.at[j,'home_team'] == i:
#                 tmp.at[j,'home'] = start_elo
#             elif tmp.at[j,'away_team'] == i:
#                 tmp.at[j,'away'] = start_elo
#             else:
#                 continue
#             break
#     
#     for j, row in tmp.iterrows():
#         row['new_home'], row['new_away'] = np.nan, np.nan
#         row['elo_prob_home'], row['elo_prob_away'] = np.nan, np.nan
#         
#         prob = 1 / (1 + math.pow(10, (row['home'] - row['away']) / 400))
#         
#         if (row['home_win'] == 1):
#             row['new_home'] = row['home'] + K * (1-prob)
#             row['new_away'] = row['away'] + K * (prob-1)
#         else:
#             row['new_home'] = row['home'] + K * (-prob)
#             row['new_away'] = row['away'] + K * (prob)
#             
#         i = 0
#         for z in range(j+1,len(tmp)):
#             if tmp.at[z,'home_team'] == row['home_team']:
#                 tmp.at[z,'home'] = row['new_home']
#                 i += 1
#             if tmp.at[z,'away_team'] == row['away_team']:
#                 tmp.at[z,'away'] = row['new_away']
#                 i += 1
#             if i == 2:
#                 break
#         
#         return tmp['home'], tmp['away']
# =============================================================================
