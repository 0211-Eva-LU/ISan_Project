from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import json
import os
import json
import requests
from time import sleep
from tqdm import tqdm
from datetime import datetime
import re



def download_image(img_url, save_path):
    img_data = requests.get(img_url).content
    with open(save_path, 'wb') as handler:
        handler.write(img_data)

def scrap_top_movies(driver,url):
    # driver = webdriver.Chrome()
    driver.get(url)
    
    wait = WebDriverWait(driver, 10)
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ipc-metadata-list-summary-item")))
    except Exception as e:
        print("Timeout waiting for movies to load: {e}")
        # driver.quit()
        # exit()
    # sleep(1)
    movies = driver.find_elements(By.CSS_SELECTOR, ".ipc-metadata-list-summary-item")
    # print(len(movies))

    os.makedirs("images", exist_ok=True)

    movie_data_list = []
    for idx, movie in enumerate(movies[:]):
        try:
            title = movie.find_element(By.CSS_SELECTOR, "h3").text
            movie_url = movie.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            movie_id = movie_url.split("/")[-2]
            # if movie_id in ["tt3170832", "tt0118715"]:
            movie_ranking =re.search(r"chttp_i_(\d+)",movie_url)
            if movie_ranking:
                movie_ranking = movie_ranking.group(1)
            else:
                movie_ranking = None
            movie_data_list.append({
                "id": movie_id,
                "title": title,
                "url": movie_url,
                "ranking":movie_ranking
            })
        except Exception as e:
            print(f"Error extracting basic info for movie #{idx}: {e}")
            continue

    movie_list = []
    print("Number of movies to process: ", len(movie_data_list))
    for idx, movie_data in tqdm(enumerate(movie_data_list), total=len(movie_data_list), desc="Processing movies"):
        try:
            movie_id = movie_data["id"]
            directors, writers, stars = scrap_movie_crew(driver, movie_id)
            year, level, length, rating = scrap_movie_base(driver, movie_id)
            save_path = scrap_movie_images(driver, movie_id)
            genres = scrap_movie_genres(driver, movie_id)
            storyline = scrap_movie_storyline(driver, movie_id)
            SCRAPE_TIME = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            movie_list.append({
                **movie_data,  
                "directors": directors,
                "writers": writers,
                "stars": stars,
                "year": year,
                "level": level,
                "length": length,
                "rating": rating,
                "img": save_path,
                "genres": genres if genres else [],
                "storyline":storyline,
                "SCRAPE_TIME":SCRAPE_TIME
            })
        except Exception as e:
            print(f"Error processing movie #{idx} ({movie_data.get('title', 'unknown')}): {e}")
            continue

    with open("imdb_top_movies.json", "w", encoding="utf-8") as f:
        json.dump(movie_list, f, indent=2, ensure_ascii=False)

    # driver.quit()
    print("All 250 movies saved & images downloaded!")

def scrap_reviews(driver, movie_id):
    
    url = f'https://www.imdb.com/title/{movie_id}/reviews/?sort=num_votes%2Cdesc&spoilers=EXCLUDE'
    driver.get(url)

    wait = WebDriverWait(driver, 10)
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,".sc-7ebcc14f-1")))
    except Exception as e:
        print("Timeout waiting for reviews on movie {movie_id}: {e}")
        # driver.quit()
        # exit()

    move_review = driver.find_elements(By.CSS_SELECTOR,".sc-7ebcc14f-1")
    review_info = []
    for i, review in enumerate(move_review):
        
        rating_el = review.find_elements(By.CSS_SELECTOR, ".ipc-rating-star--rating")
        if rating_el == []:
            review_rating = None
        else:
            review_rating = rating_el[0].text

        review_title =  review.find_element(By.CSS_SELECTOR,".ipc-title__text.ipc-title__text--reduced").text
        review_content = review.find_element(By.CSS_SELECTOR,".ipc-html-content-inner-div").text
        review_info.append({"review_rating": float(review_rating) if review_rating else None,
                            "review_title": review_title,
                            "review_content":review_content,
        })
    return review_info

def scrap_movie_images(driver, movie_id):
    url = f'https://www.imdb.com/title/{movie_id}/'
    driver.get(url)

    wait = WebDriverWait(driver, 10)
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/mediaviewer/rm']")))
    except Exception as e:
        print("Timeout waiting for reviews on movie {movie_id}: {e}")
        # driver.quit()
        # exit()

    media_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/mediaviewer/rm']")
    child_url = [ (a.get_attribute("href")) for a in media_links if (a.get_attribute("href").split("?")[1]) == "ref_=tt_ov_i"][0]
    driver.get(child_url)
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img")))
        image = driver.find_element(By.CSS_SELECTOR, "img")
        image_url = image.get_attribute("src")
        
        if image_url:
            download_image(image_url, f"images/{movie_id}.jpg")
            return f"images/{movie_id}.jpg"
        else:
            print(f"No image URL found for movie {movie_id}")
            return None
    except Exception as e:
        print(f"Error downloading image for movie {movie_id}: {e}")
        # driver.quit()
        # exit()
        # return None


def scrap_movie_genres(driver, movie_id):
    url = f'https://www.imdb.com/title/{movie_id}/'
    # print(f"URL: {url}")
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    try:
     
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ipc-chip-list__scroller")))
    except Exception as e:
        print(f"Timeout waiting for genres on movie {movie_id}: {e}")
        # driver.quit()
        # exit()
        # return []

    chip_texts = driver.find_elements(By.CSS_SELECTOR, ".ipc-chip-list__scroller a.ipc-chip.ipc-chip--on-baseAlt span.ipc-chip__text")
    style = [chip.text.strip() for chip in chip_texts]
    return style


def scrap_movie_base(driver, movie_id):
    url = f'https://www.imdb.com/title/{movie_id}/'
    driver.get(url)
    # sleep(1)
    wait = WebDriverWait(driver, 10)
    year = None
    level = None
    length = None
    rating = None
    

    try:
    
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sc-4dc495c1-0 .sc-4dc495c1-1.lbQcRY")))
        rating = driver.find_element(By.CSS_SELECTOR, ".sc-4dc495c1-0 .sc-4dc495c1-1.lbQcRY").text
    except Exception as e:
        print(f"Error extracting rating for movie {movie_id}: {e}")
        # driver.quit()
        # exit()
    
    try:
    
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sc-af040695-0.iOwuHP li.ipc-inline-list__item")))
        metadata_items = driver.find_elements(By.CSS_SELECTOR, ".sc-af040695-0.iOwuHP li.ipc-inline-list__item")
    except Exception as e:
        print(f"Error extracting metadata for movie {movie_id}: {e}")
        # driver.quit()
        # exit()
        # return year, level, length, rating
    
    for item in metadata_items:
        text = item.text.strip()
        
        try:
            link = item.find_element(By.CSS_SELECTOR, "a")
            href = link.get_attribute("href")
            
            if "releaseinfo" in href:
                year = text
                continue
    
            if "parentalguide" in href:
                level = text
                continue
                
        except:
            pass
        
        if "h" in text.lower() or ("m" in text.lower() and not text.replace("h", "").replace("m", "").replace(" ", "").isdigit()):
            length = text
            continue

    return year, level, length, rating

def scrap_movie_crew(driver, movie_id):
    url = f'https://www.imdb.com/title/{movie_id}/'
    driver.get(url)

    wait = WebDriverWait(driver, 10)

    directors = []
    writers = []
    stars = []

    try:
       
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-testid='title-pc-principal-credit']")))
        crew_items = driver.find_elements(By.CSS_SELECTOR, "li[data-testid='title-pc-principal-credit']")
    except Exception as e:
        print(f"Error waiting for crew info for movie {movie_id}: {e}")
        # driver.quit()
        # exit()
        # return directors, writers, stars
    # print(len(crew_items))
    
    for item in crew_items:
        try:
            label_elements = item.find_elements(By.CSS_SELECTOR, ".ipc-metadata-list-item__label")
            if not label_elements:
                continue
                
            label_text = label_elements[0].text.strip()
            # print(label_text)
            name_links = item.find_elements(
                By.CSS_SELECTOR, 
                ".ipc-metadata-list-item__content-container a.ipc-metadata-list-item__list-content-item"
            )
            names = [link.text.strip() for link in name_links if link.text.strip()]
            # print(names)
            
            if label_text in ["Director", "Directors"]:
                directors = names
            elif label_text in ["Writer", "Writers"]:
                writers = names
            elif label_text in ["Star", "Stars"]:
                stars = names
                
        except Exception as e:
            print(f"Error extracting crew info for {label_text}: {e}")
            continue

    return directors, writers, stars

def scrap_movie_storyline(driver, movie_id):
    url = f'https://www.imdb.com/title/{movie_id}/'
    driver.get(url)

    storyline = None
    import time
    
    try:
        time.sleep(2)
 
        max_scrolls = 100  # 最多滾動 10 次（避免無限循環）
        scroll_pause = 0.5  # 每次滾動後暫停時間
        
        storyline = None
        
        for i in range(max_scrolls):

            try:
                element = driver.find_element(
                    By.CSS_SELECTOR, 
                    "[data-testid='plot-xl']"
                )
                if element and element.text:
                    storyline = element.text
                    # print(f"✓ 在第 {i+1} 次滾動後找到元素！")
                    break
            except:
                pass
            
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(scroll_pause)
        
        if not storyline:
            raise Exception("找不到劇情元素")

        storyline = storyline.strip()
        # return storyline
        
    except Exception as e:
        print(f"❌ Error getting storyline for movie {movie_id}: {e}")
        # driver.quit()
        # exit()

    return storyline

def main():
    # 1. 先建立 options 並設定所有參數
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")        # Chrome 瀏覽器在啟動時最大化視窗
    options.add_argument("--incognito")              # 無痕模式
    options.add_argument("--disable-popup-blocking") # 停用彈窗阻擋
    options.add_argument("--lang=en-US")
    options.add_experimental_option(
        "prefs",
        {"intl.accept_languages": "en,en_US"}
    )

    # 2. 再用 options 建立 driver
    driver = webdriver.Chrome(options=options)

    try:
        top_movie_url = "https://www.imdb.com/chart/top/"
        scrap_top_movies(driver, top_movie_url)
    except Exception as e:
        print(f"Error scraping top movies: {e}")
    finally:
        driver.quit()
    # with open("imdb_top_movies.json", "r", encoding="utf-8") as f:
    #     movies_list = json.load(f)

    # movies_to_process = movies_list 
    # all_movies_reviews = {}

    # for idx, movie in enumerate(movies_to_process, 1):
    #     movie_id = movie["id"]
    #     movie_reviews = scrap_reviews(driver,movie_id)
        
    #     all_movies_reviews[movie_id] = {
    #         "movie_name": movie["title"],
    #         "movie_info": {
    #             "year": movie["year"],
    #             "length": movie["length"],
    #             "img": movie["img"],
    #             "level": movie["level"],
    #             "rating": movie["rating"],
    #             "url": movie["url"]
    #         },
    #         "review_count": len(movie_reviews),
    #         "reviews": movie_reviews
    #     }

    # with open("imdb_reviews.json", "w") as f:
    #     json.dump(all_movies_reviews, f, indent=2)


    # with open("imdb_top_movies.json", "r", encoding="utf-8") as f:
    #     movies_list = json.load(f)
    # print(len(movies_list))
    # with open("IMDB_reviews.json", "r", encoding="utf-8") as f:
    #     movies_list = json.load(f)
    # print(len(movies_list))

if __name__ == "__main__":
    main()