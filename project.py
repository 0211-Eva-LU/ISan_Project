
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
# from webdriver_manager.chrome import ChromeDriverManager

# 建立 Service 物件，指定 chromedriver.exe 的路徑


# 設定 Chrome 瀏覽器的選項
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized") # Chrome 瀏覽器在啟動時最大化視窗
options.add_argument("--incognito") # 無痕模式
options.add_argument("--disable-popup-blocking") # 停用 Chrome 的彈窗阻擋功能。

# 建立 Chrome 瀏覽器物件
driver = webdriver.Chrome(options=options)
driver.get("https://www.imdb.com/chart/top/?ref_=hm_nv_menu") #到首頁
wait = WebDriverWait(driver, 10)






error_info = []
movie_link = []
all_movie_detail=[]
all_movie_review=[]


#抓取250筆首頁資料
search_all = driver.find_elements(By.CSS_SELECTOR,".ipc-metadata-list-summary-item")

for index,info in enumerate(search_all):
        try:
            info_name = info.find_element(By.CSS_SELECTOR,"h3").text
            info_link = info.find_element(By.CSS_SELECTOR,"a").get_attribute("href")
            dec_elems = info.find_elements(By.CSS_SELECTOR, ".sc-432a38ea-6.fhDXpP.cli-title-metadata span")  # 這個 selector 你換成你實際用的
            info_id =  info_link.split("https://www.imdb.com/title/")[1].split("/")[0]
            dec_list = []
            for dec in dec_elems:     # 這裡就會一個一個跑：這部電影的 dec1、dec2、dec3
                dec_list.append(dec.text)
        except (StaleElementReferenceException, NoSuchElementException) as e:
                error_info.append({"爬取首頁錯誤":str(e),"網頁":driver.current_url,"筆數":index})
                continue
        movie_link.append({
            "id":info_id,
            "name": info_name,
            "link": info_link,
            "dec":dec_list

        })
    
        

def get_all_detail(url):
    driver.get(url)
    styles_list= []
    casts_list=[]
    try:
        move_id = url.split("title/")[1].split("/")[0]
        move_zhname=driver.find_element(By.CSS_SELECTOR,".hero__primary-text").text
        move_ehname=driver.find_element(By.CSS_SELECTOR,".sc-b41e510f-2.jUfqFl.baseAlt").text
        move_rating=driver.find_element(By.CSS_SELECTOR,".sc-4dc495c1-1.lbQcRY").text
        move_ratingpeople=driver.find_element(By.CSS_SELECTOR,".sc-4dc495c1-3.eNfgcR").text
        move_img=driver.find_element(By.CSS_SELECTOR,".ipc-lockup-overlay.ipc-focusable.ipc-focusable--constrained").get_attribute("href")
        move_cast=driver.find_elements(By.CSS_SELECTOR,".sc-10bde568-5.dWhYSc .sc-10bde568-1.jBmamV")
        move_styles=driver.find_elements(By.CSS_SELECTOR,".ipc-chip-list__scroller span")
    #     move_genre = wait.until(
    #     EC.presence_of_element_located(
    #         (By.CSS_SELECTOR, "[data-testid='storyline-genres'] a")
    #     )
    # ).text
        move_country=driver.find_element(By.CSS_SELECTOR,"[data-testid='title-details-origin'] a").text
        
    

        for styles in move_styles:
            styles_list.append(styles.text)


        for cast in move_cast:
            casts_list.append(cast.text)
        
        return {
         "move_id":move_id,
         "zhname":move_zhname,
                    "ehname":move_ehname,
                    "rating":move_rating,
                    "ratingpeople":move_ratingpeople,
                    "move_img":move_img,
                    "styles":styles_list,
                    "move_casts":casts_list,
                    # "move_genre":move_genre,
                    "move_country":move_country,

                    }
    except (StaleElementReferenceException, NoSuchElementException) as e:
            error_info.append({"爬取內頁錯誤":str(e),"網頁":driver.current_url})
            return None
          

   

        
    



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

for m in movie_link:
    detail = get_all_detail(m['link'])
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