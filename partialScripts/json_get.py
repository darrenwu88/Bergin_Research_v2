import requests
import json
from datetime import datetime
import os

""" Last updated: 14-Sep-2021
    Author: Caldow
    Python 3.9.5
This sample code allows a user to download data from TSI-Link.  Also needed: 
    1. A license from TSI for API data access for each of the sensors you 
       wish to access
    2. Your client credentials from TSI-Link (API tab)
The code is broken into five blocks
    1. Read credentials file
    2. Read or request and update the cached security token (POST)
    3. Get the sensor information (GET)
    4. Get the telemetry data (GET)
    5. Save data to a file
Disclaimer:  This sample code and instructions are provided without any 
guarantee or warranty. It is purposely simplistic so the basics can be 
understood.  It does not have extensive error checking or a complex user 
interface. TSI is not responsible for any damage or data loss due to using 
or modifying the code below.
-------------- Read credentials file --------------"""
#replace filename with your file from TSI-L ink API
with open(os.path.join(r'./admin_secrets', "secrets-c2mgvpsfp7ufo92pvpp0.json")) as cred_file:  
    cred_data = json.load(cred_file)
    
"""-------------- Get security token information --------------
The security token is required to get any other information from TSI-Link.  
It is generally valid for 24 hours (86400 seconds) after it has been returned 
so you do not have to call it repeatedly. In fact if you call too often you 
will get an error so it is cached in a local file.
"""
#read security token cache file
CACHE_FILENAME = "tokencache.txt"
tok_expires = 86400 #24 hrs typical
BUFFER = 120 #seconds.  How long it takes to run the rest of your program 
# after reading the security token.  Increase if needed.
tokencached = False
if os.path.exists(CACHE_FILENAME):
    modified=os.path.getmtime(CACHE_FILENAME)
    now = datetime.now().timestamp()    
    delta = now - modified
    if delta < (tok_expires - BUFFER):  #if token is still valid, read it
        tokencached = True
    else:
        tokencached = False
        print("Token code expired: get new token and write to file")
else:
    tokencached = False
    print("No token code file found")
    
if tokencached == True:
    cfile = open(CACHE_FILENAME,'r')
    tok_code = cfile.read()
    print("Read valid token code")
    cfile.close()
else:
    #need to get token and write to file
    url = "https://tsilink.com/oauth/token"
    payload = json.dumps({
      "grant_type": "client_credentials",
      "client_id": cred_data['id'],                  
      "audience": cred_data['audience'],
      "client_secret": cred_data['secret'], 
    })
    
    headers = {
      'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    response_json = response.json()
    print(response_json)
    tok_code = response_json['access_token']
    tok_type = response_json['token_type'] 
    tok_expires = int(response_json['expires_in'])
    
    cfile = open(CACHE_FILENAME,'w')
    cfile.write(tok_code)
    cfile.close()
    print("Token written to file")
"""-------------- Get sensor information --------------
Note that the response is a list of sensors with dictionary entries for 
each. The metadata entry is also a dictionary
"""
url = "https://tsilink.com/api/v2/external/devices"
payload={}
headers={}
tok_code = "Bearer " + tok_code
headers['Authorization'] = tok_code
response = requests.request("GET", url, headers=headers, data=payload)
response_json = response.json()
#Extract useful information from response and store in sensor_info dict
num_sensors = len(response_json)
sensor_info = []
for dic in response_json:
    meta = dic['metadata']
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
    
#print(sensor_info)
"""-------------- Get telemetry data --------------
There are several ways to get telemetry data for each device:
    1. no arguments will return the last single record
    2. data_age with an integer will return an integer number of 
       days of records up to 30 days
    3. data_start_date + data_age will return an integer number of days 
       from the start date
    4. data_start_date + data_end_date will return records between the 
       two dates
Records can be returned in either json or .csv format based on the 
optional "Accept" header below.
    
Uncomment the values below for the desired effect.
"""
url = "https://tsilink.com/api/v2/external/telemetry"
params={}
payload={}
headers={}
fname_s = fname_e = ""
data_start_date = data_age = data_end_date = ""
headers['Authorization'] = tok_code
#optional arguments
#headers.update({'Accept': 'text/csv'})  #comment out this line for json
#data_age="&age=1" #days of data (can be used with start date)
data_start_date = "&start_date=2022-03-01T00:00:00.000Z"  #use UTC format.  
data_end_date = "&end_date=2022-03-02T00:00:00.000Z"  #use UTC format
if (data_start_date != "" and data_end_date != ""):
    fname_s = data_start_date[12:22]  #only want the date part of the string
    fname_e = data_end_date[10:20]


for x in range(num_sensors):
    filename = sensor_info[x]['serial']+"_"+fname_s+"_"+fname_e+".csv"
    dev_id="?device_id="+sensor_info[x]['device_id']
    response = requests.request("GET", url+dev_id+data_age+data_start_date+\
                                data_end_date, headers=headers, data=payload)
#-------------- Save telemetry data to .csv files --------------
    f = open(filename,"w")
    #f.write("device_id,"+sensor_info[x]['device_id']+"\n")
    #f.write("model,"+sensor_info[x]['model']+"\n")
    #f.write("serial,"+sensor_info[x]['serial']+"\n")
    #f.write("friendlyName,"+sensor_info[x]['friendlyName']+"\n")
    #f.write("is_indoor,"+format(sensor_info[x]['is_indoor'])+"\n")
    #f.write("latitude,"+format(sensor_info[x]['latitude'])+"\n")
    #f.write("longitude,"+format(sensor_info[x]['longitude'])+"\n")
    #f.write("\n")
    f.write(response.text)
    f.close()

