from datetime import datetime
import json
import os
from seleniumbase import Driver
import time 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from constants import *
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Scrape() :
    def __init__(self) -> None:
        self.posts=set()
        self.catch=list()
        self.ignore=list()
        self.notsure=list()
        self.urls=set()
        self.driver=self.start_browser()
        self.login()
        for url in URLS :
            page=url.replace('https://www.facebook.com/','')
            date=f'{datetime.now():%y_%m_%d_%H_%M_%S}'
            self.get_posts(url)
            self.classify_posts()
            self.save(url,self.scrape_details(self.catch),self.scrape_details(self.ignore), self.scrape_details(self.notsure),f'{page}_{date}.json')
            self.save_trace(f'trace_{page}_{date}.json',url,self.urls)
            self.cleanup()
        
    def start_browser(self) :
        return Driver(headless=HEADLESS)
    
    def login(self) :
        self.driver.get('https://www.facebook.com')
        self.driver.find_element(By.ID, 'email').send_keys(EMAIL)
        self.driver.find_element(By.ID, 'pass').send_keys(PASSWORD)
        self.driver.find_element(By.NAME, 'login').click()
        time.sleep(2)

    def get_posts(self,url) :
        treated= self.check_trace(url)
        self.driver.get(url)
        time.sleep(3)
        start_time=time.time()
        while len(self.posts)<POSTS_NUMBER :
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            try :
                self.postList=self.driver.find_element(By.CSS_SELECTOR,'div[role="feed"]').find_elements(By.CSS_SELECTOR,'div[class="x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"]')
            except :
                self.postList=self.driver.find_element(By.CSS_SELECTOR,'div[data-pagelet="ProfileTimeline"]').find_elements(By.CSS_SELECTOR,'div[class="x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"]')
            #print(len(self.postList))
            for elem in self.postList : 
                try :
                    self.driver.execute_script("arguments[0].scrollIntoView();", elem)
                    time.sleep(2)
                    p_url=elem.find_element(By.CSS_SELECTOR,'a[class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv xo1l8bm"]').get_attribute('href').split('__cft__[0]=')[0]
                    #print(p_url)
                    if not self.check_post(p_url,treated) :
                        self.posts.add(elem)
                        self.urls.add(p_url)
                except :
                    pass
            #print(len(self.posts))
            if time.time()>=start_time+SCROLL_TIMEOUT :
                print('Scroll time exceeded')
                break 

    def scrape_content(self,post) :
        self.driver.execute_script("arguments[0].scrollIntoView();", post)
        try :  # checking for show original button
                post.find_element(By.XPATH,'//*[@id="mount_0_0_oZ"]/div/div[1]/div/div[3]/div/div/div[2]/div[1]/div/div[3]/div/div/div[4]/div/div/div[2]/div/div/div/div[2]/div[2]/div[10]/div/div/div/div/div/div/div/div/div/div[8]/div/div/div[3]/blockquote/span/div[2]/div/span/div[2]').click()
        except :
                pass 
        try : # checking for see more button
                post.find_element(By.CSS_SELECTOR,'div[class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xzsf02u x1s688f"]').click()
        except : 
                pass
        try :
                content=post.find_element(By.CSS_SELECTOR,'span[class="x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h"]').text
        except : 
                try :
                    content=post.find_element(By.CSS_SELECTOR,'div[class="x78zum5 xdt5ytf xz62fqu x16ldp7u"]').text
                except :
                    content=None
        return content

    def classify_posts(self) :
        self.posts=list(self.posts)[0:POSTS_NUMBER]
        for post in self.posts :
            content=self.scrape_content(post)
            if content :
                match_catch=[ x for x in CATCH if x.upper() in content.upper()] 
                match_ignore=[ x for x in IGNORE if x.upper() in content.upper()] 
                if any(match_catch) and any(match_ignore):
                    self.notsure.append({'catch' : match_catch ,
                                         'ignore' : match_ignore,
                                         'post' :post,
                                         })
                elif any(match_catch)  :
                    self.catch.append({ 'catch' : match_catch ,
                                         'post' :post,
                                         }
                                        )
                elif any(match_ignore)  :
                    self.ignore.append({
                                        'ignore' : match_ignore,
                                         'post' :post,
                                         
                                         })
        print(len(self.posts),len(self.catch),len(self.ignore),len(self.notsure))
            
    def scrape_details(self,plist) :
            data=[]
            for elem in plist :
                try :
                    content=self.scrape_content(elem['post'])
                    time.sleep(2)
                    author=self.wait_element(elem['post'],(By.TAG_NAME,'strong'),60).text
                    url=self.wait_element(elem['post'],(By.CSS_SELECTOR,'a[class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv xo1l8bm"]'),60).get_attribute('href').split('__cft__[0]=')[0]
                    date=self.wait_element(elem['post'],(By.CSS_SELECTOR,'a[class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv xo1l8bm"]'),60).text
                    reactions=[]
                    try : #checking for reactions tab
                        self.wait_element(elem['post'],(By.CSS_SELECTOR,'div[class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x1n2onr6 x87ps6o x1lku1pv x1a2a7pz x1heor9g xnl1qt8 x6ikm8r x10wlt62 x1vjfegm x1lliihq"]'),60).click()
                        time.sleep(5)
                        reacts=self.wait_element(self.driver,(By.CSS_SELECTOR,'div[class="x1jx94hy xh8yej3"]'),60)
                        divs=self.wait_elements(reacts,(By.TAG_NAME,'div'),60)
                        n_reactions=None
                        for div in divs :
                            try :
                                label= div.get_attribute('aria-label')
                                if 'All' in label :
                                    n_reactions =label.replace('All,','')
                                elif 'Like' in label :
                                    reactions.append(label)
                                elif 'Love' in label :
                                    reactions.append(label)
                                elif 'Haha' in label :
                                    reactions.append(label)
                                elif 'Sad' in label :
                                    reactions.append(label)
                                elif 'Angry' in label :
                                    reactions.append(label)
                                elif 'Wow' in label :
                                    reactions.append(label)
                            except : 
                                pass
                    except :
                        pass
                    finally : #Closing reactions tab
                        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                    s_comments=[]
                    try : #Scraping comments
                        n_comments=self.wait_element(elem['post'],(By.CSS_SELECTOR,'div[class="x1i10hfl x1qjc9v5 xjqpnuy xa49m3k xqeqjp1 x2hbi6w x1ypdohk xdl72j9 x2lah0s xe8uvvx x2lwn1j xeuugli x1hl2dhg xggy1nq x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x3nfvp2 x1q0g3np x87ps6o x1a2a7pz xjyslct xjbqb8w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1heor9g xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1ja2u2z xt0b8zv"]'),60).find_element(By.TAG_NAME,'span').text
                        self.wait_element(elem['post'],(By.CSS_SELECTOR,'div[class="x1i10hfl x1qjc9v5 xjqpnuy xa49m3k xqeqjp1 x2hbi6w x1ypdohk xdl72j9 x2lah0s xe8uvvx x2lwn1j xeuugli x1hl2dhg xggy1nq x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x3nfvp2 x1q0g3np x87ps6o x1a2a7pz xjyslct xjbqb8w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1heor9g xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1ja2u2z xt0b8zv"]'),60).click()
                        comments_section=self.wait_element(self.driver,(By.CSS_SELECTOR,'div[class="x6s0dn4 x78zum5 xdj266r x11i5rnm xat24cr x1mh8g0r xe0p6wg"]'),60)
                        #clicking 'All comments'
                        comments_section.find_element(By.CSS_SELECTOR,'div[class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x1n2onr6 x87ps6o x1lku1pv x1a2a7pz"]').click()
                        self.driver.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div[3]').click()
                        comments=self.wait_elements(self.driver,(By.CSS_SELECTOR,'div[class="x169t7cy x19f6ikt"]'),60)[0:COMMENTS_NUMBER]
                        for com in comments :
                            self.driver.execute_script("arguments[0].scrollIntoView();", com)
                            time.sleep(4)
                            comment=com.find_element(By.CSS_SELECTOR,'div[class="xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs"]').text.strip()
                            profile=com.find_element(By.CSS_SELECTOR,'a[class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv"]')
                            profile_url=profile.get_attribute('href')
                            profile_name=profile.text
                            date=com.find_element(By.CSS_SELECTOR,'a[class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa xo1l8bm"]').text
                            
                            s_comments.append({"date":date,
                                               "profile" : profile_name,
                                            "profile_url":profile_url,
                                            'comment':comment})                
                    except :
                        pass
                    finally :
                        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                    dic={    "matched" : {key: value for key, value in elem.items() if key != 'post' and key != 'content'},
                            "author":author,
                            "post_url":url,
                            'date':date,
                            'post':content,
                            'number of reactions':n_reactions,
                            'number of comments':n_comments,
                            'reactions':reactions,
                            'comments':s_comments

                        }
                    data.append(dic)
                except :
                    pass
            return data
    

    def cleanup(self) :
        self.posts.clear()
        self.catch.clear()
        self.ignore.clear()
        self.notsure.clear()
        self.urls.clear()
    
    def save(self,url,catch,ignore,notsure,file_name) :
        data={"url":url ,
              "catch":catch,
              "ignore":ignore,
              'notsure':notsure}
        with open(f'{os.getcwd()}/data/{file_name}', "w",encoding='utf-8') as outfile:
            json.dump(data, outfile,indent=4)
            
    def save_trace (self , file_name,url,posts) : 
        data={'url' : url,
              'date' : f"{datetime.now()}",
              'posts': list(posts) ,
              'catch' : CATCH ,
              'ignore' : IGNORE
              } 
        with open(f'{os.getcwd()}/traces/{file_name}', "w",encoding='utf-8') as outfile:
            json.dump(data, outfile,indent=4)


    def check_trace(self,url) :
        if CHECK_TRACE :
            treated_posts=[]
            page=url.replace('https://www.facebook.com/','')
            for file in os.listdir(f'{os.getcwd()}/traces') :
                if f"trace_{page}" in file :
                    print(f'Previous trace found : {file}')
                    with open(f'{os.getcwd()}/traces/{file}', 'r') as file:
                        data = json.load(file)
                    if USE_SAME_WORDS :
                        if data['catch']== CATCH and data['ignore']==IGNORE :
                            #print('Keywords match')
                            treated_posts.append(data['posts'])
                    else :
                        treated_posts.append(data['posts'])
            return treated_posts
        else :  
            return []
    
    def check_post(self,post,postlist) :
        for elem in postlist :
            if post in elem :
                #print(f'Treated post found : {post}')
                return True
        return False
    
    def wait_element(self,driver,elem,timeout) :  
        try:
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(elem))
        except : 
            pass
    def wait_elements(self,driver,elem,timeout) :  
        try:
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_all_elements_located(elem))
        except : 
            pass
        
if __name__ == "__main__":
    s=Scrape()
