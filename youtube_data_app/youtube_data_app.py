import pandas as pd
import re
from tqdm import tqdm
from datetime import datetime
import sys

# 구글 api를 사용하기 위한 모듈
from googleapiclient.discovery import build

#FutureWarning 무시
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# 유튜브 api를 활용한 데이터 수집 클래스
class YoutubeData():
    def __init__(self, developer_key):
        self.developer_key = developer_key
        self.youtube = build('youtube', 'v3', developerKey=developer_key)

    def read_file(self):
        
        # 파일을 읽어서 df에 저장한다.
        df = pd.read_excel('./링크데이터/url리스트.xlsx', engine='openpyxl') 
        return df
    
    #read_file 함수에서 return 된 df를 인자로 받는다.
    # get_channel_id 함수를 실행하고 df에 channel_id를 추가한다.
    def get_channel_id(self, df):
        import requests
        from bs4 import BeautifulSoup
        
        # df에 channel_id라는 컬럼을 추가한다.
        df['채널ID'] = ''
        
        for i in tqdm(range(len(df['url']))):
            # url에 'https://www.youtube.com/@~~~' 이런식으로 되어있거나 'https://www.youtube.com/c/' 이런식이면,  res=requests.get(df['url'][i])를 실행하고 soup=BeautifulSoup(res.content, 'html.parser')를 실행한다.
            # url에 'https://www.youtube.com/channel/~~~' 이런식으로 되어있는 경우 url에서 마지막 / 뒤의 값을 가져온다.
            # url이 null이거나 ''이면, df['channel_id'][i]에 null을 넣는다.
            if df['url'][i] == '' or df['url'][i] == None:
                df['채널ID'][i] = None
            elif 'https://www.youtube.com/@' in df['url'][i] or 'https://www.youtube.com/c/' in df['url'][i]:
                res = requests.get(df['url'][i])
                soup = BeautifulSoup(res.content, 'html.parser')
                df['채널ID'][i] = soup.find('meta', attrs={'name':'channelId'})['content'] # soup에서 meta 태그의 name이 channelId인 것을 찾아서 content를 가져온다.
            else:
                df['채널ID'][i] = df['url'][i].split('/')[-1] # url에서 마지막 / 뒤의 값을 가져온다.
        return df
    
    # get_channel_id 함수에서 return 된 df를 인자로 받는다.
    # get_channel_info 함수를 실행하고 
    def get_channel_info(self, youtube, df):
        
        # df에 '채널명', '채널소개', '커스텀ID', '채널개설일', '이메일' 컬럼을 추가한다.
        df['채널명'] = ''
        df['채널소개'] = ''
        df['커스텀ID'] = ''
        df['채널개설일'] = ''
        df['이메일'] = ''
         
        for i, channel in tqdm(enumerate(df['채널ID'])): # df['channel_id']의 값을 하나씩 가져온다. enumerate를 사용하면 i에는 index가, channel에는 df['channel_id']의 값이 들어간다.
            channel_response = youtube.channels().list(
                part='snippet', 
                id=channel
                ).execute()
            
        # channel_response['items'][0]['snippet']['title'])
        # channel_response['items'][0]['snippet']['description'])
        # channel_response['items'][0]['snippet']['customUrl'])
        # channel_response['items'][0]['snippet']['publishedAt'])
            df['채널명'][i] = channel_response['items'][0]['snippet']['title']
            df['채널소개'][i] = channel_response['items'][0]['snippet']['description']
            df['커스텀ID'][i] = channel_response['items'][0]['snippet']['customUrl']
            df['채널개설일'][i] = channel_response['items'][0]['snippet']['publishedAt']
        
        for i, description in tqdm(enumerate(df['채널소개'])):
            df['이메일'][i] = re.findall(r'[\w\.-]+@[\w\.-]+', description)
            
        #채널개설일 2007-10-17T12:33:01Z 형식에서 2007-10-17 형식으로 변경
        for i, date in tqdm(enumerate(df['채널개설일'])):
            df['채널개설일'][i] = date.split('T')[0]

        return df
    
    def get_channel_statistics(self, youtube, df):
        df['누적구독자'] = ''
        df['누적조회수'] = ''
        df['누적영상수'] = ''
        
        for i, channel in tqdm(enumerate(df['채널ID'])):
            channel_response = youtube.channels().list(
                part='statistics', 
                id=channel
                ).execute()
            
            df['누적구독자'][i] = channel_response['items'][0]['statistics']['subscriberCount']
            df['누적조회수'][i] = channel_response['items'][0]['statistics']['viewCount']
            df['누적영상수'][i] = channel_response['items'][0]['statistics']['videoCount']
            
        return df   
    
    def save_file(self, df):
        #오늘 날짜를 가져온다.
        today = datetime.now().strftime('%Y-%m-%d')
    
        #유튜브데이터추출기폴더 안에 추출데이터 경로로 df 데이터를 저장한다.
        df.to_excel(f'./추출데이터/{today}.xlsx', index=False)
        
        
    def main(self):
        # read_file 함수를 실행하고 df에 return 된 값을 넣는다.
        df = self.read_file()
        # get_channel_id 함수를 실행하고 df에 return 된 값을 넣는다.
        df = self.get_channel_id(df)
        # get_channel_info 함수를 실행하고 df에 return 된 값을 넣는다.
        df = self.get_channel_info(self.youtube, df)
        # get_channel_statistics 함수를 실행하고 df에 return 된 값을 넣는다.
        df = self.get_channel_statistics(self.youtube, df)
        # save_file 함수를 실행한다.
        self.save_file(df)

if __name__ == '__main__':
    #developer_key는 해당경로에 key_config.txt 파일을 읽어온다.
    developer_key = open("./key_config.txt").read()
    #경로에 key_config 파일이 없을 경우 안내 메시지를 출력하고 종료한다.
    if not developer_key:
        print("key_config.txt 파일이 없습니다. key_config.txt 파일을 생성하고 API 키를 입력해주세요.")
        sys.exit()
    # YoutubeData 클래스를 실행한다.
    YoutubeData(developer_key).main()



