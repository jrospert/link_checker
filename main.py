import argparse
from bs4 import BeautifulSoup,SoupStrainer
import validators
import requests
from urllib.request import urlopen
from urllib.parse import urlparse
import sys
import re


def valid_args(arguments, *valid):
    args_provided = []
    for argument in arguments:
        if not argument[0] == "action" and not (
            argument[1] == None or argument[1] == False
        ):
            args_provided.append(argument[0])
    for arg_provided in args_provided:
        if not arg_provided in valid:
            return False
    return True

def isValidURLFormat(site):
    # validators is based on the regex-weburl.js by dperini
    # https://gist.github.com/dperini/729294
    if not validators.url(site):
        return False
    else:
        print(f'THE LINK: " {site} " is a valid URL')
        return True
    
def getResponseCode(url):
    response = requests.get(url, verify=False)
    return response.status_code
   
def isURLResponsive(site):
    response_code = getResponseCode(site)

    if response_code == 200:
        return True
    else:
        return False
    
def getBodyHTML(jsonDict):
    # Extract the values from a nested dictionary
    # Dict structure: {'data':{'attributes':{'body':{'value':body_text}}}}
    # Dict structure (human readable):
    # 'data':
    #   'attributes':
    #       'body':
    #           'value':           
    body_html = jsonDict['data']['attributes']['body']['value']
    return body_html

def getLinkList(html):
    # Parse through the body html
    soup = BeautifulSoup(html, 'html.parser')
    links_list = []
    # Traverse through the parsed soup object for all link (a href) tags
    # link is a BeautifulSoup Tag object
    for link in soup.find_all('a'):
        temp_link = link.attrs
        # Access the Tag obj, link, attrs
        # Get the link.attrs value (string) for href (much like getting value from json)
        # This will extract the URL as a string value
        link_str = link.attrs['href']
        # Add URL to the list of URLs
        links_list.append(link_str)
        #print(link_str)

    return links_list
    

def validate_hyperlinks(site):

    # This returns the json and all the links are in the body of json
    response = requests.get(site)
    json_dict = response.json()
    body = getBodyHTML(json_dict)
   
    hyperlink_list = getLinkList(body)
    for hyperlink in hyperlink_list:
        print(f'Checking {hyperlink} ...')
        if not isValidURLFormat(hyperlink):
            print(f'THE LINK: " {hyperlink} " is not a valid URL')
            continue
        else:
            if not isURLResponsive(hyperlink):
                print(f'THE LINK: " {hyperlink} " is UNREACHABLE')
                continue
            else:
                print(f'THE LINK: " {hyperlink} " is Ok')
   

def main(): 
        
    parser = argparse.ArgumentParser(description="Website URL Checker")
    parser.add_argument(
        "action",
        choices=[
            "check_urls"
        ],
    )
    parser.add_argument("--website", help="website to check URLs")
    args = parser.parse_args()
    arg_list = [(arg, getattr(args, arg)) for arg in vars(args)]

    if args.action == "check_urls":
        if not valid_args(arg_list, "website"):
            sys.exit("Invalid Option Provided for check_urls")
        if args.website:
            website = args.website
            print(f'website is: {website}')

            #Validate the regex of a URL
            if not isValidURLFormat(website):
                sys.exit("Invalid Website")
            else:
                pass
            
            if not isURLResponsive(website):
                sys.exit(f'Site is not responsive. Received error code: ')
            else:
                print(f'The url {website} is ok')
                foo = validate_hyperlinks(website)

        else:
            sys.exit("check_urls requires --website option")
    
if __name__ == "__main__":
    main()