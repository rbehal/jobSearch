from HelperFuncs import *

class MonsterJob:
    def __init__(self, ID, posting):
        self.id = ID
        self.posting = posting
        self.platform = "Monster"
        
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
        self.titleSoup = self.posting.find("h2", class_ = "title") 
        self.title = removeNL(self.titleSoup.text)
        
        
    def setDatePosted(self):
        self.datePosted = self.posting.find("time").text  
        today = date.today()

        if (self.datePosted[0:2].isdigit()): # Checks if more than 9 days ago
            datetimePosted = today - timedelta(days=int(self.datePosted[0:2])) # Gets datetime object
            self.datePosted = datetimePosted.strftime("%m/%d/%y")
        elif (self.datePosted[0].isdigit()):
            datetimePosted = today - timedelta(days=int(self.datePosted[0])) # Gets datetime object
            self.datePosted = datetimePosted.strftime("%m/%d/%y")
        else:
            self.datePosted = today.strftime("%m/%d/%y")          
        
        
    def setLocation(self):
        locationClass = self.posting.find("div", class_ = "location")
        self.location = removeNL(locationClass.find("span", class_ = "name").text)
        self.location = self.location.title() # Convers to proper case
        
        
    def setCompany(self):
        locationClass = self.posting.find("div", class_ = "company")
        self.company = removeNL(locationClass.find("span", class_ = "name").text)
    
    
    def setDetailedSoup(self):# Soup for the separate page for viewing job description
        self.detailsURL = self.titleSoup.find("a").get("href")
        try: # Causes error if non ASCII characters are in the link
            self.detailedSoup = createSoup(self.detailsURL)
        except:
            self.detailedSoup = None
        
        
    def setDescription(self):   
        if (self.detailedSoup is None):
            self.description = None
            return;        
        
        # Creates description adding newlines between paragraphs
        descriptionTextDiv = self.detailedSoup.findAll(['p', 'li'])
        
        if (descriptionTextDiv is not None):
            self.description = ""
        else:
            self.description = None

        for element in descriptionTextDiv[14:(len(descriptionTextDiv) - 1)]: # Slices to only get necessary text
            if (element.name is 'p'):
                self.description += element.text + 2*chr(10) # 10 is new line character
            else:
                self.description += element.text + chr(10)           
            
    def setApply(self):
        if (self.detailedSoup is None or ("applyOnlineUrl" in str(self.detailedSoup.text)) is False):
            self.applyLink = None
            return
        else:
            applyLinkHTML = str(self.detailedSoup.text)
    
        applyLinkRawPattern = re.compile(r"^(.+?)applyOnlineUrl\":\"(.+?)\",\"applyType(.+?)$", re.MULTILINE | re.DOTALL) # Regex for where the URL is stored

        applyLinkRaw = re.search(applyLinkRawPattern, applyLinkHTML) # Raw pattern
        applyLinkRaw = applyLinkRaw.group(2).replace("u002F", "") # Removes u002F characters

        # If there is an ad link, remove the ad part 
        applyLinkAdPattern = re.compile(r"^https:(.+?)ad.doubleclick.net(.+?)\?(.+?)$", re.MULTILINE | re.DOTALL)
        applyLinkAdRaw = re.search(applyLinkAdPattern, applyLinkRaw)

        # Set the final apply links
        if applyLinkAdRaw is None:
            self.applyLink = applyLinkRaw
        else:
            self.applyLink = applyLinkAdRaw.group(3)
            
        self.applyLink = self.applyLink.replace("\\", "/")

        if len(self.applyLink) >= 250:
            self.applyLink = shortenLink(self.applyLink)



def getMonsterJobs(searchTerm):
    filteredTerm = ""
    for letter in searchTerm: # Replacing spaces with +s for indeed query
        if (letter != " "):
            filteredTerm += letter
        else:
            filteredTerm += "-"
    
    soup = createSoup("https://www.monster.ca/jobs/search/?q=" + filteredTerm + "&where=Canada")
    
    # Creating jobs array
    jobs = []
    for section in soup.find_all("section"):
        jobID = section.get("data-jobid")
        if jobID is not None:
            job = MonsterJob(jobID, section)
            if (job.valid):
                jobs.append(job)
    return jobs