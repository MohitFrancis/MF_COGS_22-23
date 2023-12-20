'''
Program:    MF_GISY6060_Webscraping.py
Programmer: Mohit Francis
Date:       28 March 2023
Purpose:    GISY 6060 - Assignment 4 - Web Scraping Script
            Receives a user’s input, uses search patterns on web pages to locate the longitude
            and latitude values of each city and writes the city name, country/US state name,
            longitude, and latitude to the Python console shell.  The user has the option to
            enter another city, if they wish to see coordinates of more than one city, or the
            the option to exit the program. The start and stop times of the script must also be
            printed to the Python shell window.
'''


## Import libraries:
## sys manipulates Python's runtime environment.
## re is Python's Regular Expression / RegEx module.
## urllib is a web scraping module.
## urllib.request is the library which allows website access.
## datetime is for displaying timestamps of script start and end times.
import sys

import re

import urllib 

from urllib import request 

from datetime import datetime 


## The following dictionary by Roger Allen, available under public domain, and sourced from: https://gist.github.com/rogerallen/1583593.
## Modified to exclude all US territories except the District of Columbia/DC, which is a valid abbreviation accepted by the website.
us_state_to_abbrev = {
"Alabama": "AL",
"Alaska": "AK",
"Arizona": "AZ",
"Arkansas": "AR",
"California": "CA",
"Colorado": "CO",
"Connecticut": "CT",
"Delaware": "DE",
"Florida": "FL",
"Georgia": "GA",
"Hawaii": "HI",
"Idaho": "ID",
"Illinois": "IL",
"Indiana": "IN",
"Iowa": "IA",
"Kansas": "KS",
"Kentucky": "KY",
"Louisiana": "LA",
"Maine": "ME",
"Maryland": "MD",
"Massachusetts": "MA",
"Michigan": "MI",
"Minnesota": "MN",
"Mississippi": "MS",
"Missouri": "MO",
"Montana": "MT",
"Nebraska": "NE",
"Nevada": "NV",
"New Hampshire": "NH",
"New Jersey": "NJ",
"New Mexico": "NM",
"New York": "NY",
"North Carolina": "NC",
"North Dakota": "ND",
"Ohio": "OH",
"Oklahoma": "OK",
"Oregon": "OR",
"Pennsylvania": "PA",
"Rhode Island": "RI",
"South Carolina": "SC",
"South Dakota": "SD",
"Tennessee": "TN",
"Texas": "TX",
"Utah": "UT",
"Vermont": "VT",
"Virginia": "VA",
"Washington": "WA",
"West Virginia": "WV",
"Wisconsin": "WI",
"Wyoming": "WY",
"District of Columbia": "DC",
}


## Print welcome message and purpose of program.
print("\n" + "----- WELCOME! :)"*5, "-----\n")

print('\nThis program will allow you to find the longitude and latitude of any City in any Country or US State in the world.')


## Print messages describing optimal function of script to user.
## Print accepted US State names and abbreviations to help user.
print('\n\nRULES')

print("*****************")

print('\n1. Enter the full, correct name(s) of the city/cities you wish you search without single or double quotes. No nicknames.')

print("   E.g. Toronto; not 'Toronto', TO, or the 6ix.")

print('\n2. Capitalise each word in a name, or all letters in a US State abbreviation.')

print('   E.g. Ottawa is correctly spelled and capitalised, not Otawa or ottawa; CA is correct but not Ca or ca.')

print("\n3. Check entered names for leading or trailing whitespaces, hyphens, full stops/periods, or apostrophes.")

print("   E.g.  ..--Toronto''..   is not a valid search term, but Toronto is.")

print("\n4. If necessary, include hyphens (-), full stops/periods (.), spaces ( ), and/or apostrophes (') within location names, but not numbers or other special characters.")

print("   E.g. Southend-on-Sea or St. John's are correct, but not S=outh3n!d on Se4 or S3t J0h+n@s.")

print('\n5. Enter the most commonly used, full name(s) of the country/countries you wish to search (applies to all countries except the US/United States), though certain exceptions apply. No abbreviations.')

print('   E.g. United Kingdom; not the UK, and definitely not the United Kingdom of Great Britain and Northern Ireland.')

print('\n6. For a city in the US/United States, enter the state name but not the country name.')

print('   E.g. California or New Hampshire, but not the United States or the United States of America.')

print('\n7. For a city in the US/United States, you may also enter the two letter State abbreviation(s) in all capitals, but not the country abbreviation.')

print('   E.g. CA for California or NH for New Hampshire, but not the US or USA.')

print("\n8. The valid US State and Territory abbreviations, with the correct formatting, are the following: \n")

for keys in us_state_to_abbrev:

    print("   " + keys + " - " + us_state_to_abbrev[keys])


## Function has_nums_specs(inputString) checks input strings for specified non-standard special characters
## (i.e. all special characters except whitespaces  , full stops/periods ., apostrophes ' , and hyphens -)
## and returns True or False.
def has_nums_specs(inputString):
    
    return bool(re.search(r'[0-9\!\$\@\#\%\^\&\*\(\)\_\+\=\[\]\{\}\|\;\:\"\,\/\<\>\?\~\`\\]+', inputString))


## Function get_city(prompt, err) gets input from user for city they wish to search.
## Returns an error message if the input city name contains certain non-standard special characters.
def get_city(prompt, err):
    
    ## Initialize the boolean value for the loop. 
    good = False

    ## Start the while loop.
    while not good:

        ## Attempt to read the entered city name, and if successful, change the boolean value.
        try:
            
            ## Display the prompt passed to the function.
            city = input(prompt)

            ## If city name does not contain invalid special characters, change boolean to True.
            if not has_nums_specs(city):
                
                good = True
                
            else:
                
            ## If the input is not successful, display the error message.
                print(err)

        ## If the input is not successful, display the error message.
        except:
            
            print(err)

    ## When the loop ends, return the good city name to the calling statement.
    return city


## Function get_country_or_state(prompt, err) gets input from user for country or US State they wish to search.
## Returns an error message if the input country / state name contains certain non-standard special characters.
## Or if state name / abbrevation is not found in specified dictionary.
def get_country_or_state (prompt, err):
 
    ## Initialize the boolean value for the loop.
    good = False

    ## Start the while loop.
    while not good:

        ## Attempt to read the entered country/state name. If successful, change the boolean value.
        ## After success, check if entered location matches a US state name, or US state code.
        try:
            
            ## Display the prompt passed to the function.
            location = input(prompt)

            ## If location does not have invalid special characters, change boolean value to True.
            if not has_nums_specs(location):
                
                good = True

                ## Additionally, if location is also in the list of US State dictionary keys, then change location name to the corresponding value of key.
                if location in us_state_to_abbrev.keys():

                    location = us_state_to_abbrev.get(location)
                
                    good = True

                ## Or if location is in the list of US State dictionary values, then return location name.
                elif location in us_state_to_abbrev.values():

                    good = True

            else:
                
            ## If the input is not successful, display the error message.
                print(err)

        ## If the input is not successful, display the error message.
        except:
            
            print(err)

    ## When the loop ends, return the good species code to the calling statement.
    return location


## Function main() contains the main portion of the script.
def main():

    ## Prompt user for city and country/US State names.
    ## Display error message if input is not successful.
    cityInput = get_city("\n\nPlease enter the full name of the City you wish to search: ", "\nInvalid City Name - Entry Contains Numbers or Invalid Special Characters. Please try again.")

    countryInput = get_country_or_state("\nPlease enter the Country name or US State name/abbreviation where the City you wish to search for is located: ", "\nInvalid Country Name or Invalid US State Name/Abbreviation - Entry Contains Numbers or Invalid Special Characters. Please try again.")

    ## Display the user inputs. This helps the user check for spelling, capitalisation, or other errors if script does not work.
    print('\n\nENTRIES')

    print("*****************")

    print('\nYou entered {0} for the City Name.'.format(cityInput))

    print('You entered {0} for the Country/US State Name.'.format(countryInput))

    ## Replace whitespaces within city or country/US state names with a plus sign (+).
    cityInput = re.sub("(\s)", "+", cityInput)

    countryInput = re.sub("(\s)", "+", countryInput)

    ## Combine the inputted city and country/US state names into the search string.
    searchInput = cityInput + ',' + '+' + countryInput

    ## Set URL for website and append the search string to the URL.
    urlWebsite = "https://www.travelmath.com/cities/" + searchInput

    ## Inform user of search start and display start time of script after URL has been set.
    print('\n\nSEARCHING...')

    print("*****************")

    starttime = datetime.now()

    print("\nSearch Started At: %0.2d:%0.2d:%0.2d.\n" % (starttime.hour, starttime.minute, starttime.second))

    ## Connect and open URL.
    inspectSite = urllib.request.urlopen(urlWebsite)    

    ## Read the whole page and convert to UTF - 8 string formatting.
    webPageRead = inspectSite.read().decode('utf-8')

    ## Set the search patterns to be used in the regular expression.
    patternLong = "<strong>Longitude:</strong>" + "(.*)" + "</p>"

    patternLat = "<strong>Latitude:</strong>" + "(.*)" + "</p>"

    patternCity = "<title>" + "(.*)" + "</title>"

    patternCountry = "<strong>Country:</strong>" + "(.*)" + "</a>"

    patternState = "<strong>State:</strong>" + "(.*)" + "</a>"

    ## Use the search method from the "re" module to search out the pattern within
    ## the website via the variable that stores the webpage's content.
    ## If results are found, store the match objects in the below variables.
    matchTextLong = re.search(patternLong, webPageRead)

    matchTextLat = re.search(patternLat, webPageRead)

    matchTextCity = re.search(patternCity, webPageRead)

    matchTextCountry = re.search(patternCountry, webPageRead)

    matchTextState = re.search(patternState, webPageRead)

    ## If RegEx search was successful, extract the actual values from the match objects.
    if matchTextLong:

        ## Print finish time of search.
        endtime = datetime.now()
        print("Search Finished At: %0.2d:%0.2d:%0.2d.\n" % (endtime.hour, endtime.minute, endtime.second))

        ## Print messages for search success.
        print("Search...SUCCESSFUL!")

        ## Print result messages.
        print("\n\nRESULTS")

        print("*****************\n")

        ## Extract country and city values from match objects.
        countryVal = str(matchTextCountry.group(1)).split('>')[1]
        
        cityVal = str(matchTextCity.group(1)).split(',')[0]

        ## If country is the United States, then set the country value to the name of the state.
        ## Print formatted message displaying the location of the city, in its corresponding state, in the United States.
        if countryVal == 'United States':
            
            countryVal = str(matchTextState.group(1)).split('>')[1]
            
            print("{} is a city in the state of {} in the UNITED STATES OF AMERICA (USA).".format(cityVal.upper(), countryVal.upper()))

        ## For all other countries, print formatted message displaying the location of the city, in its corresponding country.
        else:
            
            print("{} is a city in the country of {}.".format(cityVal.upper(), countryVal.upper()))

        ## Extract longitude and latitude values from match objects.
        longVal = str(matchTextLong.group(1))
        
        latVal = str(matchTextLat.group(1))

        ## Print formatted messages displaying the longtitude and latitude of the city.
        ## Print formatted message displaying the longitude and latitude of the city, in its corresponding state, in the United States.
        if countryVal in us_state_to_abbrev.keys():
            
            print("The longtitude of {0}, {1}, USA is {2}.".format(cityVal.upper(), countryVal.upper(), longVal.strip()))

            print("The latitude of {0}, {1}, USA is {2}.".format(cityVal.upper(), countryVal.upper(), latVal.strip()))

        ## For all other countries, print formatted message displaying the longitude and latitude of the city, in its corresponding country.
        else:
            
            print("The longtitude of {0}, {1} is {2}.".format(cityVal.upper(), countryVal.upper(), longVal.strip()))

            print("The latitude of {0}, {1} is {2}.".format(cityVal.upper(), countryVal.upper(), latVal.strip()))

        ## Ask user if they wish to try again.
        again = input("\n\nEnter another City and Country/US State? (Y/N?): ")

        ## If not No, then run program again. Print message for program re-run.
        while again[0].upper() != "N":

            print("\n\nRestarting program...")
            
            main()
        
            if len(again) == 0:
                
                again = "Y"

        ## If No, then exit program.
        else:

                ## Print exit and goodbye messages. 
                print("\nExiting program... Thank you!")
                
                print("\n" + " ----- GOODBYE! :("*5, "-----\n")

                ## Force a good clean exit.
                sys.exit(0)

    ## If RegEx search was unsuccessful, then variables for match objects are empty.
    else:

        ## Print finish time of search.
        endtime = datetime.now()

        print("Search Finished At: %0.2d:%0.2d:%0.2d.\n" % (endtime.hour, endtime.minute, endtime.second))

        ## Print messages for search failure and possible reasons why script failed.
        print("Search...FAILED!\n")

        ## Print result messages.
        print("\nERROR")

        print("*****************\n")

        print("City and country/US state not found.\n")

        print('\nHINTS')

        print("*****************")

        print('\n1. Check if the entered city and country/US state names actually exist.')

        print('\n2. Check entered names for spelling or capitalisation errors, especially for country or US state names comprised of more than one word.\n   E.g. Ottawa is correct spelled and capitalised, not Otawa or ottawa; United Kingdom is correctly spelled and capitalised, not unted Kingdom.')

        print("\n3. Check if entered names contain hyphens, full stops/periods, or apostrophes.\n   E.g. Southend-on-Sea or St. John's are correct, but not Southend on Sea or St Johns.")

        print("\n4. Check entered names for leading/trailing whitespaces, hyphens, full stops/periods, or apostrophes.\n   E.g.  ..--Toronto''   is not a valid search term, but Toronto is a valid search term.")

        print('\n5. The entered city may not be located in the entered country.\n')


        ## Ask user if they wish to try again.
        again = input("\nWould you like to try again and enter another City and Country/US State? (Y/N?): ")     

        ## If not No, then run program again. Print message for program re-run.
        if again[0].upper() != "N":

            print("\n\nRestarting program...")
    
            main()
 
            if len(again) == 0:
                
                again = "Y"

        ## If No, then exit program.
        else:

            ## Print exit and goodbye messages.            
            print("\n\nExiting program... Thank you!")
            
            print("\n\n" + "----- GOODBYE! :("*5, "-----\n")

            ## Force a good clean exit.
            sys.exit(0)


## Call and run function main().
main()
