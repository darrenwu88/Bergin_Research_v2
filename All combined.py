# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 12:41:17 2022

@author: trb50
"""

import requests
import json
from datetime import datetime, timedelta,date
import os
import pandas as pd
import numpy as np
import glob
import time
import shutil
from selenium import webdriver
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
# Enter the serial number for which you want to extract the sensor value
OurSerial = '81432123027'



def get_data():

    # login credential and tokens
    cred_data = {"id":"BWlNJyLZ9uj9AMVmDxHC","audience":"https://tsilink.com/api/v2/rbac","accountId":"c3smtl0qi9clu8nikadg","email":"rmaskey@cdes.edu.np","secret":"&L*J427V0N*K3d2B4*7QgDUX0tcVmFVl","createdAt":"2022-03-09T13:29:10.559198855Z"}

    url = "https://tsilink.com/oauth/token"
    payload = json.dumps({
            "grant_type": "client_credentials",
            "client_id": cred_data['id'],
            "audience": cred_data['audience'],
            "client_secret": cred_data['secret'],
        })

    headers = {'Content-Type': 'application/json'}

    response = requests.request("POST", url, headers=headers, data=payload)
    response_json = response.json()
    tok_code = response_json['access_token']



    url = "https://tsilink.com/api/v2/external/devices"
    payload = {}
    headers = {}
    tok_code = "Bearer " + tok_code
    headers['Authorization'] = tok_code
    response = requests.request("GET", url, headers=headers, data=payload)
    response_json = response.json()
    sensor_info = []
    for dic in (response_json):
        meta = dic['metadata']
        a = (dic['serial'])
        if (a == OurSerial):
            dic2 = {}
            dic2.update({
                'account_id': dic['account_id'],
                'device_id': dic['device_id'],
                'model': dic['model'],
                'serial': dic['serial'],
                'friendlyName': meta['friendlyName'],
                'is_indoor': meta['is_indoor'],
                'latitude': meta['latitude'],
                'longitude': meta['longitude'],
            })
            sensor_info.append(dic2)
            break
    if len(sensor_info) == 0:
        print("No such serial number for this country, skipping program: Re-Check the serial number and try agian!")
        return
        # print(sensor_info)

    url = "https://tsilink.com/api/v2/external/telemetry"
    params = {}
    payload = {}
    headers = {}
    fname_s = fname_e = ""
    data_start_date = data_age = data_end_date = ""
    headers['Authorization'] = tok_code
    # optional arguments
    headers.update({'Accept': 'text/csv'})  # comment out this line for json
    # data_age="&age=0.5" #days of data (can be used with start date)

    data_start_date = "&start_date="+str(date.today()-timedelta(days=7))+"T00:00:00.000Z"  # use UTC format.
    data_end_date = "&start_date="+str(date.today())+"T00:00:00.000Z" # use UTC format
    if (data_start_date != "" and data_end_date != ""):
        fname_s = data_start_date[12:22]  # only want the date part of the string
        fname_e = data_end_date[10:20]

    filename = sensor_info[0]['serial'] + "_" + fname_s + "_" + fname_e + ".csv"
    dev_id = "?device_id=" + sensor_info[0]['device_id']
    response = requests.request("GET", url + dev_id + data_age + data_start_date + \
                                data_end_date, headers=headers, data=payload)

    # -------------- Save telemetry data to .csv files --------------
    f = open(filename, "w")
    f.write(response.text)
    f.close()

    serial_number = sensor_info[0]['serial']
    lat_value = sensor_info[0]['latitude']
    long_value = sensor_info[0]['longitude']
    site_name = sensor_info[0]['friendlyName']
    is_indoors = sensor_info[0]['is_indoor']
    country = "Nepal"

    df = pd.read_csv(filename, header=[0, 1])

    # Serial / Site Name / Country / Timestamp / Long / Lat / is_indoors   format
    df.insert(0, "Serial Number", serial_number)
    df.insert(1, "Country", country)
    df.insert(2, 'Site Name', site_name)
    df.insert(4, "Longitude", long_value)
    df.insert(5, "Latitude", lat_value)
    df.insert(6, "is_indoors", is_indoors)

    # calculate time delta of sensor data retrieval (e.g. 15 min or 1 min usually)
    time = pd.to_datetime(df['Timestamp', 'UTC'], format='%m/%d/%Y %H:%M')

    # account for times where data isn't continuous
    if (len(time) != 0):
        sensor_timedelta = time.diff()
        sensor_timedelta[0] = 0 
        for i in range(1,len(sensor_timedelta)):            
            (sensor_timedelta[i])=int(str(sensor_timedelta[i])[-5:-3])
       
        df.insert(len(df.columns), 'Time Delta', sensor_timedelta)

    df = df.rename(columns=lambda x: x if not "Unnamed" in str(x) else "")
    df.to_csv("Raw_individual.csv", index=False)
    os.remove(filename)

def mergeeverything():
    get_data()

    df_raw = pd.read_csv('Raw_individual.csv')

    # collapse headers
    for col in df_raw.columns:
        # get first row value for this specific column
        first_row = df_raw.iloc[0][col]
        new_column_name = str(col) + ' (' + str(first_row) + ')'  # first_row

        # rename the column with the existing column header plus the first row of that column's data
        df_raw.rename(columns={col: new_column_name}, inplace=True)

    df_raw = df_raw.rename(columns=lambda x: x if not "(nan)" in str(x) else x[:(len(x) - 6)])
    df_raw.drop([0], inplace=True)

    # convert data cols from str to int
    df_raw[['PM1.0 (ug/m3)', 'PM2.5 (ug/m3)', 'PM4.0 (ug/m3)', 'PM10 (ug/m3)']] = df_raw[
        ['PM1.0 (ug/m3)', 'PM2.5 (ug/m3)', 'PM4.0 (ug/m3)', 'PM10 (ug/m3)']].apply(pd.to_numeric, downcast='signed',
                                                                                   errors='coerce')

    # revert type of serial number column
    df_raw["Serial Number"] = df_raw["Serial Number"].astype(np.int64)

    df_raw.to_csv('Level0.csv', index=False)

    ### Level 0 Hourly

    df_hourly = pd.read_csv('Level0.csv')
    time = pd.to_datetime(df_hourly['Timestamp (UTC)'], format='%m/%d/%Y %H:%M')

    grouping = df_hourly.groupby(['Serial Number', time.dt.year, time.dt.month, time.dt.day, time.dt.hour]).transform(
        lambda x: len(x))
    count = grouping['Time Delta']
    df_hourly.insert(len(df_hourly.columns), 'Entry Count', count)

    df_hourly = df_hourly[df_hourly['Entry Count'] * df_hourly['Time Delta'] >= 45]

    df_hourly_groups = df_hourly.groupby(
        ['Country', 'Serial Number', time.dt.year, time.dt.month, time.dt.day, time.dt.hour,
         'Site Name', 'Longitude', 'Latitude', 'is_indoors'], as_index=True)

    df_hourly = df_hourly_groups[['PM1.0 (ug/m3)', 'PM2.5 (ug/m3)', 'PM4.0 (ug/m3)', 'PM10 (ug/m3)',
                                  'PM0.5 NC (#/cm3)', 'PM1.0 NC (#/cm3)', 'PM2.5 NC (#/cm3)', 'PM4.0 NC (#/cm3)',
                                  'PM10 NC (#/cm3)', 'Typical Particle Size (um)', 'Temperature (Celsius)',
                                  'Relative Humidity (%)', 'Time Delta', 'Entry Count']].mean()

    # format columns so csv format stays the same
    df_hourly = df_hourly.reset_index(
        level=['Serial Number', 'Country', 'Site Name', 'Longitude', 'Latitude', 'is_indoors'])
    df_hourly.insert(3, 'Timestamp (UTC)', df_hourly.index.to_numpy())
    df_hourly.insert(9, 'Applied PM2.5 Custom Calibration Factor', "")
    df_hourly.insert(12, 'Applied PM10 Custom Calibration Factor', "")

    # convert tuple timestamp to datetime type
    df_hourly['Timestamp (UTC)'] = df_hourly['Timestamp (UTC)'].apply(lambda x: datetime(*x))
    df_hourly['Timestamp (UTC)'] = df_hourly['Timestamp (UTC)'].dt.strftime('%m/%d/%Y %H:%M')

    # precision value adjustment for data
    df_hourly[['PM1.0 (ug/m3)', 'PM2.5 (ug/m3)', 'PM4.0 (ug/m3)', 'PM10 (ug/m3)', 'Typical Particle Size (um)']] = \
        df_hourly[
            ['PM1.0 (ug/m3)', 'PM2.5 (ug/m3)', 'PM4.0 (ug/m3)', 'PM10 (ug/m3)', 'Typical Particle Size (um)']].round(
            2)

    df_hourly[['PM0.5 NC (#/cm3)', 'PM1.0 NC (#/cm3)', 'PM2.5 NC (#/cm3)', 'PM4.0 NC (#/cm3)', 'PM10 NC (#/cm3)',
               'Temperature (Celsius)', 'Relative Humidity (%)', 'Time Delta']] = df_hourly[
        ['PM0.5 NC (#/cm3)', 'PM1.0 NC (#/cm3)', 'PM2.5 NC (#/cm3)', 'PM4.0 NC (#/cm3)', 'PM10 NC (#/cm3)',
         'Temperature (Celsius)', 'Relative Humidity (%)', 'Time Delta']].round(1)

    df_hourly.to_csv('Level0_hourly.csv', index=False)

    ### LEVEL 1 QA

    # insert Case Error
    case_error = df_raw['Device Status'][1:].astype(int).map(lambda x: (f'{x:08b}')).astype(str).map(
        lambda x: x[0:5]).map(lambda x: x[-1:])
    df_raw.insert(len(df_raw.columns), 'Case Error', case_error)

    # insert PM Sensor Error
    PM_sensor_error = df_raw['Device Status'][1:].astype(int).map(lambda x: (f'{x:08b}')).astype(str).map(
        lambda x: x[0:4]).map(lambda x: x[-1:])
    df_raw.insert(len(df_raw.columns), 'PM Sensor Error', PM_sensor_error)

    # Remove T, RH if case_error = 1
    df_raw.loc[df_raw['Case Error'] == '1', ['Temperature (Celsius)', 'Relative Humidity (%)']] = None

    # Remove PM2.5, PM10 if pm_sensor_error = 1
    df_raw.loc[df_raw['PM Sensor Error'] == '1',
               ['PM1.0 (ug/m3)', 'PM2.5 (ug/m3)', 'PM4.0 (ug/m3)', 'PM10 (ug/m3)',
                'PM1.0 NC (#/cm3)', 'PM0.5 NC (#/cm3)', 'PM1.0 NC (#/cm3)', 'PM2.5 NC (#/cm3)',
                'PM4.0 NC (#/cm3)', 'PM10 NC (#/cm3)', 'Typical Particle Size (um)']] = None

    # delete error columns
    df_raw.drop(['Case Error', 'PM Sensor Error'], axis=1, inplace=True)

    # data capping function for ug/m3 measurements
    # also adding an is_capped column to show that the relevant data has been capped

    df_raw.insert(7, 'is_capped', 'No')

    # 1 min -> >5000
    # 5 min -> >2000
    # >10min -> >1000

    # PM1.0
    df_raw.loc[(df_raw['Time Delta'] >= 10) & (df_raw['PM1.0 (ug/m3)'] >= 1000), ['PM1.0 (ug/m3)']] = 1000
    df_raw.loc[(df_raw['Time Delta'] >= 10) & (df_raw['PM1.0 (ug/m3)'] >= 1000), ['is_capped']] = 'Yes'

    df_raw.loc[(df_raw['Time Delta'] >= 5) & (df_raw['PM1.0 (ug/m3)'] >= 2000), ['PM1.0 (ug/m3)']] = 2000
    df_raw.loc[(df_raw['Time Delta'] >= 5) & (df_raw['PM1.0 (ug/m3)'] >= 2000), ['is_capped']] = 'Yes'

    df_raw.loc[(df_raw['Time Delta'] >= 1) & (df_raw['PM1.0 (ug/m3)'] >= 5000), ['PM1.0 (ug/m3)']] = 5000
    df_raw.loc[(df_raw['Time Delta'] >= 1) & (df_raw['PM1.0 (ug/m3)'] >= 5000), ['is_capped']] = 'Yes'

    # PM2.5
    df_raw.loc[(df_raw['Time Delta'] >= 10) & (df_raw['PM2.5 (ug/m3)'] >= 1000), ['PM2.5 (ug/m3)']] = 1000
    df_raw.loc[(df_raw['Time Delta'] >= 10) & (df_raw['PM2.5 (ug/m3)'] >= 1000), ['is_capped']] = 'Yes'

    df_raw.loc[(df_raw['Time Delta'] >= 5) & (df_raw['PM2.5 (ug/m3)'] >= 2000), ['PM2.5 (ug/m3)']] = 2000
    df_raw.loc[(df_raw['Time Delta'] >= 5) & (df_raw['PM2.5 (ug/m3)'] >= 2000), ['is_capped']] = 'Yes'

    df_raw.loc[(df_raw['Time Delta'] >= 1) & (df_raw['PM2.5 (ug/m3)'] >= 5000), ['PM2.5 (ug/m3)']] = 5000
    df_raw.loc[(df_raw['Time Delta'] >= 1) & (df_raw['PM2.5 (ug/m3)'] >= 5000), ['is_capped']] = 'Yes'

    # PM4.0
    df_raw.loc[(df_raw['Time Delta'] >= 10) & (df_raw['PM4.0 (ug/m3)'] >= 1000), ['PM4.0 (ug/m3)']] = 1000
    df_raw.loc[(df_raw['Time Delta'] >= 10) & (df_raw['PM1.0 (ug/m3)'] >= 1000), ['is_capped']] = 'Yes'

    df_raw.loc[(df_raw['Time Delta'] >= 5) & (df_raw['PM4.0 (ug/m3)'] >= 2000), ['PM4.0 (ug/m3)']] = 2000
    df_raw.loc[(df_raw['Time Delta'] >= 5) & (df_raw['PM4.0 (ug/m3)'] >= 2000), ['is_capped']] = 'Yes'

    df_raw.loc[(df_raw['Time Delta'] >= 1) & (df_raw['PM4.0 (ug/m3)'] >= 5000), ['PM4.0 (ug/m3)']] = 5000
    df_raw.loc[(df_raw['Time Delta'] >= 1) & (df_raw['PM4.0 (ug/m3)'] >= 5000), ['is_capped']] = 'Yes'

    # PM10
    df_raw.loc[(df_raw['Time Delta'] >= 10) & (df_raw['PM10 (ug/m3)'] >= 1000), ['PM10 (ug/m3)']] = 1000
    df_raw.loc[(df_raw['Time Delta'] >= 10) & (df_raw['PM10 (ug/m3)'] >= 1000), ['is_capped']] = 'Yes'

    df_raw.loc[(df_raw['Time Delta'] >= 5) & (df_raw['PM10 (ug/m3)'] >= 2000), ['PM10 (ug/m3)']] = 2000
    df_raw.loc[(df_raw['Time Delta'] >= 5) & (df_raw['PM10 (ug/m3)'] >= 2000), ['is_capped']] = 'Yes'

    df_raw.loc[(df_raw['Time Delta'] >= 1) & (df_raw['PM10 (ug/m3)'] >= 5000), ['PM10 (ug/m3)']] = 5000
    df_raw.loc[(df_raw['Time Delta'] >= 1) & (df_raw['PM10 (ug/m3)'] >= 5000), ['is_capped']] = 'Yes'

    ### OUTPUT
    df_raw.to_csv('Level1.csv', index=False)

    # the bit that add's NPT column
    try:
        df_raw_modified = df_raw.copy()
        df_raw_modified['Timestamp (NPT)'] = pd.to_datetime(df_raw_modified['Timestamp (UTC)']) + timedelta(hours=5,
                                                                                                            minutes=45)
        # rearranging columns so two time columns end up side by side
        cols = list(df_raw_modified.columns.values)
        cols = cols[0:3] + [cols[-1]] + cols[3:-1]
        df_raw_modified = df_raw_modified[cols]

        # writing it to a new CSV file
        df_raw_modified.to_csv('Level1_with_NPT.csv', index=False)
    except:
        print("Had error while converting to local time.")

    ### Level 1 Hourly (same logic as Level 0 Hourly)

    df_hourly_1 = pd.read_csv('Level1.csv')
    time = pd.to_datetime(df_hourly_1['Timestamp (UTC)'], format='%m/%d/%Y %H:%M')

    # don't count rows where there is PM Sensor error
    df_hourly_1 = df_hourly_1[df_hourly_1['PM1.0 (ug/m3)'].notna()]

    grouping = df_hourly_1.groupby(['Serial Number', time.dt.year, time.dt.month, time.dt.day, time.dt.hour]).transform(
        lambda x: len(x))
    count = grouping['Time Delta']
    df_hourly_1.insert(len(df_hourly_1.columns), 'Entry Count', count)

    # 75% completeness criteria for each hour
    df_hourly_1 = df_hourly_1[df_hourly_1['Entry Count'] * df_hourly_1['Time Delta'] >= 45]

    df_hourly_1_groups = df_hourly_1.groupby(
        ['Country', 'Serial Number', time.dt.year, time.dt.month, time.dt.day, time.dt.hour,
         'Site Name', 'Longitude', 'Latitude', 'is_indoors'], as_index=True)

    df_hourly_1 = df_hourly_1_groups[['PM1.0 (ug/m3)', 'PM2.5 (ug/m3)', 'PM4.0 (ug/m3)', 'PM10 (ug/m3)',
                                      'PM0.5 NC (#/cm3)', 'PM1.0 NC (#/cm3)', 'PM2.5 NC (#/cm3)', 'PM4.0 NC (#/cm3)',
                                      'PM10 NC (#/cm3)', 'Typical Particle Size (um)', 'Temperature (Celsius)',
                                      'Relative Humidity (%)', 'Time Delta', 'Entry Count']].mean()

    df_hourly_1 = df_hourly_1.reset_index(
        level=['Serial Number', 'Country', 'Site Name', 'Longitude', 'Latitude', 'is_indoors'])
    df_hourly_1.insert(3, 'Timestamp (UTC)', df_hourly_1.index)
    df_hourly_1.insert(9, 'Applied PM2.5 Custom Calibration Factor', "")
    df_hourly_1.insert(12, 'Applied PM10 Custom Calibration Factor', "")

    # include Applied PM2.5 Custom Calibration Factor', 'Applied PM10 Custom Calibration Factor

    # convert tuple to datetime
    df_hourly_1['Timestamp (UTC)'] = df_hourly_1['Timestamp (UTC)'].apply(lambda x: datetime(*x))
    df_hourly_1['Timestamp (UTC)'] = df_hourly_1['Timestamp (UTC)'].dt.strftime('%m/%d/%Y %H:%M')

    # precision value adjustment for data
    df_hourly_1[['PM1.0 (ug/m3)', 'PM2.5 (ug/m3)', 'PM4.0 (ug/m3)', 'PM10 (ug/m3)', 'Typical Particle Size (um)']] = \
        df_hourly_1[
            ['PM1.0 (ug/m3)', 'PM2.5 (ug/m3)', 'PM4.0 (ug/m3)', 'PM10 (ug/m3)', 'Typical Particle Size (um)']].round(2)

    df_hourly_1[['PM0.5 NC (#/cm3)', 'PM1.0 NC (#/cm3)', 'PM2.5 NC (#/cm3)', 'PM4.0 NC (#/cm3)', 'PM10 NC (#/cm3)',
                 'Temperature (Celsius)', 'Relative Humidity (%)', 'Time Delta']] = df_hourly_1[
        ['PM0.5 NC (#/cm3)', 'PM1.0 NC (#/cm3)', 'PM2.5 NC (#/cm3)', 'PM4.0 NC (#/cm3)', 'PM10 NC (#/cm3)',
         'Temperature (Celsius)', 'Relative Humidity (%)', 'Time Delta']].round(1)

    df_hourly_1.to_csv('Level1_hourly.csv', index=False)

    # the bit that add's NPT column
    try:
        df_hourly_1_NPT = pd.read_csv('Level1.csv')
        df_hourly_1_NPT['Timestamp (UTC)'] = pd.to_datetime(df_hourly_1_NPT['Timestamp (UTC)']) + timedelta(hours=5,
                                                                                                            minutes=45)
        # print(1)
        time = pd.to_datetime(df_hourly_1_NPT['Timestamp (UTC)'], format='%m/%d/%Y %H:%M')
        # print(2)

        # don't count rows where there is PM Sensor error
        df_hourly_1_NPT = df_hourly_1_NPT[df_hourly_1_NPT['PM1.0 (ug/m3)'].notna()]
        # print(3)
        grouping = df_hourly_1_NPT.groupby(
            ['Serial Number', time.dt.year, time.dt.month, time.dt.day, time.dt.hour]).transform(
            lambda x: len(x))
        count = grouping['Time Delta']
        # print(4)
        df_hourly_1_NPT.insert(len(df_hourly_1_NPT.columns), 'Entry Count', count)

        # print("Error here")
        # 75% completeness criteria for each hour
        df_hourly_1_NPT = df_hourly_1_NPT[df_hourly_1_NPT['Entry Count'] * df_hourly_1_NPT['Time Delta'] >= 45]

        df_hourly_1_groups = df_hourly_1_NPT.groupby(
            ['Country', 'Serial Number', time.dt.year, time.dt.month, time.dt.day, time.dt.hour,
             'Site Name', 'Longitude', 'Latitude', 'is_indoors'], as_index=True)

        df_hourly_1_NPT = df_hourly_1_groups[['PM1.0 (ug/m3)', 'PM2.5 (ug/m3)', 'PM4.0 (ug/m3)', 'PM10 (ug/m3)',
                                              'PM0.5 NC (#/cm3)', 'PM1.0 NC (#/cm3)', 'PM2.5 NC (#/cm3)',
                                              'PM4.0 NC (#/cm3)',
                                              'PM10 NC (#/cm3)', 'Typical Particle Size (um)', 'Temperature (Celsius)',
                                              'Relative Humidity (%)', 'Time Delta', 'Entry Count']].mean()

        df_hourly_1_NPT = df_hourly_1_NPT.reset_index(
            level=['Serial Number', 'Country', 'Site Name', 'Longitude', 'Latitude', 'is_indoors'])
        df_hourly_1_NPT.insert(3, 'Timestamp (UTC)', df_hourly_1_NPT.index)
        df_hourly_1_NPT.insert(9, 'Applied PM2.5 Custom Calibration Factor', "")
        df_hourly_1_NPT.insert(12, 'Applied PM10 Custom Calibration Factor', "")

        # include Applied PM2.5 Custom Calibration Factor', 'Applied PM10 Custom Calibration Factor

        # convert tuple to datetime
        df_hourly_1_NPT['Timestamp (UTC)'] = df_hourly_1_NPT['Timestamp (UTC)'].apply(lambda x: datetime(*x))
        df_hourly_1_NPT['Timestamp (UTC)'] = df_hourly_1_NPT['Timestamp (UTC)'].dt.strftime('%m/%d/%Y %H:%M')

        # precision value adjustment for data
        df_hourly_1_NPT[
            ['PM1.0 (ug/m3)', 'PM2.5 (ug/m3)', 'PM4.0 (ug/m3)', 'PM10 (ug/m3)', 'Typical Particle Size (um)']] = \
            df_hourly_1_NPT[
                ['PM1.0 (ug/m3)', 'PM2.5 (ug/m3)', 'PM4.0 (ug/m3)', 'PM10 (ug/m3)',
                 'Typical Particle Size (um)']].round(2)

        df_hourly_1_NPT[
            ['PM0.5 NC (#/cm3)', 'PM1.0 NC (#/cm3)', 'PM2.5 NC (#/cm3)', 'PM4.0 NC (#/cm3)', 'PM10 NC (#/cm3)',
             'Temperature (Celsius)', 'Relative Humidity (%)', 'Time Delta']] = df_hourly_1_NPT[
            ['PM0.5 NC (#/cm3)', 'PM1.0 NC (#/cm3)', 'PM2.5 NC (#/cm3)', 'PM4.0 NC (#/cm3)', 'PM10 NC (#/cm3)',
             'Temperature (Celsius)', 'Relative Humidity (%)', 'Time Delta']].round(1)
        # print(df_hourly_1_NPT.columns)

        df_hourly_1_NPT.rename(columns={'Timestamp (UTC)': 'Timestamp (NPT)'}, inplace=True)
        # writing it to a new CSV file
        df_hourly_1_NPT.to_csv('Level1_hourly_with_NPT.csv', index=False)
    except:
        print("Had error while converting to local time Hourly data.")



mergeeverything()

directory = r'D:\Air Data'
destinationdirectory = r'D:\Air Data\Data From Our Server'

# iterate over files in
# that directory
for filename in os.listdir(directory):
	f = os.path.join(directory, filename)
	j = os.path.join(destinationdirectory, filename)
	# checking if it is a file
	if os.path.isfile(f) and f[-4:]==".csv":
		#print(f)
		shutil.move(f,j)


ITEM_LIST=[-12,-8,-6,-1]

for i in ITEM_LIST:
    driver = webdriver.Chrome(executable_path="./chromedriver")

    driver.get("http://smog.spatialapps.net/apps/airqualitynp/")

    driver.maximize_window()  # Maximize the page
    try:
        WebDriverWait(driver, 150).until(EC.presence_of_element_located((By.CLASS_NAME, "pollutant-cascader")))
    finally:

        tripdash = driver.find_elements(By.CLASS_NAME, "pollutant-cascader")
        td = tripdash[-1]
        ActionChains(driver).click(td).perform()
        time.sleep(3)
        Select_item = driver.find_elements(By.CLASS_NAME, "el-select-dropdown__item")
        sl = Select_item[i]
        # negative numbering for the list item works the best here for some weird reasons.
        ActionChains(driver).click(sl).perform()
        time.sleep(2)

        Calculate = driver.find_element("xpath",
            "/html/body/div[1]/div/section/section/div/div[2]/div[1]/div/div[1]/div[1]/div/div/div[2]/div/div[1]/div/button")
        ActionChains(driver).click(Calculate).perform()
        time.sleep(3)
        CSV_drop = driver.find_elements(By.CLASS_NAME, "highcharts-exporting-group")
        td1 = CSV_drop[3]
        ActionChains(driver).click(td1).perform()
        downcsv = driver.find_elements(By.CLASS_NAME, "highcharts-menu-item")[-2]
        ActionChains(driver).click(downcsv).perform()
        time.sleep(3)
        driver.close()

"""
# list of Dashboard sensor
Bhaisipati  -27 
Bhaktapur -26
Bharatpur -25
Bhimdatta (Mahendranagar) -24
Biratnagar -23 
DHM, Pkr -22
Damak -21
Dang -20
Dhangadhi -19
Dhankuta -18
Dhulikhel -17
GBS, Pkr -16
Hetauda -15
Janakpur  -14 
Jhumka  -13
Khumaltar -12
Lumbini  -11
Nepalgunj  -10
PU Pkr -9
Pulchowk -8
Rara -7
Ratnapark -6
Sauraha -5
Shankapark  -4
Simara  -3
Surkhet  -2
TU Kritipur -1
"""

directory = r'C:\Users\trb50\Downloads'
destinationdirectory = r'D:\Air Data\Data from ICIMOD Dashboard'

# iterate over files in
# that directory
for filename in os.listdir(directory):
	f = os.path.join(directory, filename)
	j = os.path.join(destinationdirectory, filename)
	# checking if it is a file
	if os.path.isfile(f) and f[-4:]==".csv":
		#print(f)
		shutil.move(f,j)
        
print("Progam completed suscessully, Data extracted from the server and stored locally")
time.sleep(10)
