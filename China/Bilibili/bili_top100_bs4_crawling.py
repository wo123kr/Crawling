import re
import requests
from bs4 import BeautifulSoup

def getHTMLText(url, code="utf-8"):
    try:
        #设置http请求头
        Hostreferer = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
        }   
        r = requests.get(url, headers=Hostreferer)
        r.raise_for_status()
        r.encoding = code
        return r.text
    except:
        return "爬取出错！"
    
def parseText(text, movieInfo): #解析爬取的数据
    soup = BeautifulSoup(text,'html.parser')
    ul = soup.find('ul', class_='rank-list')
    details=ul.find_all('li')
    for detail in details:
        movieRank = detail.find('span').text
        movieName = detail.find('a', class_='title').text
        upName1 = detail.find('span', class_='data-box up-name').text
        upName2 = upName1.strip()
        #movieSeenNum1 = detail.find(text=re.compile('\d+万')).string
        movieSeenNum1 = detail.find(text=re.compile('\d+万+\s')).string
        movieSeenNum2 = movieSeenNum1.strip()

            
        url1 = detail.find('a', class_='title')
        url2 = url1.get('href')
        url3 = 'https:'+url2
        
        uptext = getHTMLText(url3)     
        upsoup=BeautifulSoup(uptext,'html.parser')
        like=upsoup.find('span',class_='like').text.strip()
        coin=upsoup.find('span',class_='coin').text.strip()
        collect=upsoup.find('span',class_='collect').text.strip()
        share=upsoup.find('span',class_='share').text.strip()
        
        movieInfo.append([movieRank,movieName,upName2,movieSeenNum2,like,coin,collect,share,url3])
    
    
def writeFile(fpath, movieInfo): #将爬取的数据写入文件
    with open(fpath, 'w', encoding='utf-8') as f:
        for info in movieInfo:
            f.write(','.join(info) + '\n')
    
if __name__ == '__main__':
    movieInfo = [['排名','标题','up主','播放量','点赞数','投币数','收藏人数','分享数','视频链接']]
    url = 'https://www.bilibili.com/v/popular/rank/all'
    text = getHTMLText(url)
    parseText(text, movieInfo)
    writeFile('movie_top100.csv', movieInfo)
    writeFile('movie_top100.excel', movieInfo)
    print('爬取完成！！')