from operator import index
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import datetime
import numpy as np

#simple functiion that fits the pca object with the dataframe and returns the pca object
def get_pca(df):
    pca = PCA()
    pca.fit(df)

    return pca

#function to plot the variance ratios
def plot_variance(p,title,index=-1):
    plt.plot(range(0,len(p)), p)
    plt.ylabel('Explained Variance')
    plt.xlabel('Principal Components')
    plt.title(title)

    #add marker for first pca above 95%

    if(index >= 0):
        plt.scatter(i,p[i],c="red")

    plt.show()

#function that finds the index of the first pca with cumulative variance greater than 95

def find_index(cumulative_variance):
    for i in range(len(cumulative_variance)):
        if(cumulative_variance[i] > 0.95):
            return i

#read csv file
data = pd.read_csv("stock_data.csv")

stocks = data[['date','close','Name']]

names = stocks
names = names.drop_duplicates(subset=['Name'],keep='first').sort_values('Name')

# print(names['Name'][0:5])
# print(names['Name'][-5:])

sorted_by_date = stocks.sort_values('date',ascending=True)

first_dates = sorted_by_date.drop_duplicates(subset=['Name'],keep='first').sort_values('Name')
last_dates = sorted_by_date.drop_duplicates(subset=['Name'],keep='last').sort_values('Name')

too_late = first_dates.query("date > '2014-01-01'")
too_early = last_dates.query("date < '2017-12-31'")

names_to_remove = too_late.append(too_early)
names_to_remove = names_to_remove['Name'].to_numpy()

#Remove all stocks that started trading after 2014-01-01 or stopped trading before 2017-12-31
clean_stocks = stocks[~stocks.Name.isin(names_to_remove)]
clean_names = clean_stocks.drop_duplicates(subset=['Name'])

#Remove all dates before 2014-01-01 and after 2017-12-31
clean_stocks = clean_stocks.query("date > '2014-01-01' & date < '2017-12-31'")

#create new dataframe with columns for stock names and indexed by dates
names = clean_names['Name'].to_numpy()

#find close dates for all stocks on a specific date
close = clean_stocks.query("date == '2014-01-02'")

#find dates that are common to all stocks
#group the dataframe by date and then loop through the groups and check they contain all of the stocks.
#since all stocks have to be in the group we can check if the size of the group is equal to the number of stocks

grouped_by_date = clean_stocks.groupby('date')

dates = []

for name, group in grouped_by_date:
    if(group.shape[0] == clean_names.shape[0]):
        #if the date is shared by all stocks then append it to an array that will serve as the index to the new df
        dates.append(name)


#remove the dates that arent shared by all stocks
clean_stocks = clean_stocks[clean_stocks.date.isin(dates)]

#for each date get the close values

all_close_data = []

for date in dates:
    close_values = clean_stocks[clean_stocks['date'] == date].sort_values('Name')
    close_values = close_values['close'].to_numpy()
    all_close_data.append(close_values)

#create new pandas dataframe from the data
df = pd.DataFrame(columns=names,index=dates,data=all_close_data)

df = df.sort_index()

#calculate all returns

all_returns_data = []

for i in range(df.shape[0]):

    #if it is the first row then skip

    if(i == 0):
        continue

    #calculate returns row by row

    date = df.iloc[i].to_numpy()
    previous_date = df.iloc[i-1].to_numpy()

    returns = np.divide((date - previous_date),previous_date)

    all_returns_data.append(returns)

#create new dataframe for the returns

returns_df = pd.DataFrame(columns=names,index=dates[1:],data=all_returns_data)

#calculate principal components
returns_pca = get_pca(returns_df)

#print principal components
# print("Principal components of the returns df: ")
# print(returns_pca.components_)

returns_var = returns_pca.explained_variance_ratio_
returns_cumulative = np.cumsum(returns_var)

i = find_index(returns_cumulative)

plot_variance(returns_var[0:20],"Explained variance ratios")
plot_variance(returns_cumulative,"Cumulative explained variance ratios",index=i)

#apply mean normalization to each column
normalized_returns = (returns_df-returns_df.mean())/returns_df.std()

#repeat steps 7-9

#calculate principal components
normalized_returns_pca = get_pca(normalized_returns)

#print principal components
# print("Principal components of the returns df: ")
# print(returns_pca.components_)

normalized_var = normalized_returns_pca.explained_variance_ratio_
norm_cumulative = np.cumsum(normalized_var)

i = find_index(norm_cumulative)

plot_variance(normalized_var[0:20],"Normalized Explained variance ratios")
plot_variance(norm_cumulative," Normalized Cumulative explained variance ratios",index=i)