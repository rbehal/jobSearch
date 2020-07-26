# Imports
from lxml import html
import requests
import bs4 as bs
import urllib.request
import regex as re
import json
from datetime import date
from datetime import timedelta
import xlsxwriter as xw
import bitly_api
import string
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
stopwords = stopwords.words('english')


def removeNL(string): # Helper function to remove new line
    removeChars = ["\n", "\r"]
    for i in range(0, 5): 
        for char in removeChars:
            string = re.sub(char + '$', '', string)
            string = re.sub('^' + char, '', string)
            
    return string


def createSoup(URL): # Create HTML parsed BS object from URL
    source = urllib \
        .request \
        .urlopen(URL) \
        .read()
    return bs.BeautifulSoup(source, 'html.parser')


def shortenLink(longURL):
    API_USER = "rbehal"
    ACCESS_TOKEN = "3c78ba7edaba170ec27e18905ac22e0af9e36419"
    
    c = bitly_api.Connection(access_token=ACCESS_TOKEN)
    response = c.shorten(longURL)
     
    return response['url']  


def removeSimilarJobs(jobs):  # Takes in a jobs array and returns the array with duplicate jobs removed
    def cleanString(description): # Helper function - Normalizes text
        if description is None:
            return ''
        description = ''.join([word for word in description if word not in string.punctuation])
        description = description.lower()

        temp = []
        for word in description.split():
            if word not in stopwords:
                temp.append(word)

        description = ' '.join(temp)

        return description
    
    def cosineSimVectors(vec1, vec2): # Helper function - Retrieve similarity (0-1)
        vec1 = vec1.reshape(1, -1)
        vec2 = vec2.reshape(1, -1)

        return cosine_similarity(vec1, vec2)[0][0]
    
    
    jobDescriptions = [job.description for job in jobs]
    cleanDescriptions = []
    for description in jobDescriptions:
        cleanDescription = cleanString(description)
        if (len(cleanDescription) > 0):
            cleanDescriptions.append(cleanDescription)

    if not (len(cleanDescriptions) > 1): 
        return jobs

    vectorizer = CountVectorizer().fit_transform(cleanDescriptions)
    vectors = vectorizer.toarray()
    
    indicesToRemove = []
    for i in range(0, len(vectors)):
        for j in range(i + 1, len(vectors)):
            if (cosineSimVectors(vectors[i], vectors[j]) > 0.9):
                indicesToRemove.append(j)

    indicesToRemove = list(set(indicesToRemove))

    jobsToRemove = [] # Must do this in two loops because dynamically removing changes indexing
    for index in indicesToRemove:
        jobsToRemove.append(jobs[index])
    for job in jobsToRemove:
        jobs.remove(job)
    
    return jobs


def initializeJobsToIgnore(): # Creates array of jobs to ignore
    file = open("jobsToIgnore.txt", "r")
    jobsToIgnoreRaw = file.readlines()
    file.close()
    
    jobsToIgnore = []
    
    for job in jobsToIgnoreRaw:
        jobsToIgnore.append(job[1:(len(job) - 2)])
    
    return jobsToIgnore


jobsToIgnore = initializeJobsToIgnore()
def checkJobsToIgnore(job):
    if ((job.title + job.company) in jobsToIgnore): # jobsToIgnore initialized in Main
        return False
    else:
        return True    