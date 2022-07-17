"""
Gets list of models of the top brands from scraping IMCDB website

Data source: https://www.imcdb.org/ 

Saves data to csv with each row as [make, model, movie appearance count]

"""

import requests
from bs4 import BeautifulSoup
import pandas as pd 
import time 

def get_list_of_brand_models(brand):
    """
    Gets a list of all the brand's models from IMCDB website
    Input a string brand name 'Brand' such as 'Lamborghini'
    Returns list of: ['brand', model',(count of model appearances)'] 
    """
    url = 'https://www.imcdb.org/vehicles_make-'+brand+'.html' #generates the url for the request url
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    html = list(soup.children)[2]
    body = list(html.children)[3]
    pagedetails = list(body.children)[9]
    textstring = pagedetails.get_text()
    textstringsplit = textstring.split('\n')
    while "" in textstringsplit:
        textstringsplit.remove("") #removes empty spaces 
    textstringsplit = textstringsplit[1:] #removes the header off the list 
    #try statement below is for ensuring a list returned
    try:
        if "(none)" in textstringsplit[0]:
            #renames 'none' meaning unidentified car models from the list for a clean dataframe
            textstringsplit[0] = textstringsplit[0].replace('(none)', 'Unidentified') 
    except:
        return None #an error occured and it did not return a list
    for i, s in enumerate(textstringsplit):
        textstringsplit[i] = s.split(' (') #splits the string by model name and appearance count
        textstringsplit[i][1] = textstringsplit[i][1].replace(')', '') #cleans the other right hand paarantheses
        textstringsplit[i].insert(0, brand) #adds the brand into the list
    return textstringsplit

#read the top brands file 
brandsfile = open('TopBrands.txt', 'r')
brands = brandsfile.read()
brands = brands.split('\n')

#get the list of models in each make and number of appearances for each make 
modelcounts = [] #will be full list of top makes in form [make, model, apperance count]
for make in brands:
    time.sleep(1) #1 second delay to avoid risking overwhelming website 
    print('Retrieving '+make+' models counts...')
    makelist = get_list_of_brand_models(make)
    if makelist is not None:
        for model in makelist:
            modelcounts.append(model) #add the data to the full list

#drop anything row in model counts with a length greater than 3
#TODO this is a temproary workaround for an error occuring only on a few models
for j, t in enumerate(modelcounts):
    if len(modelcounts[j]) > 3:
        del modelcounts[j]

#model counts now populated with full data, save to csv 
df = pd.DataFrame(modelcounts)
df.columns = ['Make', 'Model', 'AppearanceCount']
df.to_csv('ModelAppearanceCounts.csv', index=False)

