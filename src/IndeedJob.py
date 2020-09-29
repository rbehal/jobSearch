from HelperFuncs import *

class IndeedJob:
    def __init__(self, ID, soup):
        self.id = ID
        self.posting = soup.find(attrs={"data-jk": ID})
        self.platform = "Indeed"
        
        self.setTitle()
        self.setCompany()
        
        if not checkJobsToIgnore(self):
            self.valid = False
            return
        else:
            self.valid = True
            
        self.setDatePosted()
        self.setLocation()
        self.setDetailedSoup()
        self.setDescription()
        self.setApply()
       
    
    def setTitle(self):
        self.title = self.posting.find("h2", class_ = "title").text
        self.title = removeNL(self.title)
    
        
    def setDatePosted(self):
        self.datePosted = self.posting.find("span", class_ = "date").text  
        today = date.today()
        
        if (self.datePosted == "Today" or self.datePosted == "Just posted"):
            self.datePosted = today.strftime("%m/%d/%y")
        elif (self.datePosted[0:2].isdigit()): # Checks if more than 9 days ago
            datetimePosted = today - timedelta(days=int(self.datePosted[0:2])) # Gets datetime object
            self.datePosted = datetimePosted.strftime("%m/%d/%y")
        else:
            datetimePosted = today - timedelta(days=int(self.datePosted[0])) # Gets datetime object
            self.datePosted = datetimePosted.strftime("%m/%d/%y")
          
        
    def setLocation(self):
        def checkLocation(class_):
            return class_ is not None and "location" in class_
        self.location = self.posting.find(class_ = checkLocation).text 
        
        
    def setCompany(self):
        self.company = self.posting.find("span", class_ = "company").text
        self.company = removeNL(self.company)
        
        
    def setDetailedSoup(self):# Soup for the separate page for viewing job description
        self.detailsURL = "https://ca.indeed.com/viewjob" + "?jk=" + self.id
        self.detailedSoup = createSoup(self.detailsURL)
        
        
    def setDescription(self):   
        descriptionTextDiv = self.detailedSoup.find("div", {"id" : "jobDescriptionText"})
        self.description = ""
        for element in descriptionTextDiv.findAll(['p', 'li']): # Creates description adding newlines between paragraphs
            if (element.name is 'p'):
                self.description += element.text + 2*chr(10) # 10 is new line character
            else:
                self.description += element.text + chr(10)
            
            
    def setApply(self):
        applyLinkDiv = self.detailedSoup.find("div", {"id" : "viewJobButtonLinkContainer"})
        
        if applyLinkDiv is not None:
            self.applyLink = applyLinkDiv.find("div", class_ = "icl-u-lg-hide").find('a').get('href')
        else:
            self.applyLink = self.detailsURL

        if len(self.applyLink) >= 250:
            self.applyLink = shortenLink(applyLink)



def getIndeedJobs(searchTerm):
    filteredTerm = ""
    for letter in searchTerm: # Replacing spaces with +s for indeed query
        if (letter != " "):
            filteredTerm += letter
        else:
            filteredTerm += "+"
    
    soup = createSoup("https://ca.indeed.com/jobs?q=" + filteredTerm + "&l=Canada&sort=date")
    jobIDsHTML = None

    for script in soup.find_all("script", {"src":False}):
        if ("jobKeysWithInfo['" in str(script)): # This is where jobIDs are stored
            jobIDsHTML = str(script)

    if (jobIDsHTML is None):
        return [] 
            
    # Create array of jobs
    jobIDRawPattern = re.compile(r"^(.+?)jobKeysWithInfo\['(.+?)'\](.+?)$", re.MULTILINE | re.DOTALL)
    jobIDsRaw = re.findall(jobIDRawPattern, jobIDsHTML)
    jobIDPattern = re.compile(r"^[A-Fa-f0-9]{16}$")
    jobs = []
    
    for row in jobIDsRaw:
        for entry in row:
            if re.match(jobIDPattern, entry):                
                # Creating job
                job = IndeedJob(entry, soup)
                if (job.valid):
                    jobs.append(job)    

    return jobs
