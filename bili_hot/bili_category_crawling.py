import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm.auto import tqdm

# 크롤링 전 세팅
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

chrome_options.add_argument("disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36")
# chrome_options.add_argument('headless')

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
# driver.maximize_window()

df = pd.read_csv("D:/OneDrive - 아도바/Project/bili_project/연결/owner_info.csv")
df.drop_duplicates(subset=['url'], keep='first', inplace=True)

owner_lst=[]
name_lst=[]
category_lst=[]

i = 0
for i in df.index:
    url_path = df['url'][i]
    owner_lst.append(df['owner_id'][i])
    
    wait = WebDriverWait(driver, 20)
    driver.get(url_path+"/video") # 영상 url
    time.sleep(3)

    # for item in tqdm(range(repeat)): # END버튼 반복 횟수, 1회당 20개씩 댓글 업데이트 
    #     wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
    #     time.sleep(1) # END버튼 클릭 이후, 1초 대기 후, 다시 END 버튼 진행

    # 데이터 가져오기    
    try:
        for name in tqdm(wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="h-name"]')))): # 댓글
            if name.text != '':
                name_temp = name.text.replace('\n', ' ')
                name_lst.append(name_temp)
            else:
                name_lst.append(' ')         
    except:
        # 크롤링 값이 없을 경우에
        name_lst.append('')
        
    # 데이터 가져오기    
    try:
        for category in tqdm(wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#submit-video-type-filter')))): # 댓글
            if category.text != '':
                category_temp = category.text.replace('\n', ' ')
                category_lst.append(category_temp)
            else:
                category_lst.append(' ')         
    except:
        # 크롤링 값이 없을 경우에
        category_lst.append('')

    i = i + 1
    print("총:", len(df.index))
    print(i , "크롤링 완료 !!!")
    
    

df = pd.DataFrame({'owner_id': owner_lst ,'name': name_lst, 'category': category_lst})
# to_csv 저장
filename = datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")
df.to_excel("category"+ " " + filename + ".xlsx")
print('save done')

