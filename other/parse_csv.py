import csv

with open('input.csv', 'r') as csv_file: 
    csv_reader = csv.DictReader(csv_file) # add , delimiter=',' to specify delimiter

    # next(csv_reader)  # skips over both header rows 

    for line in csv_reader:
       # print(line) # prints "['GFMS', 'http://flood.umd.edu/', '2014'...etc]"
        print(line['topic']) # prints "GFMS"




'''
sample csv: file.csv

(CSV file header) 6 fields total 
topic,name,website,publication,conf-level,identifier

DictReader returns:
OrderedDict([('topic', 'Flooding'), ('name', 'GFMS')...etc])

'''
