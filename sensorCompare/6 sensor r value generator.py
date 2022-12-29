#!/usr/bin/env python
# coding: utf-8

# # Generate $r$ and $r^{2}$ Values for Your Sensors

# ### Read in Data and Group by Preferred Interval

# Each cell following the import pandas cell is reading in and grouping one csv file.
# 
# You will need to update the path and filename in the first line of each cell. My first csv file is called Duke1example.csv and is located in the folder "Bergin" which is located in my Desktop folder. 
# 
# If you are having trouble figuring out the path to your file:
# 
# Mac: Open Finder, click "Go" on the bar on top of your screen, and click "Go to Folder". If you drag a file into the dialogue box, the path for that file will be displayed.
# 
# Windows: Open folder holding your file, hold down shift key, and right click file. You can either select "copy as path" or you can view the path by selcting "properties".

# In[29]:


import pandas as pd


# In[30]:


#df1 = pd.read_csv("/Users/carmenallison/Desktop/Bergin/Duke1example.csv", skiprows=[1])
df1 = pd.read_csv("C:\Users\pvb5\Documents\StateDepartment\09_RawData\Dhaka University 1 (inside) (23.72823112 90.39856483) Date Range 07_11_2021 08_11_2021.csv", skiprows=[1])

pd.set_option("display.max.columns", None)
df1['Timestamp'] = pd.to_datetime(df1['Timestamp'], format = '%m/%d/%Y %H:%M')
df1['PM2.5'] = pd.to_numeric(df1['PM2.5'],errors='coerce')
g1 = df1.groupby([df1.Timestamp.dt.strftime('%b %d %-I %p')])['PM2.5'].mean().reset_index(name='Hourly Average 1')


# In[31]:


#df2 = pd.read_csv("/Users/carmenallison/Desktop/Bergin/Duke2example.csv", skiprows = [1])
df2 = pd.read_csv("C:\Users\pvb5\Documents\StateDepartment\09_RawData\Dhaka University 2 (inside) (23.72820547 90.39852372) Date Range 07_11_2021 08_11_2021.csv", skiprows=[1])
pd.set_option("display.max.columns", None)
df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], format = '%m/%d/%Y %H:%M', errors = 'coerce',)
df2['PM2.5'] = pd.to_numeric(df2['PM2.5'],errors='coerce')
g2 = df2.groupby([df2.Timestamp.dt.strftime('%b %d %-I %p')])['PM2.5'].mean().reset_index(name='Hourly Average 2')


# In[32]:


#df3 = pd.read_csv("/Users/carmenallison/Desktop/Bergin/Duke3example.csv", skiprows = [1])
df3 = pd.read_csv("C:\Users\pvb5\Documents\StateDepartment\09_RawData\Dhaka University 3 (inside) (23.7282198 90.39855491) Date Range 07_11_2021 08_11_2021.csv", skiprows = [1])
pd.set_option("display.max.columns", None)
df3['Timestamp'] = pd.to_datetime(df3['Timestamp'], format = '%m/%d/%Y %H:%M', errors = 'coerce',)
df3['PM2.5'] = pd.to_numeric(df3['PM2.5'],errors='coerce')
g3 = df3.groupby([df3.Timestamp.dt.strftime('%b %d %-I %p')])['PM2.5'].mean().reset_index(name='Hourly Average 3')


# In[33]:


#df4 = pd.read_csv("/Users/carmenallison/Desktop/Bergin/Duke4example.csv", skiprows = [1])
df4 = pd.read_csv("C:\Users\pvb5\Documents\StateDepartment\09_RawData\Dhaka University 4 (inside) (23.72816881 90.39851761) Date Range 07_11_2021 08_11_2021.csv", skiprows = [1])
pd.set_option("display.max.columns", None)
df4['Timestamp'] = pd.to_datetime(df4['Timestamp'], format = '%m/%d/%Y %H:%M', errors = 'coerce',)
df4['PM2.5'] = pd.to_numeric(df4['PM2.5'],errors='coerce')
g4 = df4.groupby([df4.Timestamp.dt.strftime('%b %d %-I %p')])['PM2.5'].mean().reset_index(name='Hourly Average 4')


# In[34]:


#df5 = pd.read_csv("/Users/carmenallison/Desktop/Bergin/Duke5example.csv", skiprows = [1])
df5 = pd.read_csv("C:\Users\pvb5\Documents\StateDepartment\09_RawData\Dhaka University 5 (inside) (23.72819827 90.39849481) Date Range 07_11_2021 08_11_2021.csv", skiprows = [1])
pd.set_option("display.max.columns", None)
df5['Timestamp'] = pd.to_datetime(df5['Timestamp'], format = '%m/%d/%Y %H:%M', errors = 'coerce',)
df5['PM2.5'] = pd.to_numeric(df5['PM2.5'],errors='coerce')
g5 = df5.groupby([df5.Timestamp.dt.strftime('%b %d %-I %p')])['PM2.5'].mean().reset_index(name='Hourly Average 5')


# In[35]:


#df6 = pd.read_csv("/Users/carmenallison/Desktop/Bergin/Duke6example.csv", skiprows = [1])
df6 = pd.read_csv("C:\Users\pvb5\Documents\StateDepartment\09_RawData\Dhaka University 6 (inside) (23.72821424 90.39859138) Date Range 07_11_2021 08_11_2021.csv", skiprows = [1])
pd.set_option("display.max.columns", None)
df6['Timestamp'] = pd.to_datetime(df6['Timestamp'], format = '%m/%d/%Y %H:%M', errors = 'coerce',)
df6['PM2.5'] = pd.to_numeric(df6['PM2.5'],errors='coerce')
g6 = df6.groupby([df6.Timestamp.dt.strftime('%b %d %-I %p')])['PM2.5'].mean().reset_index(name='Hourly Average 6')


# ### Change Index and Horizontally Concatenate Dataframes

# In[36]:


g1.set_index('Timestamp', inplace=True)
g2.set_index('Timestamp', inplace=True)
g3.set_index('Timestamp', inplace=True)
g4.set_index('Timestamp', inplace=True)
g5.set_index('Timestamp', inplace=True)
g6.set_index('Timestamp', inplace=True)


# In[37]:


concatdf  = pd.concat([g1, g2, g3, g4, g5, g6], ignore_index=False, axis = 1)


# ### Compute $r$ and $r^{2}$ Values

# In[38]:


import numpy as np
import matplotlib as mpl
import scipy.stats as sp

y=np.array(concatdf['Hourly Average 1'].dropna().values, dtype=float)
x=np.array(concatdf['Hourly Average 2'].dropna().values, dtype=float)
slope, intercept, r_value, p_value, std_err =sp.linregress(x,y)
rS1S2 = r_value
r2S1S2 = r_value ** 2

y=np.array(concatdf['Hourly Average 1'].dropna().values, dtype=float)
x=np.array(concatdf['Hourly Average 3'].dropna().values, dtype=float)
slope, intercept, r_value, p_value, std_err =sp.linregress(x,y)
rS1S3 = r_value
r2S1S3 = r_value ** 2

y=np.array(concatdf['Hourly Average 1'].dropna().values, dtype=float)
x=np.array(concatdf['Hourly Average 4'].dropna().values, dtype=float)
slope, intercept, r_value, p_value, std_err =sp.linregress(x,y)
rS1S4 = r_value
r2S1S4 = r_value ** 2

y=np.array(concatdf['Hourly Average 1'].dropna().values, dtype=float)
x=np.array(concatdf['Hourly Average 5'].dropna().values, dtype=float)
slope, intercept, r_value, p_value, std_err =sp.linregress(x,y)
rS1S5 = r_value
r2S1S5 = r_value ** 2

y=np.array(concatdf['Hourly Average 1'].dropna().values, dtype=float)
x=np.array(concatdf['Hourly Average 6'].dropna().values, dtype=float)
slope, intercept, r_value, p_value, std_err =sp.linregress(x,y)
rS1S6 = r_value
r2S1S6 = r_value ** 2

y=np.array(concatdf['Hourly Average 2'].dropna().values, dtype=float)
x=np.array(concatdf['Hourly Average 3'].dropna().values, dtype=float)
slope, intercept, r_value, p_value, std_err =sp.linregress(x,y)
rS2S3 = r_value
r2S2S3 = r_value ** 2

y=np.array(concatdf['Hourly Average 2'].dropna().values, dtype=float)
x=np.array(concatdf['Hourly Average 4'].dropna().values, dtype=float)
slope, intercept, r_value, p_value, std_err =sp.linregress(x,y)
rS2S4 = r_value
r2S2S4 = r_value ** 2

y=np.array(concatdf['Hourly Average 2'].dropna().values, dtype=float)
x=np.array(concatdf['Hourly Average 5'].dropna().values, dtype=float)
slope, intercept, r_value, p_value, std_err =sp.linregress(x,y)
rS2S5 = r_value
r2S2S5 = r_value ** 2

y=np.array(concatdf['Hourly Average 2'].dropna().values, dtype=float)
x=np.array(concatdf['Hourly Average 6'].dropna().values, dtype=float)
slope, intercept, r_value, p_value, std_err =sp.linregress(x,y)
rS2S6 = r_value
r2S2S6 = r_value ** 2

y=np.array(concatdf['Hourly Average 3'].dropna().values, dtype=float)
x=np.array(concatdf['Hourly Average 4'].dropna().values, dtype=float)
slope, intercept, r_value, p_value, std_err =sp.linregress(x,y)
rS3S4 = r_value
r2S3S4 = r_value ** 2

y=np.array(concatdf['Hourly Average 3'].dropna().values, dtype=float)
x=np.array(concatdf['Hourly Average 5'].dropna().values, dtype=float)
slope, intercept, r_value, p_value, std_err =sp.linregress(x,y)
rS3S5 = r_value
r2S3S5 = r_value ** 2

y=np.array(concatdf['Hourly Average 3'].dropna().values, dtype=float)
x=np.array(concatdf['Hourly Average 6'].dropna().values, dtype=float)
slope, intercept, r_value, p_value, std_err =sp.linregress(x,y)
rS3S6 = r_value
r2S3S6 = r_value ** 2

y=np.array(concatdf['Hourly Average 4'].dropna().values, dtype=float)
x=np.array(concatdf['Hourly Average 5'].dropna().values, dtype=float)
slope, intercept, r_value, p_value, std_err =sp.linregress(x,y)
rS4S5 = r_value
r2S4S5 = r_value ** 2

y=np.array(concatdf['Hourly Average 4'].dropna().values, dtype=float)
x=np.array(concatdf['Hourly Average 6'].dropna().values, dtype=float)
slope, intercept, r_value, p_value, std_err =sp.linregress(x,y)
rS4S6 = r_value
r2S4S6 = r_value ** 2

y=np.array(concatdf['Hourly Average 5'].dropna().values, dtype=float)
x=np.array(concatdf['Hourly Average 6'].dropna().values, dtype=float)
slope, intercept, r_value, p_value, std_err =sp.linregress(x,y)
rS5S6 = r_value
r2S5S6 = r_value ** 2


# ### Display $r$ and $r^{2}$ Values

# In[39]:


print('Sensor 1 vs Sensor 2:', '\n', 'r =', rS1S2, '\n', 'r2 =', r2S1S2, '\n')
print('Sensor 1 vs Sensor 3:', '\n', 'r =', rS1S3, '\n', 'r2 =', r2S1S3, '\n')
print('Sensor 1 vs Sensor 4:', '\n', 'r =', rS1S4, '\n', 'r2 =', r2S1S4, '\n')
print('Sensor 1 vs Sensor 5:', '\n', 'r =', rS1S5, '\n', 'r2 =', r2S1S5, '\n')
print('Sensor 1 vs Sensor 6:', '\n', 'r =', rS1S6, '\n', 'r2 =', r2S1S6, '\n')
print('Sensor 2 vs Sensor 3:', '\n', 'r =', rS2S3, '\n', 'r2 =', r2S2S3, '\n')
print('Sensor 2 vs Sensor 4:', '\n', 'r =', rS2S4, '\n', 'r2 =', r2S2S4, '\n')
print('Sensor 2 vs Sensor 5:', '\n', 'r =', rS2S5, '\n', 'r2 =', r2S2S5, '\n')
print('Sensor 2 vs Sensor 6:', '\n', 'r =', rS2S6, '\n', 'r2 =', r2S2S6, '\n')
print('Sensor 3 vs Sensor 4:', '\n', 'r =', rS3S4, '\n', 'r2 =', r2S3S4, '\n')
print('Sensor 3 vs Sensor 5:', '\n', 'r =', rS3S5, '\n', 'r2 =', r2S3S5, '\n')
print('Sensor 3 vs Sensor 6:', '\n', 'r =', rS3S6, '\n', 'r2 =', r2S3S6, '\n')
print('Sensor 4 vs Sensor 5:', '\n', 'r =', rS4S5, '\n', 'r2 =', r2S4S5, '\n')
print('Sensor 4 vs Sensor 6:', '\n', 'r =', rS4S6, '\n', 'r2 =', r2S4S6, '\n')
print('Sensor 5 vs Sensor 6:', '\n', 'r =', rS5S6, '\n', 'r2 =', r2S5S6, '\n')


# ### Produce and Display $r^{2}$ Matrix

# In[40]:


data = [['', r2S1S2, r2S1S3, r2S1S4, r2S1S5, r2S1S6], [r2S1S2, '', r2S2S3, r2S2S4, r2S2S5, r2S2S6], 
        [r2S1S3, r2S2S3, '', r2S3S4, r2S3S5, r2S3S6], [r2S1S4, r2S2S4, r2S3S4, '', r2S4S5, r2S4S6],
        [r2S1S5, r2S2S5, r2S3S5, r2S4S5, '', r2S5S6], [r2S1S6, r2S2S6, r2S3S6, r2S4S6, r2S5S6, '']]

matrixdf = pd.DataFrame(data, index=['Sensor 1', 'Sensor 2', 'Sensor 3', 'Sensor 4', 'Sensor 5', 'Sensor 6'],
                  columns=['Sensor 1', 'Sensor 2', 'Sensor 3', 'Sensor 4', 'Sensor 5', 'Sensor 6'])

print(matrixdf)


# ### Constructing Your Own Matrix

# For ease in constructing your own matrix to compare sensors, here is a list of $r^{2}$ values in the same order as listed in the "Display $r$ and $r^{2}$ Values" segment:

# In[41]:


print(r2S1S2, '\n', r2S1S3, '\n',r2S1S4, '\n', r2S1S5, '\n', r2S1S6, '\n', r2S2S3, '\n', r2S2S4, '\n',
      r2S2S5, '\n', r2S2S6, '\n', r2S3S4, '\n', r2S3S5, '\n', r2S3S6, '\n', r2S4S5, '\n', r2S4S6, '\n',
      r2S5S6, '\n',)


# ### Visualize Specific Sensor Correlations

# If you are interested in producing a correlation plot for specific sensors, you will need to update the following manually:
# 
# Line 2 and 3: Specify which Hourly Averages you are interested in comparing. (ie if you are comparing sensors 2 and 5 you would change the contents of the brackets in line 3 to 'Hourly Average 2' and the contents of the brackets in line 4 to 'Hourly Average 5')
# 
# Line 7: Update title to reflect sensors being compared.
# 
# Line 8 and 9: Update plot labels to reflect sensors being compared.
# 
# Line 10 and 11: If necessary, update x and y limits of plot to fit data points.
# 
# Line 12: Update the the variable inside format() to reflect the $r^{2}$ value you would like to display on the plot. For example, if you are comparing sensor 2 and sensor 5 in your plot you would replace the current variable in the format parentheses with r2S2S5. It is important to note that all of the $r^{2}$ value variable names follow the same pattern where the lower sensor number precedes the higher sensor number.
# 
# Line 14: Comment out this line by placing a # in front of the line if you don't want the line of best fit

# In[42]:


import matplotlib.pyplot as plt
x=concatdf['Hourly Average 1']
y=concatdf['Hourly Average 2']

fig, ax = plt.subplots()
ax.scatter(x, y)
plt.title('Sensor 1 vs Sensor 2')
plt.xlabel('Sensor 1 PM2.5 Concentration')
plt.ylabel('Sensor 2 PM2.5 Concentration')
ax.set_ylim([0, 8])
ax.set_xlim([0, 7])
plt.text(0.78, 0.9, "r2 = {}\n".format(r2S1S2), horizontalalignment='center', 
         verticalalignment='center', style = 'italic', transform=ax.transAxes)
plt.plot(np.unique(x), np.poly1d(np.polyfit(x, y, 1))(np.unique(x)))


# In[ ]:




