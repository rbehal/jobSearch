from HelperFuncs import *

class LinkedInJob:
    def __init__(self, ID, posting):
        self.id = ID
        self.posting = posting
        self.platform = "LinkedIn"
        
        self.setTitle()
        self.setCompany()
        
        if not checkJobsToIgnore(self):
            self.valid = False
            return
        else:
            self.valid = True
            
        self.setDetailedSoup()
        self.setDatePosted()
        self.setLocation()
        self.setDescription()
        self.setApply()
        
        
    def setTitle(self):
        self.title = self.posting.find("span", class_ = "screen-reader-text").text        
        
        
    def setDatePosted(self):
        def checkDateClass(class_):
            return class_ is not None and "listdate" in class_ 
        
        self.datePosted = self.posting.find("time", class_ = checkDateClass).text        
        today = date.today()
        
        if ("hour" in self.datePosted):
            self.datePosted = today.strftime("%m/%d/%y")
        elif (self.datePosted[0:2].isdigit()): # Checks if more than 9 days ago
            datetimePosted = today - timedelta(days=int(self.datePosted[0:2])) # Gets datetime object
            self.datePosted = datetimePosted.strftime("%m/%d/%y")
        else:
            datetimePosted = today - timedelta(days=int(self.datePosted[0])) # Gets datetime object
            self.datePosted = datetimePosted.strftime("%m/%d/%y")
        
        
    def setLocation(self):
        self.location = self.posting.find("span", class_ = "job-result-card__location").text
        
        
    def setCompany(self):
        def checkCompanyClass(class_):
            return class_ is not None and "result-card__subtitle" in class_ 
        
        companyDiv = self.posting.find("h4", checkCompanyClass)
        if (companyDiv is not None):
            self.company = companyDiv.text
        else:
            self.company = None
    
    
    def setDetailedSoup(self):# Soup for the separate page for viewing job description
        self.detailsURL = self.posting.find("a", class_ = "result-card__full-card-link").get("href")
        self.detailedSoup = createSoup(self.detailsURL)
       
        
    def setDescription(self):  
        descriptionTextDiv = self.detailedSoup.find("section", class_ = "description").findAll(['p', 'li'])
        
        if (descriptionTextDiv is not None):
            self.description = ""
            for element in descriptionTextDiv:
                if (element.name is 'p'):
                    self.description += element.text + 2*chr(10) # 10 is new line character
                else:
                    self.description += element.text + chr(10)   
        else:
            self.description = None
             
        
    def setApply(self):
        applyDiv = self.detailedSoup.find("a", class_ = "apply-button apply-button--link")
        if (applyDiv is not None):
            applyLink = applyDiv.get("href")
            if len(applyLink) < 250:
                self.applyLink = applyLink
            else:
                self.applyLink = shortenLink(applyLink)
        else:
            self.applyLink = self.detailsURL
        


def getLinkedInJobs(searchTerm):
    filteredTerm = ""
    for letter in searchTerm: # Replacing spaces with %20s for indeed query
        if (letter != " "):
            filteredTerm += letter
        else:
            filteredTerm += "%20"

    URL = "https://www.linkedin.com/jobs/search/?geoId=101174742&keywords=" + filteredTerm + "&location=Canada&sortBy=DD&f_TP=1%2C2&redirect=false&position=1&pageNum=0"
    
    try: # Perhaps handle differently later
        soup = createSoup(URL)
    except:
        return []
    
    def postingCheck(entityUrn):
        return entityUrn is not None and "jobPosting" in entityUrn
    jobPostings = soup.findAll("li", {"data-entity-urn" : postingCheck}) #jobPostings follow this
    
    # Creating jobs array
    jobs = []
    for posting in jobPostings:
        jobID = posting.get("data-id")
        if jobID is not None:
            job = LinkedInJob(jobID, posting)
            if (job.valid):
                jobs.append(job)
    
    return jobs