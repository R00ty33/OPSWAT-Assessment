# imports
from pip._vendor import requests #requests
import hashlib #hashing
import json #json parser

# attributes
url = "https://api.metadefender.com/v4/file" 
ContentType = 'application/octet-stream' 
apikey = '' # *** ENTER YOUR API-KEY HERE ***
file = '' # *** ENTER THE FILE LOCATION HERE, SIZE < 140Mb*** 

# Read File
binary_file = open(file, 'rb') # opening file to read as binary
data = binary_file.read() # binary for file is stored in variable data
binary_file.close() # closes file

#Calculate the hash of the given samplefile
hash_object = hashlib.sha1(data) # Creates sha1 hash object
hash_file = hash_object.hexdigest() # Converts hash object to hexadecimal


#Perform hash lookup at metadefender.opswat.com

# HTTP Header for hash look up
url = "https://api.metadefender.com/v4/hash/" + hash_file
headers = { 
 "apikey": apikey
}
# GET response for hash lookup
response = requests.request("GET", url, headers=headers)
print("Hash look up on: " + hash_file)
if (response.status_code == 200): # if hash exists
    print("Hash exists\nResults:")
    json_data = response.json() if response.status_code == 200 else None
    data_id = json_data['data_id']
    print(json.dumps(json_data, indent = 3))

elif (response.status_code == 404): # if hash does not exist
    # HTTP Header to upload file
    print("Hash does not exist \nUploading file...")
    url = "https://api.metadefender.com/v4/file" 
    headers = {
    "apikey": apikey,
    "Content-Type": ContentType,
    }
    # POST response to upload file
    response = requests.request("POST", url, headers=headers, data="hash_file") 
    json_data = response.json() if response.status_code == 200 else None
    print("Scan queue: " + str(json_data['in_queue']))
    data_id = json_data['data_id'] # obtains data_id for fetching results

    # HTTP Header to fetch analysis results
    url = "https://api.metadefender.com/v4/file/" + data_id
    headers = { # DO NOT CHANGE
    "apikey": apikey,
    "x-file-metadata": "{x-file-metadata}"
    }
    response = requests.request("GET", url, headers=headers)
    json_data = response.json() if response.status_code == 200 else None

    # Repeatedly polls on data_id to fetch analysis results
    while(json_data['scan_results']['progress_percentage'] != 100): 
        print("Scan Progress Percentage... " + str(json_data['scan_results']['progress_percentage']) + "%")
        response = requests.request("GET", url, headers=headers)
        json_data = response.json() if response.status_code == 200 else None
    
    # Progress_Percentage = %100
    print("Results " + json.dumps(json_data, indent = 3))
    

else: # error occured
    print(response.status_code)
    print(response.text)