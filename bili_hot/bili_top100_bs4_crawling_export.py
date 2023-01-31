import re
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

def getHTMLText(url, code="utf-8"):
    try:
        #http 요청 헤더 설정
        Hostreferer = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
        }   
        r = requests.get(url, headers=Hostreferer)
        r.raise_for_status()
        r.encoding = code
        return r.text
    except:
        return "크롤링 실패" 
    
def parseText(text, movieInfo): 
    soup = BeautifulSoup(text,'html.parser')
    ul = soup.find('ul', class_='rank-list')
    details=ul.find_all('li',class_='rank-item')
    for detail in tqdm(details):
        Rank = detail.find('span').text
        Name = detail.find('a', class_='title').text
        upName1 = detail.find('span', class_='data-box up-name').text
        upName2 = upName1.strip()
        view1 = detail.find(text=re.compile('\d+万+\s')).string 
        view2 = view1.strip() 

        url1 = detail.find('a', class_='title')
        url2 = url1.get('href')
        url3 = 'https:'+url2
        
        uptext = getHTMLText(url3)     
        upsoup=BeautifulSoup(uptext,'html.parser')
        
        top100_list.append([Rank,Name,upName2,view2,url3])
    
    
def writeFile(fpath, movieInfo): 
    with open(fpath, 'w', encoding='utf-8') as f:
        for info in movieInfo:
            f.write(','.join(info) + '\n')
    
if __name__ == '__main__':
    top100_list = [['排名','标题','up主','播放量','视频链接']]
    hot_tab = ['all','origin','rookie','bangumi']
    
    for i in hot_tab:
        print(f'현재 {i} 인기순위 수집중...')
        url = f'https://www.bilibili.com/v/popular/rank/{i}'
        text = getHTMLText(url)
        parseText(text, top100_list)
        writeFile(f'top100_{i}.csv', top100_list)
        writeFile(f'top100_{i}.excel', top100_list)
        print('크롤링 성공')
        