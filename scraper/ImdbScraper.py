'''
--- Proof Of Concept Web scraper for imdb ---

Description: 
A tool that uses requests to scrape any given imdb page for a link to its associated trailer.
Only use this tool to obtain a link once, then cache it. each link eventually expires. Using this tool
too much could potentially get you ip banned (from imdb).
'''

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
    
def videoScraper(ID):

    ua = UserAgent()

    headers = {'User-Agent': f'{ua.chrome}'}
    response = requests.get(f'https://www.imdb.com/title/{ID}/', headers=headers)

    if response.status_code == 200: 
    
        soup = BeautifulSoup(response.text, 'html.parser')

        JScript = str(soup.find(id='__NEXT_DATA__'))[4000:7000]

        videoElementPassOne = re.search(r"https:\/\/imdb-video\.media-imdb\.com[^\"]*", JScript) # obtains video using regular expression

        if videoElementPassOne == None: # for when no trailer exists
            print("no trailer exists")
            return "N/A"
        
        videoElementPassTwo = videoElementPassOne.group() 
        videoElementPassTwo = videoElementPassTwo.replace("\\u0026", "&")

        return videoElementPassTwo
    
    print("Bad Repsonse")
    return "N/A"

if __name__ == '__main__':
     
    print (videoScraper('tt0000009')) # replace with any movie id
    


