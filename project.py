
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    ElementClickInterceptedException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os
import requests
import re
import time
from bs4 import BeautifulSoup as bs
from datetime import datetime
# from webdriver_manager.chrome import ChromeDriverManager

# 建立 Service 物件，指定 chromedriver.exe 的路徑


# 設定 Chrome 瀏覽器的選項
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized") # Chrome 瀏覽器在啟動時最大化視窗
options.add_argument("--incognito") # 無痕模式
options.add_argument("--disable-popup-blocking") # 停用 Chrome 的彈窗阻擋功能。

# 建立 Chrome 瀏覽器物件
driver = webdriver.Chrome(options=options)
# driver.get("https://www.imdb.com/chart/top/?ref_=hm_nv_menu") #到首頁
wait = WebDriverWait(driver, 10)

movie_link = []
error_info=[]
all_movie_detail=[]
all_movie_review=[]







#抓取250筆首頁資料

def main():
    try:
        top_movie_url = "https://www.imdb.com/chart/top/"   
        search_top(top_movie_url)
    finally:
        driver.quit()


def loaddata():
    with open ('movedetail.json','r',encoding='utf-8') as f:
        data_detail=json.load(f)

    with open('movereview.json','w',encoding='utf-8')as h:
        data_review=json.load(r)

        
    return data_detail,data_review


def renewdata(topurl):
    global movie_link, error_info, all_movie_detail, all_movie_review
    # driver = webdriver.Chrome(options=options)
    driver.get(topurl) #到首頁
    search_all = driver.find_elements(By.CSS_SELECTOR,".ipc-metadata-list-summary-item")
    now_id = []
    for index,info in enumerate(search_all):
            try:
                info_name = info.find_element(By.CSS_SELECTOR,"h3").text
                info_link = info.find_element(By.CSS_SELECTOR,"a").get_attribute("href")
                info_id =  info_link.split("https://www.imdb.com/title/")[1].split("/")[0]
                sort = re.search(r"chttp_t_(\d+)",info_link)
                if sort:
                    info_sort = sort.group(1)
                else :
                    info_sort = None
            except (StaleElementReferenceException, NoSuchElementException) as e:
                    error_info.append({"爬取首頁錯誤":str(e),"網頁":driver.current_url,"筆數":index})
                    continue
                 
            now_id.append(info_id)
            movie_link.append({
                "id":info_id,
                "name": info_name,
                "link": info_link,
                "sort":info_sort
            })
    print("首頁抓取完畢!")

    data_detail, data_review = loaddata()
    old_id = []
    for i in data_detail:
        old_id.append(i['move_id'])

    new_id = []
    for i in now_id:
        if i not in old_id:
            new_id.append(i)

    for mid in new_id :
        for m in movie_link :
            if m['id'] == mid :
                detail = get_all_detail(m['link'])
                if detail is None:
                    continue
            data_detail.append(detail)
            review = get_all_review(m["id"])
            data_review.extend(review)
           
            

    

    with open('movedetail.json','w',encoding='utf-8')as f:
                json.dump(data_detail,f,indent=4,ensure_ascii=False)


    with open('homepage.json','w',encoding='utf-8')as f:
                json.dump(movie_link,f,indent=4,ensure_ascii=False)

    
    with open('movereview.json','w',encoding='utf-8')as f:
                json.dump(data_review,f,indent=4,ensure_ascii=False)


    with open('error.json','w',encoding='utf-8')as f:
            json.dump(error_info,f,indent=4,ensure_ascii=False)
        
    
    return movie_link




def search_top(topurl):
    global movie_link, error_info, all_movie_detail, all_movie_review
    # driver = webdriver.Chrome(options=options)
    driver.get(topurl) #到首頁
    search_all = driver.find_elements(By.CSS_SELECTOR,".ipc-metadata-list-summary-item")
    now_id = []
    for index,info in enumerate(search_all):
            try:
                info_name = info.find_element(By.CSS_SELECTOR,"h3").text
                info_link = info.find_element(By.CSS_SELECTOR,"a").get_attribute("href")
                info_id =  info_link.split("https://www.imdb.com/title/")[1].split("/")[0]
                sort = re.search(r"chttp_t_(\d+)",info_link)
                if sort:
                    info_sort = sort.group(1)
                else :
                    info_sort = None
            except (StaleElementReferenceException, NoSuchElementException) as e:
                    error_info.append({"爬取首頁錯誤":str(e),"網頁":driver.current_url,"筆數":index})
                    continue
                 
            now_id.append(info_id)
            movie_link.append({
                "id":info_id,
                "name": info_name,
                "link": info_link,
                "sort":info_sort
            })
    print("首頁抓取完畢!")
    


        
        

    for m in movie_link:
        detail=get_all_detail(m['link'])
        if detail is None:
            continue
        all_movie_detail.append(detail)
        review = get_all_review(m["id"])
        all_movie_review.extend(review)

    with open('movedetail.json','w',encoding='utf-8')as f:
                json.dump(all_movie_detail,f,indent=4,ensure_ascii=False)


    with open('homepage.json','w',encoding='utf-8')as f:
                json.dump(movie_link,f,indent=4,ensure_ascii=False)


    with open('movereview.json','w',encoding='utf-8')as f:
                json.dump(all_movie_review,f,indent=4,ensure_ascii=False)


    with open('error.json','w',encoding='utf-8')as f:
            json.dump(error_info,f,indent=4,ensure_ascii=False)
        
    
    return movie_link
    
        

def get_all_detail(url):
    driver.get(url)
    styles_list= []
    casts_list=[]
    directors = []
    writers = []
    year = level = length = None
    movie_path = None
    SCRAPE_TIME = datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        move_id = url.split("title/")[1].split("/")[0]
        move_ehname=driver.find_element(By.CSS_SELECTOR,".sc-b41e510f-2.jUfqFl.baseAlt").text
        move_rating=driver.find_element(By.CSS_SELECTOR,".sc-4dc495c1-1.lbQcRY").text
        move_ratingpeople=driver.find_element(By.CSS_SELECTOR,".sc-4dc495c1-3.eNfgcR").text
        move_img=driver.find_element(By.CSS_SELECTOR,".ipc-lockup-overlay.ipc-focusable.ipc-focusable--constrained").get_attribute("href")
        move_cast=driver.find_elements(By.CSS_SELECTOR,".sc-10bde568-5.dWhYSc .sc-10bde568-1.jBmamV")
        move_styles=driver.find_elements(By.CSS_SELECTOR,".ipc-chip-list__scroller span")
        crew_items = driver.find_elements(By.CSS_SELECTOR, "li[data-testid='title-pc-principal-credit']")
    
        for item in crew_items:
            try:
                label_elements = item.find_elements(By.CSS_SELECTOR, ".ipc-metadata-list-item__label")
                if not label_elements:
                    continue
                    
                label_text = label_elements[0].text.strip()
                
                name_links = item.find_elements(
                    By.CSS_SELECTOR, 
                    ".ipc-metadata-list-item__content-container a.ipc-metadata-list-item__list-content-item"
                )
                names = [link.text.strip() for link in name_links if link.text.strip()]
                
                if label_text == "Director":
                    directors = names
                elif label_text == "Writers":
                    writers = names
                elif label_text == "Stars":
                    stars = names
                    
            except Exception as e:
                print(f"Error extracting crew info for {label_text}: {e}")
                continue

    
    
    
    
    
    #     move_genre = wait.until(
    #     EC.presence_of_element_located(
    #         (By.CSS_SELECTOR, "[data-testid='storyline-genres'] a")
    #     )
    # ).text
        move_country=driver.find_element(By.CSS_SELECTOR,"[data-testid='title-details-origin'] a").text
        
    
        move_dec= driver.find_elements(By.CSS_SELECTOR,".sc-af040695-0.iOwuHP ul li")
        infos = [d.text for d in move_dec]

        if len(infos) >= 1:
            year = infos[0]
        if len(infos) >= 2:
            level = infos[1]
        if len(infos) >= 3:
            length  = infos[2]



        for styles in move_styles:
            styles_list.append(styles.text)


        for cast in move_cast:
            casts_list.append(cast.text)
        
        if move_img != None :
            movie_path=imgdownload(move_img,move_id)
        
        return {
         "move_id":move_id,
                    "ehname":move_ehname,
                    "rating":move_rating,
                    "ratingpeople":move_ratingpeople,
                    "move_img":move_img,
                    "styles":styles_list,
                    "move_casts":casts_list,
                    "move_country":move_country,
                    "year":year,
                    "level":level,
                    "length":length,
                    "moviepath":movie_path,
                    "directors":directors,
                    "writers":writers,
                    "scrapetime":SCRAPE_TIME}
    except (StaleElementReferenceException, NoSuchElementException) as e:
            error_info.append({"爬取內頁錯誤":str(e),"網頁":driver.current_url})
    
    
          

   

        
    



def get_all_review(id):
    

    driver.get(f'https://www.imdb.com/title/{id}/reviews/?sort=num_votes%2Cdesc&spoilers=EXCLUDE')
    try:
        # 等到這個按鈕「可被點擊」
        see_more_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ipc-see-more__text"))
        )

        # 捲到畫面中間，避免被 footer 或其他東西擋住
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", see_more_btn)
        time.sleep(1)

        see_more_btn.click()
        time.sleep(2)  # 等他把 25 筆新評論載進來

    except (TimeoutException, NoSuchElementException):
        # 找不到按鈕 / 超時：有些片本來就沒有「25 more」，沒關係，直接用現有評論
        error_info.append({
            "階段": "評論頁展開按鈕-找不到或超時",
            "錯誤訊息": "Timeout 或 NoSuchElementException",
            "網頁": driver.current_url,
            "movie_id": id,
        })
    except ElementClickInterceptedException as e:
        # 找到了但被擋住：一樣記錯誤，但不要讓程式死
        error_info.append({
            "階段": "評論頁展開按鈕-點擊被擋",
            "錯誤訊息": str(e),
            "網頁": driver.current_url,
            "movie_id": id,
        })
        # 不再 raise，直接用目前畫面上有的評論就好

    # 不管有沒有成功點「25 more」，到這裡都去抓評論
    move_review = driver.find_elements(By.CSS_SELECTOR,".sc-7ebcc14f-1.dtHbLR.user-review-item")
    review_info = []

    for review in move_review:
        try:
            review_rating = review.find_element(By.CSS_SELECTOR,".ipc-rating-star--rating").text
        except NoSuchElementException:
            review_rating = None
        try:
            review_title =  review.find_element(By.CSS_SELECTOR,".ipc-title__text.ipc-title__text--reduced").text
            review_content = review.find_element(By.CSS_SELECTOR,".ipc-html-content-inner-div").text
        except (StaleElementReferenceException, NoSuchElementException) as e:
            error_info.append({"爬取評論錯誤":str(e),"網頁":driver.current_url}) 
       
        review_info.append({
          "movie_id":id,
          "review_rating":review_rating,
                            "review_title":review_title,
                            "review_content":review_content})
    return review_info


    


def imgdownload(movie_img,move_id):


    folder_name = "projectimg"
    if not os.path.exists(folder_name):
        os.mkdir(folder_name,exist_ok=True)
    else:
        print("已建立過資料夾")


    # with open(f"{moviedata}.json",'r',encoding='utf-8') as f:
    # #     data=json.load(f)

    # move_data=[]
    # for index,url_element in enumerate(data):
    #     # print(sticker_element)
    #     # print(sticker_element["data-preview"])
    #     url_element = data[index]["move_img"]
    #     move_id = data[index]["move_id"]
    
    #     move_data.append({"url":url_element,
    #                     "id":move_id})
    #找到圖片





   


    # for index,movie in enumerate(move_data):
    driver.get(movie_img)
    real_url=driver.find_element(By.CSS_SELECTOR,".sc-b66608db-2.cEjYQy img").get_attribute('src')
    # r= requests.get(url)
    img_content = requests.get(real_url).content
    imgpath = f"{move_id}.jpg"
           
            
    with open(f"projectimg/{move_id}.jpg","wb") as f:
                    f.write(img_content)
    return imgpath
    # with open(f"{moviedata}.json","w",encoding="utf-8") as f:
    #                 json.dump(data,f,indent=4,ensure_ascii=False)




            


if __name__ == "__main__":
    main()




