import pandas as pd

df = pd.read_excel('BlueSky Sensors Inventory List.xlsx', skiprows = 2)
df.drop(df.columns[[0, 1]], axis = 1, inplace = True)
df.to_csv('haha.csv', index = False)