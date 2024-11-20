'''
--- Proof Of Concept Web scraper for imdb ---

Description: 
A tool that uses selenium to scrape any given imdb page for a link to its associated trailer.
Only use this tool to obtain a link once, then cache it. each link eventually expires. Using this tool
too much could potentially get you ip banned (from imdb).

Use case's: 
this tool could be setup in a container which takes requests and returns data to other containers.
'''

import timeit
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent

class ImdbScraper(): 

    def __init__(self, ID = "") -> None:

        ua = UserAgent() # obtains fake user agent data

        self.options = webdriver.ChromeOptions()
        self.options.add_argument(f'user-agent={ua.chrome}') # passes fake user agent info to get past 403
        self.options.add_argument('--headless')              # runs chrome without UI
        self.options.add_argument('--log-level=3')           # ignores SSL errors

        self.browser = webdriver.Chrome(self.options)      
        self.browser.get(f'https://www.imdb.com/title/{ID}/')
        # self.browser.get_screenshot_as_file("screenshot.png")
    
    def videoScraper(self):

        try:

            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "video")))  # 10 second timeout
            videoElement = self.browser.find_elements(By.TAG_NAME, 'video')[0]                             # locates video
            videoSrc = videoElement.get_attribute('src')                                                  

            return videoSrc
        
        except Exception:

            self.browser.quit()
            print("an error occured when scraping") 

        return None

if __name__ == '__main__':
    
    start = timeit.timeit()
    videoElement = ImdbScraper("tt0482571")
    end = timeit.timeit()

    print("\nTime to execute: ",end - start)
    print("\nVideo Element: ")
    print(videoElement.videoScraper())