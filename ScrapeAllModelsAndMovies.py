"""
Gets the list of  all movies any car make and model were in from IMCDB.com 

Inout is a scraped csv of all car makes and models also from IMCDB.com
Exports results in csv form, yielded over 1,000,000 unique car model appearances in movies

The list of makes and models 'ModelAppearanceCounts.csv' 
was initially scraped using "ScrapeModelAppearanceCounts.py" file
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def get_IMCDB_results_link(url):
    """
    Input an IMCDB url from a selected car model displayed as an uncleaned list
    
    For example this will get a Dastun 240z:
        https://www.imcdb.org/search.php?resultsStyle=asList&sortBy=0&make=Datsun&model=240Z&modelMatch=1&modelInclModel=on
    
    The list must still be cleaned
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    html = list(soup.children)[2]
    body = list(html.children)[3]
    pagedetails = list(body.children)[9]
    textstring = pagedetails.get_text()
    textstringsplit = textstring.split('\n')
    return (textstringsplit)

#begin the cleanup of the result
def clean_up_IMCDB(resultlist):
    """
    Cleans up the returned movie list of a url 
    """
    while "" in resultlist:
        resultlist.remove("") #removes empty spaces 
    resultlist = resultlist[2:] #remove the headers
    for i in range(0, len(resultlist)):
        resultlist[i] = resultlist[i].split(' in ') #splits the text
        movieinfo = resultlist[i][1].split(',') #gets the movie info
        resultlist[i] =  movieinfo #updates the list of movie info
    for i, j in enumerate(resultlist):
        if len(resultlist[i]) != 3:
            del resultlist[i] #TODO this removes things that were incorrectly split errors to be improved in later versions
    return resultlist


def get_IMCDB_results_full(Make, Model):
    """
    Input car make, model
    Returns list of movies the car was in    
    """
    Model.replace(' ', '+')
    urlforrequest = 'https://www.imcdb.org/search.php?resultsStyle=asList&sortBy=0&make={}&model={}&modelMatch=1&modelInclModel=on&page=1'.format(Make, Model)
    reslist = get_IMCDB_results_link(urlforrequest)
    numberofpages = 1
    if 'Page' in reslist[0]:
        #if the resullts have more than one page
        numberofpages = int(reslist[0].split('/')[1][0]) #gets the number of pages in total there are 
    reslist = clean_up_IMCDB(reslist) #cleans up the first or only result
    if numberofpages > 1:
        #if there is more than one link required
        i = 2
        while i <= numberofpages:
            urlforrequest = urlforrequest[:-1] + str(i) #updates the page number 
            linkresult = get_IMCDB_results_link(urlforrequest) #gets the result
            linkresult = clean_up_IMCDB(linkresult) #cleans the result
            for movie in linkresult:
                reslist.append(movie) #adds on the movies 
            i = i+1
    #remove the row if it did not yield a full result (for example if missing a movie year)
    for i, j in enumerate(reslist):
        if len(reslist[i]) != 3:
            del reslist[i]
    #add the make and model to each of the rows
    for i, j in enumerate(reslist):
        reslist[i].insert(0, Model) #inserts the model into each row
        reslist[i].insert(0, Make) #inserts the make into each row
        reslist[i][3] = reslist[i][3].strip() #cleans up trailing spaces on the type of film 
        reslist[i][4] = reslist[i][4].strip() #cleans up trailing spaces on the year of film 
    return(reslist)


"""
Now scrape all of the makes and models movies to compile a gigantic list of every car in ever
The list of every model ever was scraped using the file ScrapeModelAppearanceCounts.py and saved to csv
"""

makesandmodels = pd.read_csv('ModelAppearanceCounts.csv') #gets a list of all the make and models spraped from results of ScrapeModelAppearanceCounts.py
makesandmodels = makesandmodels.values.tolist() #converts the csv to list 
everycarever = [] #will serve as a list of every identified car in every movie ever (at least if its on IMCDB)
counter = 0 #a counter to monitor the progress
errormodels = []
now = str(datetime.now()) #gets the datetime
print('Starting extraction loop at: '+now) #prints when the loop started
for car in makesandmodels:
    try:
        modelresults = get_IMCDB_results_full(car[0], car[1]) #gets the result
        everycarever.extend(modelresults) #adds the results to the main full list
    except:
        errormodels.append([car[0], car[1]]) #if there was an error record the make and model
    counter = counter + 1 #serves a s a counter for what models were not able to be retrieved
    if counter % 1000 == 0:
        print('On car model number '+str(counter))


#print the results of the export 
now = str(datetime.now())
print('Extraction loop ended at: '+now) #prints time the full scrape ended
if len(errormodels) != 0:
    print('Models which could not be retrieved:')
    print(errormodels)
else:
    print('No car models caused extraction error')
    
#save to csv
df = pd.DataFrame(everycarever)
columnnames = ['Make', 'Model', 'Title', 'TitleType', 'TitleYear', 'unknown'] #name the columns
df.columns = columnnames #convert to dataframe
df.to_csv('AllCars.csv')
