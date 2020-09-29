from HelperFuncs import * 
from IndeedJob import *
from MonsterJob import *
from LinkedInJob import *


searchTerms = input("Please enter a search term: ")
searchTerms = searchTerms.split(";")

jobs = []
for searchTerm in searchTerms:
    # TODO: Change to properly handle errors per job or something
    try:
        indeedJobs =  getIndeedJobs(searchTerm)
    except:
        indeedJobs = []
    try:
        monsterJobs = getMonsterJobs(searchTerm)
    except:
        monsterJobs = []
    try:
        linkedInJobs = getLinkedInJobs(searchTerm)
    except:
        linkedInJobs = []

    jobs.extend(indeedJobs + monsterJobs + linkedInJobs)

jobs = removeSimilarJobs(jobs)

data = []
for job in jobs:
    row = []
    
    row.append(job.title)
    row.append(job.company)
    row.append(job.datePosted)
    row.append(job.location)
    row.append(job.description)
    row.append(job.applyLink)
    row.append(job.platform)
    
    data.append(row)

fileSavePath = 'C:/Users/Rahul/Desktop/jobs.xlsm'

workbook = xw.Workbook(fileSavePath)
worksheet = workbook.add_worksheet()

tableLength = str(len(jobs) + 1) # Amount of objects in the table + 1 for header
tableRange = 'A1:G' + tableLength 
tableDataRange = 'A2:G' + tableLength

worksheet.add_table(tableRange, {'data': data,
                                 'columns': [{'header' : 'Position Title'},
                                             {'header' : 'Company'},
                                             {'header' : 'Date Posted'},
                                             {'header' : 'Location'},
                                             {'header' : 'Description'},
                                             {'header' : 'Apply Link'},
                                             {'header' : 'Platform'}],
                                 'style' : "Table Style Light 8"
                                 }) # Each job has 7 (G) attributes

# Conditional formatting based on platform
worksheet.conditional_format(tableDataRange, {'type':     'formula',
                                              'criteria': '=$G2="LinkedIn"',
                                              'format':   workbook.add_format({'bg_color' : '#FFB3B3'})})
worksheet.conditional_format(tableDataRange, {'type':     'formula',
                                              'criteria': '=$G2="Indeed"',
                                              'format':   workbook.add_format({'bg_color' : '#B3FFCC'})})
worksheet.conditional_format(tableDataRange, {'type':     'formula',
                                              'criteria': '=$G2="Monster"',
                                              'format':   workbook.add_format({'bg_color' : '#CC80FF'})})

# Column Formatting
cFormat = workbook.add_format({'align' : 'right', 'num_format' : 'mm/dd/yy'})# Column C (Date)
eFormat = workbook.add_format({'text_wrap' : True, 'valign' : 'top'})# Column E (Description)

# Adjusting column widths
worksheet.set_column(0, 0, 50)
worksheet.set_column(1, 1, 30)
worksheet.set_column(2, 2, 12, cFormat)
worksheet.set_column(3, 3, 15)
worksheet.set_column(4, 4, 70, eFormat)
worksheet.set_column(5, 5, 11)
worksheet.set_column(6, 6, 10)

# Adding VBA macro button for closing
workbook.add_vba_project('vbaProject.bin') 

worksheet.insert_button('E'+str(int(tableLength) + 2), {'macro':   'addJobsToIgnore.addJobsToIgnore',
                                                        'caption': 'Done',
                                                        'width':   200,
                                                        'height':  100})

workbook.close()