import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('BirgunjUrban_2021.csv')

test = df[['Timestamp (UTC)', 'PM2.5 (ug/m3)']].head(47423)
#42473
test['Timestamp (UTC)'] = pd.to_datetime(test['Timestamp (UTC)'], format='%m/%d/%Y %H:%M')

test.set_index(['Timestamp (UTC)'], inplace = True)

test.to_csv('test.csv')

L60 = test.rolling(60, center = True).mean()

#test30 = test.rolling(30).mean()

#test15 = test.rolling(15).mean()

concat60 = pd.concat([test, L60], axis = 1)
concat60.columns.values[0] = 'RAW'
concat60.columns.values[1] = '60'

#concat60.dropna(inplace = True)
concat60['Min60'] = concat60[['RAW', '60']].min(axis = 1)



L30 = concat60['Min60'].rolling(30, center = True).mean()

concat30 = pd.concat([concat60['Min60'], L30], axis = 1)
concat30.columns.values[0] = '60'
concat30.columns.values[1] = '30'

#concat30.dropna(inplace = True)
concat30['Min30'] = concat30[['60', '30']].min(axis = 1)



L15 = concat30['Min30'].rolling(15, center = True).mean()

concat15 = pd.concat([concat30['Min30'], L15], axis = 1)
concat15.columns.values[0] = '30'
concat15.columns.values[1] = '15'

#concat15.dropna(inplace = True)
concat15['Min15'] = concat15[['30', '15']].min(axis = 1)

concat15 = pd.concat([concat15, concat60['RAW']], axis = 1)
#concat15.dropna(inplace = True)




#concat.columns.values[0] = 'RAW'
#concat.columns.values[1] = '15'
#concat.columns.values[2] = '30'
#concat.columns.values[3] = '60'



#concat = concat.round(3)

#concat['Min'] = concat[['RAW', '15', '30', '60']].min(axis = 1)

concat15.reset_index(inplace = True)

#concat15.plot(x = 'Timestamp (UTC)', y=["RAW", 'Min15'], kind="line", figsize=(9, 8))

#plt.title('RAW Data vs Trimmed Data (Min)')
#plt.ylabel('PM2.5 (ug/m3)')

#plt.show()
print(L60)

new_df = pd.DataFrame(columns = ['Filler'])

concat60.reset_index(inplace = True)
concat30.reset_index(inplace = True)
concat15.reset_index(inplace = True)

new_df = pd.concat([new_df, df['Timestamp (UTC)']], axis=1)
new_df = pd.concat([new_df, concat60['RAW'].rename('RAW')], axis=1)
new_df = pd.concat([new_df, concat60['60']], axis=1)
new_df = pd.concat([new_df, concat30['30']], axis=1)
new_df = pd.concat([new_df, concat15['15']], axis=1)
new_df = pd.concat([new_df, concat60['Min60']], axis=1)
new_df = pd.concat([new_df, concat30['Min30']], axis=1)
new_df = pd.concat([new_df, concat15['Min15']], axis=1)


new_df.to_csv('concat.csv')
