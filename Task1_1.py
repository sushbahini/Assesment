import os
import json
import subprocess
import time
import csv

#Below links are for the given task and  is iterated from first to last number for the given links
task1="curl https://www.thegazette.co.uk/all-notices/notice/data.json?start-publish-date=2021-01-01\&end-publish-date=2021-01-31\&results-page"  

'''
The logic here is to make a single request for the task urls provided above and then get the links object and then find the last number for the given url
and then get all entries and do all necessary checks to avoid data duplicacy and retrieve only needed data and follow the data governance like when looping have a sleep for mora than 1 sec.
'''

def task1_1linux_way():
    json_string = subprocess.check_output(task1, shell=True)
    json_dictionary = json.loads(json_string)

    # Getting the last page
    for dict in json_dictionary['link']:
        if dict['@rel'] == "last" and dict['@type'] == "application/json":
            last_page_number = dict['@href'].split("=")[-1]
            print(last_page_number)

    #Getting all entries and filtering based on notice codes and avoiding duplicates in output file  
    for x in range(1, int(last_page_number)):
        print("executing "+str(x) +"of " +str(last_page_number))
        json_string = subprocess.check_output(task1+"="+str(x)+" | jq \".entry\"", shell=True)
        json_dictionary = json.loads(json_string)
        for dict in json_dictionary:
            if 'f:notice-code' in dict:
                print(str(dict['f:notice-code']))

                #below is used for task 1_1
                if dict['f:notice-code'] == "2443":
                    print(str(dict))
                    with open('data_task1_1.json') as json_file:
                        print("data_task1_1.json")
                        data = json.load(json_file)
                        temp = data['entries']
                        #checking for duplicates
                        duplicate = False
                        if len(data['entries']) > 0:
                            for entry in data['entries']:
                                if entry['id'] == dict['id']:
                                    duplicate = True
                        if duplicate == False:
                            temp.append(dict)
                    write_json(data,"data_task1_1.json")
        time.sleep(5)

def write_json(data, filename):
    with open(filename,'w') as f:
        json.dump(data, f, indent=4)

#Below method is to convert json file with entries object into csv format with some data filteration
def jsonToCsv(file1,file2):
    with open(file1) as json_file:
        data = json.load(json_file)
        entries = data['entries']   
        # now we will open a file for writing
        data_file = open(file2, 'w')  
        # create the csv writer object
        csv_writer = csv.writer(data_file)
        # Counter variable used for writing 
        # headers to the CSV file
        count = 0
        
        for entry in entries:
            entry['id'] = entry['id'].split("/")[-1]
            entry['author'] = entry['author']['name']
            if "geo:Point" in entry:
                del entry['geo:Point']
           # entry["content"] = entry["content"].split("<div><p>")[1].split("</p></div>")[0]
            if count == 0:
        
                # Writing headers of CSV file
                header = entry.keys()
                csv_writer.writerow(header)
                count += 1
        
            # Writing data of CSV file
            csv_writer.writerow(entry.values())
        
        data_file.close()

#if this file is executed from multiple sources then the output data can be merged with this given method.
def joinDataFiles(file1,file2):
    with open(file1) as json_file:
        data_task = json.load(json_file)
        temp = data_task['entries']
        #checking for duplicates
        duplicate = False
        with open(file2) as json_file1:
            data2 = json.load(json_file1)
            for entry in data2['entries']:
                temp.append(entry)
    write_json(data_task,"data_task1_1.json")

#This method can be used to check wheter the retrived dataset with entries object has duplicate or not and remove if found any duplicates.
def findDuplicates(file1_input,file2_output):
    with open(file2_output) as json_file:
        data_out = json.load(json_file)
        temp_out = data_out['entries']
        with open(file1_input) as json_file:
            data_in = json.load(json_file)
            temp_in = data_in['entries']
            for ent in temp_in:
                count = 0
                duplicate = False
                if len(data_in['entries']) > 0:
                    for entry in data_in['entries']:
                        if entry['id'] == ent['id']:
                            count=count+1
                            if count > 1:
                                duplicate = True
                if duplicate == False:
                    temp_out.append(ent)
    write_json(data_out,file2_output)


#Below will collect all data from the given link
#task1_1linux_way()

# below will check for duplicates in the final file
#findDuplicates("data.json","final_data_output.json")

# Below will join two given json files
#joinDataFiles("data_task1_1.json","2020.json")

#Below will convert json file to csv format
jsonToCsv("example.json","example.csv")