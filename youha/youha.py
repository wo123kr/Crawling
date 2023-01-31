from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import re
import os
import random
import datetime
import time
import key_config

#youha 카테고리 리스트
"""
뷰티 · 패션 - beauty
먹방 - food
BJ · 엔터테이너 - bj
Vlog · 일상 - daily
게임 - game
IT · 전자기기 - it
음악 · 춤 - music
요리 · 베이킹 - cooking
여행 · 아웃도어 - travel
동물 · 펫 - animal
스포츠 · 건강 - sports
영화 · 애니 - movie
자동차 - car
키즈 · 플레이 - kids
교육 - education
부동산 · 투자 - stock
정치 · 시사 - politics 
그림 · 만들기 - painting
운세 · 타로 - fortune
기타 - etc
"""

# 로그인 정보
id = key_config.id
pw = key_config.pw

# 크롤링할 카테고리 리스트

#bj 78페이지 부터 해야함
#music 86페이지 부터 해야함
#cooking 8페이지 부터 해야함

category = ['travel','animal','sports',
            'movie','car','kids','education','stock','politics','painting','fortune','etc']
# category = ['beauty','food','bj','daily','game','it','music','cooking','travel','animal','sports',
#             'movie','car','kids','education','stock','politics','painting','fortune','etc']

# 크롤링 결과 저장할 리스트
cr_category = [] 
cr_name = [] 
cr_info = []
cr_youtube = []
cr_email = []
cr_fans = []
cr_views = []

cr1_category = []
cr1_name = []
cr1_info = []
cr1_youtube = []
cr1_email = []
cr1_fans = []
cr1_views = []

cr2_category = []
cr2_name = []
cr2_info = []
cr2_youtube = []
cr2_email = []
cr2_fans = []
cr2_views = []

# 크롬 드라이버 설치 및 버전 확인
# 체크 후 설치, 만약 설치되어 있으면 설치 안함
chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
driver_path = f'./{chrome_ver}/chromedriver.exe'
if os.path.exists(driver_path):
    print(f"chrom driver is insatlled: {driver_path}")
else:
    print(f"install the chrome driver(ver: {chrome_ver})")
    chromedriver_autoinstaller.install(True)

youha_url = 'https://www.youha.info/signin'

# '시스템에 부착된 장치가 작동하지 않습니다' 에러 방지
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')
options.add_argument('--no-sandbox') # 사이트 차단 방지
options.add_argument('--disable-gpu') # gpu 사용 안함
options.add_argument("--disable-dev-shm-usage") # 메모리 사용량 제한
options.add_argument('--window-size=1920,1080') # 창 크기
options.add_argument('--headless') # 창이 안뜨게 하는 옵션
options.add_argument('--disable-extensions') # 확장 프로그램 사용 안함
options.add_argument('--disable-blink-features=AutomationControlled') # 자동화 방지

# 구글 크롬 드라이버를 이용해 웹 브라우저를 실행
driver = webdriver.Chrome(driver_path , options=options)
driver.implicitly_wait(10) # 암묵적으로 웹 자원 로드를 위해 10초까지 기다려 줌
driver.get(url=youha_url)
#time.sleep(10)

def login(id, pw):

    driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(id)
    time.sleep(random.uniform(2, 4)) # 2~4초 사이의 랜덤한 시간을 지연
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(pw)
    time.sleep(random.uniform(2, 4)) # 2~4초 사이의 랜덤한 시간을 지연
    driver.find_element(By.XPATH, '/html/body/div[1]/main/div/div/div[2]/div/form/button').click()
    time.sleep(random.uniform(2, 4)) # 2~4초 사이의 랜덤한 시간을 지연

login(id, pw)
time.sleep(random.uniform(2, 4)) # 2~4초 사이의 랜덤한 시간을 지연

i = 0
j = 0

start = time.time()

try:
    for i in range(0, len(category)):  
        data_url = f'https://www.youha.info/search/influencers/youtube-channels?category={category[i]}&pageSize=100'  
        driver.get(url=data_url)
        time.sleep(10)
        
        # 페이지 수 구하기
        count_page = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/div/div[2]/div/div[2]/div[1]/p').text
        number = re.sub(r'[^0-9]', '', count_page)
        numbers = int(number)/100
        if int(numbers)%numbers == 0: 
            page = int(numbers) 
        else :
            page = int(numbers) + 1
        
        # 페이지 수 만큼 반복
        try:
            for j in tqdm(range(page)): # 페이지 수 만큼 반복
                print(f'{category[i]},{j+1}페이지 크롤링중..' )
                pageurl = f'https://www.youha.info/search/influencers/youtube-channels?category={category[i]}&pageSize=100&page={j+1}' 
                driver.get(url=pageurl)
                time.sleep(5)
                
                #셀레니움 스크롤 끝까지 내려도 계속 내리는 페이지라면
                prev_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    #첫번째로 스크롤 내리기
                    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                    #시간 지연
                    time.sleep(4)
                    #두번째로 현재 문서 높이를 가져와서 저장
                    curr_height = driver.execute_script("return document.body.scrollHeight")
                    #첫번째로 가져온 높이와 두번째로 가져온 높이가 같다면 스크롤이 끝까지 내려간 것
                    if curr_height == prev_height:
                        break
                    #두번째로 가져온 높이를 다시 prev_height에 저장
                    prev_height = curr_height
                time.sleep(random.uniform(3, 5))
                
                # 페이지 소스 가져오기
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                links = soup.find_all(class_= 'MuiDataGrid-row') # 링크 가져오기
                links = [l.find('a')['href'] for l in links] # 링크 리스트로 만들기
                link = [f'https://www.youha.info/{l}' for l in links] # 링크 앞에 도메인 붙이기
                link2 = pd.DataFrame(link) # 데이터프레임으로 만들기
                link2.to_csv(f'D:/workspace/웹 크롤링 프로젝트/youha_link/{category[i]},{j+1}_link.csv', index=False) # 
                
                try: 
                    for k in tqdm(link):
                        driver.get(url=k)
                        time.sleep(random.uniform(2, 4))
                        html = driver.page_source
                        soup = BeautifulSoup(html, 'html.parser') # 페이지 소스 가져오기
                        time.sleep(random.uniform(3, 5))
                        # 크리에이터 데이터 가져오기
                        # 크리에이터 이름
                        if soup.find(class_='MuiTypography-root MuiTypography-body1 mui-style-9dwvvc') == None:
                            continue
                        else : 
                            name = soup.find(class_='MuiTypography-root MuiTypography-body1 mui-style-9dwvvc')
                            name = name.get_text()
                            cr_name.append(name)
                            cr1_name.append(name)
                            cr2_name.append(name)
                        
                        # 채널 정보
                        info = soup.find('p', class_='MuiTypography-root MuiTypography-body1 mui-style-1kqhzus')
                        info = str(info).replace('<p class="MuiTypography-root MuiTypography-body1 mui-style-1kqhzus">', '')
                        info = str(info).replace('</p>', '')
                        cr_info.append(info)
                        cr1_info.append(info)
                        cr2_info.append(info)
                        
                        # 이메일주소
                        if '@' in info:
                            pattern = re.compile(r'[\w\.-]+@[\w\.-]+')
                            email = re.search(pattern, info)
                            if email:
                                email = email.group()
                                cr_email.append(email)
                                cr1_email.append(email)
                                cr2_email.append(email)
                            else :
                                cr_email.append(email) 
                                cr1_email.append(email)
                                cr2_email.append(email)    
                        else :
                            email = '없음'
                            cr_email.append(email)
                            cr1_email.append(email)
                            cr2_email.append(email)
                        
                        # 카테고리
                        cate = soup.find(class_='MuiTypography-root MuiTypography-body1 mui-style-5myc3h')
                        cate = cate.get_text()
                        cr_category.append(cate)
                        cr1_category.append(cate)
                        cr2_category.append(cate)
                        
                        # 유튜브 링크
                        youtube = soup.select('#__next > main > div > div > div.MuiBox-root.mui-style-k008qs > div.MuiBox-root.mui-style-1rr4qq7 > div.MuiBox-root.mui-style-1rovmif > div.MuiBox-root.mui-style-1eziwv > div.MuiBox-root.mui-style-j7ig5e > a:nth-child(2)')
                        youtube = youtube[0].get('href')
                        cr_youtube.append(youtube)
                        cr1_youtube.append(youtube)
                        cr2_youtube.append(youtube)
                        
                        # 구독자수
                        fans = soup.find('p', class_='MuiTypography-root MuiTypography-body1 mui-style-1jrf6vj')
                        fans = str(fans).replace('<p class="MuiTypography-root MuiTypography-body1 mui-style-1jrf6vj">', '')
                        fans = str(fans).replace('</p>', '')
                        fans = re.sub(r'[^0-9]', '', fans)
                        cr_fans.append(fans)
                        cr1_fans.append(fans)
                        cr2_fans.append(fans)
                        
                        # 조회수
                        views = soup.find('div', class_='MuiTypography-root MuiTypography-body1 mui-style-1jrf6vj')
                        views = str(views).replace('<div class="MuiTypography-root MuiTypography-body1 mui-style-1jrf6vj">', '')
                        views = str(views).replace('</div>', '')
                        views = re.sub(r'[^0-9]', '', views)
                        cr_views.append(views)
                        cr1_views.append(views)
                        cr2_views.append(views)
                        
                        df2 = pd.DataFrame({'name':cr2_name, 'info':cr2_info, 'email':cr2_email, 'category':cr2_category, 'youtube':cr2_youtube, 'fans':cr2_fans, 'views':cr2_views})
                        if not os.path.exists(f'{category[i]}_크리에이터_데이터.csv'): # 파일이 없으면
                            df2.to_csv(f'{category[i]}_크리에이터_데이터.csv', encoding='utf-8-sig', index=False, mode = 'w') # 파일 생성
                            cr2_category = []
                            cr2_name = []
                            cr2_info = []
                            cr2_youtube = []
                            cr2_email = []
                            cr2_fans = []
                            cr2_views = []
                        else :
                            df2.to_csv(f'{category[i]}_크리에이터_데이터.csv', encoding='utf-8-sig', index=False, mode = 'a', header=False) # 파일 추가
                            cr2_category = []
                            cr2_name = []
                            cr2_info = []
                            cr2_youtube = []
                            cr2_email = []
                            cr2_fans = []
                            cr2_views = []
                
                except:
                    print('1 오류')
                    pass
                    
            # 데이터프레임으로 만들기
            df1 = pd.DataFrame({'name':cr1_name, 'info':cr1_info, 'email':cr1_email, 'category':cr1_category, 'youtube':cr1_youtube, 'fans':cr1_fans, 'views':cr1_views})
            df1.to_csv(f'{category[i]}_크리에이터_데이터[1].csv', encoding='utf-8-sig', index=False)
            print(f'{category[i]} 크리에이터 데이터 수집완료[1]')
            i = i + 1
        
        except:
            print('2 오류')
            pass    
        
        # 크리에이터 데이터 초기화
        cr1_category = []
        cr1_name = []
        cr1_info = []
        cr1_youtube = []
        cr1_email = []
        cr1_fans = []
        cr1_views = []     
          
except: 
    print('3 오류')
    pass
   
count = str(len(cr_name))
sec = time.time()-start
times = str(datetime.timedelta(seconds=sec)).split(".")
times = times[0]

print(count + '개의 크리에이터 데이터 수집완료')
print(times)
df = pd.DataFrame({'name':cr_name, 'info':cr_info, 'email':cr_email, 'category':cr_category, 'youtube':cr_youtube, 'fans':cr_fans, 'views':cr_views})
df.to_csv('[전체완료]_크리에이터_데이터.csv', encoding='utf-8-sig', index=False) # utf-8-sig : 한글깨짐 방지 
