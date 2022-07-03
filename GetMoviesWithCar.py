"""
Script asks user for input on car make and model. 
Returns list of all movies the car is in.

Uses requests and beautiful soup library to scrape data from IMCDB (Internet Movie Car Database)

IMCDB Link:
    https://www.imcdb.org/ 

Input example: 
For example try Make = 'Nissan' and Model = '350Z'
"""

import requests
from bs4 import BeautifulSoup


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
        resultlist[i] = resultlist[i].split(' in ')[1] #gets just the movie, make and model added in later
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
    return(reslist)

def main():
    """
    Asks user for input of a car make and model 
    Returns list of movies the car was in and a count 
    """   
    cont = 'y' #input to ask user if they want to look up another car
    while cont == 'y':
        carmake = input('\nEnter a car make:')
        carmodel = input('\nEnter car model:')
        movielist  = get_IMCDB_results_full(carmake, carmodel) #gets the list of all movies that car was found
        numbmovies = len(movielist) # counts number of movies in list
        for movie in movielist:
            print(movie) #prints all the movies
        print('\nNumber of movies '+carmake+' '+carmodel+' was found in: '+str(numbmovies))
        cont = input("\nWould you like to search for another car(type 'y' to continue):").lower()
        
if __name__=='__main__':
    main()
    
    
