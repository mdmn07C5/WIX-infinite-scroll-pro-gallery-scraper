import os
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep


def start_webdriver(url:str) -> webdriver:
    op = webdriver.FirefoxOptions()
    # do not open browser to air out dirty laundry
    op.add_argument('--headless')  
    # spoof agent to allow crawling on website
    op.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0)') 

    driver = webdriver.Firefox(options=op)
    driver.get(url)
    return driver
    

def scroll_to_bottom(driver: webdriver.Firefox) -> list:

    page_height = 0

    # scroll infinite scrolling webpage while there are elements to be loaded
    while True:
        # scroll only far enough for old elements to not be visible
        driver.execute_script(
            'window.scrollTo(0, window.pageYOffset + window.innerHeight);')

        print(f'scrolling... current height: {page_height}')
        
        

        # allow webpage to load a few, this also prevents us from scrolling again
        # and reaching the same height because nothing was loaded
        sleep(1.5)

        if page_height == (page_height := driver.execute_script('return window.pageYOffset;')):
            break
    
    return [
        t.find_element(By.TAG_NAME, 'img').get_attribute('src') for t in
        driver.find_elements(By.CLASS_NAME, 'gallery-item-content')
    ]

def write_to_disk(dir):
    if not os.path.exists(dir):
        os.makedirs(dir) 
    
    dir_contents = set(os.listdir(dir))

    def save(img_src):
        
        if (name := img_src.split('/')[-1]) in dir_contents:
            return
        
        with open(dir + name, 'wb') as f:

            response = requests.get(
                url=img_src[img_src.find('https'):img_src.find('v1')-1], 
                stream=True)
            
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)     

    return save 


if __name__=="__main__":
    import sys
    with start_webdriver(sys.argv[1]) as driver:
        t = scroll_to_bottom(driver)
        t.reverse()
        save = write_to_disk('./out/')
        for x in t:
            save(x)