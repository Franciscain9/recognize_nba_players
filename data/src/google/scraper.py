from selenium import webdriver
from  google.cloud  import storage
import time
import os
from selenium.webdriver.common.keys import Keys
import time
import json
import gcsfs
import pandas as pd
import requests
import os
from PIL import Image
import io
import pandas as pd



class Google : 
    def __init__(self) : 
        

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        self.driver.set_window_size(1024, 768)

        self.storage_client = storage.Client.from_service_account_json('./credentials/dev-credentials.json', project='NBA Project')

    
    def set_player(self,search_query) : 

        
        self.search_query = search_query
        
        url = "https://www.google.com/search?q={0}&source=lnms&tbm=isch".format(search_query)
        print("*****Player to scrape*****")
        print('\n')
        print(search_query)
        
        self.driver.get(url)
        time.sleep(1)


        
    def scroll_all_pages(self) : 

        element = self.driver.find_element_by_tag_name("body")
        #correct before deployment
        for i in range(1):
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.1)
        
            try:
                self.driver.find_element_by_id("smb").click()
                for i in range(1):
                    element.send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.1)  # bot id protection
            except:
                for i in range(1):
                    element.send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.1)  # bot id protection
        
        print("Reached end of Page.")
        time.sleep(0.5)
            
        self.thumbnail_results = self.driver.find_elements_by_css_selector("img.Q4LuWd")
          
            
            
    def get_images_urls(self) :

        self.image_urls = set()
        error_clicks = results_start =  0
        #correct before deployment
        for img in self.thumbnail_results[0:10] : 
            
            print("Total Errors till now:", error_clicks)
            try:
                print('Trying to Click the Image')
                time.sleep(1)
                img.click()
                time.sleep(1)
                print('Image Click Successful!')
            except Exception:
                error_clicks = error_clicks + 1
                print('ERROR: Unable to Click the Image')
                
                    
            results_start = results_start + 1
            # extract image urls    
            print('Extracting of Image URLs')
            actual_images = self.driver.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    self.image_urls.add(actual_image.get_attribute('src'))
            
        number_results = len(self.image_urls)
        print('{0} images found'.format(number_results))
        
            
            
    def get_metadata(self) : 


        with open('./credentials/dev-credentials.json', 'rb') as f:
            file = json.load(f)

        fs = gcsfs.GCSFileSystem( project= file['project_id'], token='./credentials/dev-credentials.json')
        with fs.open('data-nba-scraping/metadata/players.csv') as f:
            df = pd.read_csv(f, index_col=False)

        return df
    
    def get_nb_image(self): 

        nb_image =0
        for blob in self.storage_client.list_blobs('data-nba-scraping'):
                if self.search_query.replace(' ', '').lower() in str(blob) : 
                    nb_image += 1
        
        return nb_image 


    def download_images_and_upload_bucket(self) : 


        history = self.get_metadata()

        urls_to_use =  self.image_urls - set(list(history[history.Player == self.search_query ]['urls']))
        
        player = self.search_query.replace(' ', '').lower()
        local_file = './images/{}/{}.jpg'.format(player,player)
        bucket = self.storage_client.get_bucket('data-nba-scraping')


        print("Number of images to download : {0}".format(len(urls_to_use)))
        count = 0
        nb_image = self.get_nb_image()
        for url in urls_to_use : 
            count += 1
            
            filename = player+str(nb_image+1)
            
            try:
                print('Start downloading image {0}'.format(count))
                image_content = requests.get(url).content
                print('Image downloaded')
            except Exception as e:
                print(f"ERROR - Could not download {url} - {e}")
                continue


            try:
                print('Start downloading image')
                folder_path = './images'
                image_file = io.BytesIO(image_content)
                image = Image.open(image_file).convert('RGB')
                folder_path = os.path.join(folder_path,player)
                if os.path.exists(folder_path):
                    file_path = os.path.join(folder_path,player + '.jpg')
                else:
                    os.mkdir(folder_path)
                    file_path = os.path.join(folder_path,player + '.jpg')
                with open(file_path, 'wb') as f:
                    image.save(f, "JPEG", quality=85)
                print(f"SUCCESS - saved {url} - as {file_path}")
            except Exception as e:
                print(f"ERROR - Could not save {url} - {e}")
                continue

                   
            try : 

                
                bucket_file = 'images/{}/{}.jpg'.format(player,filename)

                print('Start uploading image to the bucket')
                blob = bucket.blob(bucket_file)
                blob.content_type = 'image/jpeg'
                with open(local_file, 'rb') as f:
                    blob.upload_from_file(f)
                    print('Image Uploaded ')
                nb_image += 1
            except IndexError : 
                    print('Invalid file')

            
            try : 
                print('Deleting local file')
                os.remove(local_file)

            except FileNotFoundError: 
                print('File not found')   

            new_row = pd.Series(data={'Player':self.search_query, 'is_learned':1, 'urls':url}, name=history.shape[0])
            #append row to the dataframe
            history = history.append(new_row, ignore_index=False)

        

        history.loc[history.Player == self.search_query , 'is_learned'] = 1
        bucket.blob('metadata/players.csv').upload_from_string(history.to_csv(index=False), 'text/csv')


    def close_driver(self):
        self.driver.close()
