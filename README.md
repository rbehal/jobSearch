# jobSearch

Python web scraper to compile multiple job search details from around the web into a single Excel document. Simply enter a search term (or multiple separated by a semicolon) and press enter. An Excel file that cleanly displays all of the job details and direct-to-apply links if available will be created.

![image](https://user-images.githubusercontent.com/1645830/88484066-f2188480-cf39-11ea-8156-37c3c5469543.png)

## Key features

- A similarity algorithm is run so that you only get *unique* job postings, as employers often post the same job on muiltiple sites. 

- A VBA macro is implemented such that as you scroll through the jobs, if you delete the description of a job, this job will be considered "seen" and will never appear in your search results again.

## Tools/Software

- Python
- BeautifulSoup
- Bit.ly API 
- Xlsxwriter
