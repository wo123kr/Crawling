from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
from tqdm import tqdm 
import os
from urllib.request import Request, urlopen
from time import sleep

chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
driver_path = f'./{chrome_ver}/chromedriver.exe'
if os.path.exists(driver_path):
    print(f"chrom driver is insatlled: {driver_path}")
else:
    print(f"install the chrome driver(ver: {chrome_ver})")
    chromedriver_autoinstaller.install(True)
# '시스템에 부착된 장치가 작동하지 않습니다' 에러 방지
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(driver_path, options=options)

# 검색어 입력
keyword = '고양이'
# 몇개 다운로드 받을지
count = 3 
pages = 3 # 몇페이지까지 다운로드 받을지

sleep(5)
#image_xpath = "//*[@id="content"]/div/div[3]/div/div[3]/div[1]/div/div/div/a/img"

for j in tqdm(range(1, pages+1)):
    for i in range(1, count+1):
        url = f'https://pixabay.com/ko/images/search/{keyword}/?pagi={j}'
        driver.get(url=url)
        image_xpath = f'//*[@id="content"]/div/div[3]/div/div[3]/div[{i}]/div/div/div/a/img'
        image_url = driver.find_element(By.XPATH, image_xpath).get_attribute('src')
        print("image_url:", image_url)
        
        image_byte = Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
        f = open(f"./{keyword}_{j}페이지_{i}.jpg", 'wb')
        f.write(urlopen(image_byte).read())
        f. close()
        sleep(5)
    j += 1
    sleep(5)