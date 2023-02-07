import sys
import urllib.request
import json
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import *
import re
import os
import key_config

class naver_search_app(QWidget): #Qwidget을 상속받는 클래스
    def __init__(self, client_id, client_secret) : #init 함수는 클래스가 생성될 때 자동으로 호출되는 함수
        self.client_id = client_id
        self.client_secret = client_secret
        super().__init__() #부모 클래스의 생성자를 호출한다. 
        self.initUI() #UI 초기화 함수 호출

    def initUI(self):
        self.setWindowTitle('네이버 검색 API')
        self.setGeometry(300, 300, 300, 200) #창 위치와 크기 설정 (x축 300, y축 300, 가로 300, 세로 200)
        self.setFixedSize(280, 220)
        
        #라벨 생성
        self.label1 = QLabel('키워드', self)
        self.label2 = QLabel('검색타입', self)
        self.label3 = QLabel('출력건수', self)
        self.label4 = QLabel('정렬', self)

        #라벨 위치
        self.label1.move(20, 20)
        self.label2.move(20, 60)
        self.label3.move(20, 100)
        self.label4.move(20, 140)

        #입력창 생성
        self.lineEdit1 = QLineEdit(self) #검색어
        self.lineEdit2 = QLineEdit(self) #검색타입
        # 입력창에 설명 넣기
        self.lineEdit2.setPlaceholderText(' 예 : 블로그, 뉴스, 이미지')
        #lineEdit2 가운데 정렬
        self.lineEdit3 = QLineEdit(self) #출력건수
        self.lineEdit3.setPlaceholderText(' 예 : 10, 100 (최대 100) ')
        self.lineEdit4 = QLineEdit(self) #정렬
        self.lineEdit4.setPlaceholderText(' 예 : 유사도순, 날짜순')

        #입력창 위치
        self.lineEdit1.move(80, 20)
        self.lineEdit2.move(80, 60)
        self.lineEdit3.move(80, 100)
        self.lineEdit4.move(80, 140)

        #버튼 생성
        self.btn1 = QPushButton('검색', self)
        self.btn1.move(60, 180) #버튼 위치 설정 (x축 200, y축 20)
        self.btn1.clicked.connect(self.btn1_clicked) #버튼 클릭시 btn1_clicked 함수 호출

        self.btn2 = QPushButton('종료', self)
        self.btn2.move(160, 180)
        self.btn2.clicked.connect(self.btn2_clicked)

        self.show()
     
     
    #input_text로 입력값을 받고 btn1_clicked을 눌렀을때 입력값에 오류가 없으면 search 함수를 호출한다.
    def input_text(self):
        #블로그 입력시 blog, 뉴스 입력시 news, 카페 입력시 cafearticle, 지식인 입력시 kin
        search_dic = {'블로그': 'blog', '뉴스': 'news', '이미지': 'image'}
        #유사도순 입력시 sim, 날짜순 입력시 date
        sort_dic = {'유사도순':'sim', '날짜순':'date'}
        keyword = self.lineEdit1.text()
        search_type = self.lineEdit2.text()
        search_type = search_dic[search_type]
        display = self.lineEdit3.text()
        sort = self.lineEdit4.text()
        sort = sort_dic[sort]
        
        #display에 머가 있든 숫자만 추출
        display = re.sub('[^0-9]', '', display)
        
        return search_type, keyword, display, sort
        
    def btn1_clicked(self):
        # 이 함수가 실행되면 input_text 함수를 실행하고 반환값을 받는다.
        # 오류가 있으면 오류창을 띄우고 return
        input_text = self.input_text()
        if input_text == None:
            return
        else:
            search_type, keyword, display, sort = input_text
            self.search(search_type, keyword, display, sort)
        
    def btn2_clicked(self):
        sys.exit(app.exec_())
    
    def search(self, search_type, keyword, display, sort) :
        encText = urllib.parse.quote(keyword) 
        url = f"https://openapi.naver.com/v1/search/{search_type}.json?query={encText}&display={display}&sort={sort}"
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

        body = response_body.decode('utf-8')
        body = json.loads(body) 
        
        if search_type == 'blog':
            #naver_blog 함수 호출
            self.naver_blog(body)
        elif search_type == 'news':
            self.naver_news(body)
        elif search_type == 'image':
            self.naver_image(body)
        
    
    def get_date(self):
        now = datetime.now()
        nowDate = now.strftime('%Y-%m-%d')
        return nowDate
    
    def remove_html_tag(self, text):
        cleanr = re.compile('<.*?>|<b>|</b>|&quot;|&lt;|&gt;|&amp;|&nbsp;|&apos;|')
        cleantext = re.sub(cleanr, '', text)
        return cleantext
    
    # 폴더가 있으면 폴더 생성 안함, 없으면 폴더 생성, 폴더 이름은 search_type
    def make_folder(self, search_type):
        if os.path.isdir(search_type): # 폴더가 있으면
            pass
        else:
            os.mkdir(search_type) # 폴더가 없으면 생성 
     
    def save_excel(self, df, search_type):
        self.make_folder(search_type)
        nowDate = self.get_date()
        # 동일한 이름의 파일이 있으면 파일명 뒤에 숫자 붙이기
        if os.path.isfile(f'{search_type}/{search_type}_{nowDate}.xlsx'):
            for i in range(1, 10):
                if os.path.isfile(f'{search_type}/{search_type}_{nowDate}_{i}.xlsx'):
                    pass
                else:
                    df.to_excel(f'{search_type}/{search_type}_{nowDate}_{i}.xlsx', index=False)
                    break
        else:
            df.to_excel(f'{search_type}/{search_type}_{nowDate}.xlsx', index=False)

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
            
        for i in range(len(title)):
            title[i] = self.remove_html_tag(title[i])
            description[i] = self.remove_html_tag(description[i])
            bloggername[i] = self.remove_html_tag(bloggername[i])
            bloggerlink[i] = self.remove_html_tag(bloggerlink[i])
            postdate[i] = self.remove_html_tag(postdate[i])

        #데이터 프레임 만들기
        df = pd.DataFrame({'title':title,'link':link, 'description':description, 'bloggerlink':bloggerlink, 'postdate':postdate})

        #get_date() 함수를 이용해서 현재 날짜를 파일명으로 저장
        self.save_excel(df, 'blog')
        self.popup()

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
        
        for i in range(len(title)):
            title[i] = self.remove_html_tag(title[i])
            originallink[i] = self.remove_html_tag(originallink[i])
            link[i] = self.remove_html_tag(link[i])
            description[i] = self.remove_html_tag(description[i])
            pubdate[i] = self.remove_html_tag(pubdate[i])
            
        #데이터 프레임 만들기
        df = pd.DataFrame({'title':title, 'originallink':originallink, 'link':link, 'description':description, 'pubdate':pubdate})
        #get_date() 함수를 이용해 excel 파일명에 날짜를 추가한다.
        self.save_excel(df, 'news')
        self.popup()
        
    def naver_image(self,body):
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
        
        for i in range(len(title)):
            title[i] = self.remove_html_tag(title[i])
            link[i] = self.remove_html_tag(link[i])
            thumbnail[i] = self.remove_html_tag(thumbnail[i])
            sizeheight[i] = self.remove_html_tag(sizeheight[i])
            sizewidth[i] = self.remove_html_tag(sizewidth[i])
        
        #데이터 프레임 만들기
        df = pd.DataFrame({'title':title, 'link':link, 'thumbnail':thumbnail, 'sizeheight':sizeheight, 'sizewidth':sizewidth})
        self.save_excel(df, 'image')
        self.popup()
        
    # 검색이 완료되면 알림팝업창을 띄워준다. 입력값에 따라 다른 알림창을 띄워준다. 
    # 입력값이 문제있으면 문제가 있는 부분을 알려주는 함수
    def popup(self):
        msg = QMessageBox()
        msg.setWindowTitle('알림')
        msg.setText('검색이 완료되었습니다.')
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

if __name__ == '__main__':
    client_id = key_config.client_id
    client_secret = key_config.client_secret
    app = QApplication(sys.argv)
    ex = naver_search_app(client_id, client_secret)
    sys.exit(app.exec_())