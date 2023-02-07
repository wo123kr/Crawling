import urllib.request
import json
import key_config
import pandas as pd
from datetime import datetime
import os

class naver_search :
    def __init__(self, client_id, client_secret) :
        self.client_id = client_id
        self.client_secret = client_secret

    #csv 저장날짜를 위한 함수
    def get_date(self):
        now = datetime.now()
        return now.strftime('%Y-%m-%d')
    
    def search(self, search_type, keyword, display, sort) :
        encText = urllib.parse.quote(keyword) 
        url = f"https://openapi.naver.com/v1/search/{search_type}?query={encText}&display={display}&sort={sort}"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id",self.client_id)
        request.add_header("X-Naver-Client-Secret",self.client_secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()

        if(rescode==200):
            response_body = response.read()
            print("api 호출 성공")
        else:
            print("Error Code:" + rescode)

        body = response_body.decode('utf-8') # 바이트 코드를 문자열로 변환한다.
        body = json.loads(body) # 문자열을 json 객체로 변환한다.
        return body
    
    # 엑셀 파일로 저장하는 함수
    # get_date() 함수를 이용해 excel 파일명에 날짜를 추가한다.
    # 만약 기존 파일이 존재한다면 파일명에 숫자를 추가한다. 1~9까지만 추가한다.
    # 파일명에 숫자를 추가하는 이유는 기존 파일을 덮어쓰는 것을 방지하기 위함이다.
    def save_excel(self, df, search_type):
        if os.path.isfile(f'{search_type}_{self.get_date()}.xlsx'):
            for i in range(1,10):
                if os.path.isfile(f'{search_type}_{self.get_date()}({i}).xlsx'):
                    continue
                else:
                    df.to_excel(f'{search_type}_{self.get_date()}({i}).xlsx')
                    break
        else:
            df.to_excel(f'{search_type}_{self.get_date()}.xlsx')
    
    def naver_blog(self, body):
        title = []
        link = []
        description = []
        bloggername = []
        bloggerlink = []
        postdate = []

        for i in range(0, len(body['items'])):
            title.append(body['items'][i]['title'])
            link.append(body['items'][i]['link'])
            description.append(body['items'][i]['description'])
            bloggername.append(body['items'][i]['bloggername'])
            bloggerlink.append(body['items'][i]['bloggerlink'])
            postdate.append(body['items'][i]['postdate'])
            
        #<b>,</b> 태그 제거 
        for i in range(len(title)):
            title[i] = title[i].replace('<b>','').replace('</b>','')
            description[i] = description[i].replace('<b>','').replace('</b>','')
        
        #데이터 프레임 만들기
        df = pd.DataFrame({'title':title,'link':link, 'description':description, 'bloggername':bloggername, 'bloggerlink':bloggerlink, 'postdate':postdate})
        self.save_excel(df, 'blog')

    def naver_news(self, body):
        title = []
        originallink = []
        link = []
        description = []
        pubdate = []

        for i in range(0, len(body['items'])):
            title.append(body['items'][i]['title'].replace('<b>','').replace('</b>',''))
            originallink.append(body['items'][i]['originallink'])
            link.append(body['items'][i]['link'])
            description.append(body['items'][i]['description'].replace('<b>','').replace('</b>',''))
            pubdate.append(body['items'][i]['pubDate'])
        
        #<b>,</b> 태그 제거 
        for i in range(len(title)):
            title[i] = title[i].replace('<b>','').replace('</b>','')
            description[i] = description[i].replace('<b>','').replace('</b>','')
        
        #데이터 프레임 만들기
        df = pd.DataFrame({'title':title, 'originallink':originallink, 'link':link, 'description':description, 'pubdate':pubdate})
        self.save_excel(df, 'news')
        
    def naver_image(self, body):
        title = []
        link = []
        thumbnail = []
        sizeheight = []
        sizewidth = []

        for i in range(0, len(body['items'])):
            title.append(body['items'][i]['title'])
            link.append(body['items'][i]['link'])
            thumbnail.append(body['items'][i]['thumbnail'])
            sizeheight.append(body['items'][i]['sizeheight'])
            sizewidth.append(body['items'][i]['sizewidth'])
        
        #데이터 프레임 만들기
        df = pd.DataFrame({'title':title, 'link':link, 'thumbnail':thumbnail, 'sizeheight':sizeheight, 'sizewidth':sizewidth})
        self.save_excel(df, 'image')

if __name__ == "__main__" :
    client_id = key_config.client_id
    client_secret = key_config.client_secret
    ns = naver_search(client_id, client_secret)
    
    search_dict = {"1":"blog", "2":"news", "3":"image"}
    sort_dic = {"1":"sim", "2":"date"}
    search_type = input("검색 타입을 입력하세요(1.블로그, 2.뉴스, 3.이미지) : ")
    keyword = input("검색어를 입력하세요 : ")
    display = input("검색 결과 출력 건수를 입력하세요(최대 100) : ")
    sort = input("정렬 방식을 입력하세요 (1. 유사도순, 2. 날짜순) : ")
    
    search_type = search_dict[search_type]
    sort = sort_dic[sort]
    
    body = ns.search(search_type, keyword, display, sort)
    
    if search_type == "blog":
        ns.naver_blog(body)
    elif search_type == "news":
        ns.naver_news(body)
    elif search_type == "image":
        ns.naver_image(body)
    else:
        print("잘못된 입력입니다.")