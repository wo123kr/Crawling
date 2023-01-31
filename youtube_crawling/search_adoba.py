# #이 코드들을 주피터 노트북에 넣어 필요한 라이브러리들을 설치한다
# !pip install gsprea
# !pip install --upgrade google-api-python-client
# !pip install oauth2client
from googleapiclient.discovery import build
import pandas as pd
import re
from tqdm import tqdm
from datetime import datetime
import key_config 

DEVELOPER_KEY = key_config.DEVELOPER_KEY
YOUTUBE_API_SERVICE_NAME='youtube'
YOUTUBE_API_VERSION='v3'

youtube=build(YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)

start_exe = input('시작하시겠습니까? (y/n) : ')

if start_exe == 'y' or start_exe == 'Y' :
    print('시작합니다.')

    #one_drive에 있는 엑셀 파일을 읽어와서 ['키워드'] 컬럼에 있는 키워드를 sheet_exclude 리스트에 넣는다
    sheet_X = []
    # 읽을 엑셀 파일이 없을경우 에러가 발생하므로 try except로 예외처리를 해준다
    try :
        onedrive = pd.read_csv('./유튜브검색리스트.csv')
        for i in onedrive['키워드'].unique():
            sheet_X.append(i)
    except: 
        print("유튜브검색리스트.csv 파일이 없습니다.")

    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    scope = ['https://spreadsheets.google.com/feeds']
    json_file_name = 'client_secret.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
    gc = gspread.authorize(credentials)
    
    # 문서 불러오기 
    doc = gc.open_by_url('https://docs.google.com/spreadsheets/d/1ZgUzmeAVE_ZOGD8YfyoV-SJ1sDNnR0K3VluWkSC3Zsk/')

    # 시트 목록 확인하기
    sheet_list = doc.worksheets()
    # 시트 선택하기
    sheet_select = [i.title for i in sheet_list]
    #sheet_select에서 sheet_exclude는 제외하고 sheet_select에 저장한다 
    sheet_select = [i for i in sheet_select if i not in sheet_X]
    #sheet_select에 검색은 제외 
    sheet_select = [i for i in sheet_select if i != '검색']

    youtube_search = pd.DataFrame(columns=['영상ID','영상제목','업로드날짜','썸네일이미지','조회수','좋아요','댓글수','영상바로가기링크','키워드'])

    # 시트별 데이터 가져와서 youtube_search에 append하기, 키워드에는 시트명을 넣는다
    for i in sheet_select:
        worksheet = doc.worksheet(i)
        df = pd.DataFrame(worksheet.get_all_records())
        df['키워드'] = i
        youtube_search = youtube_search.append(df)

    #youtube_search에 있는 영상ID를 video_list에 저장하기
    video_list = youtube_search['영상ID'].tolist()

    if len(video_list) == 0:
        print('영상ID가 없습니다.')
        
    else :
        print(str(len(video_list)) + '개의 영상ID를 가져왔습니다.')
        #채널 정보를 저장할 리스트 생성
        channel_info = []
        channel_id = []
        channel_title = []
        channel_description = []
        channel_customUrl = []
        channel_publishedAt = []
        channel_subscriberCount = []
        channel_viewCount = []
        channel_videoCount = []

        # 시트를 for 문을 돌면서 영상ID를 video_list에 저장하기
        print('영상ID를 읽어서 channelId는 가져오는 중입니다.')
        for video_id in tqdm(video_list):
            video_response = youtube.videos().list(
                part='snippet', #snippet은 영상의 정보를 가져오는 것
                id=video_id #id는 영상의 고유번호
                ).execute() #id는 영상의 고유번호
            
            #channelId가 없는 영상이 있는 경우 예외처리, 없는 경우 null값을 저장
            try: 
                channel_id.append(video_response['items'][0]['snippet']['channelId']) #channelId는 채널의 고유번호
            except: 
                channel_id.append('null')
                
        print('channelId를 읽어서 채널 정보를 가져오는 중입니다.')
        # channel_id에 저장된 channelId를 이용해서 channelTitle에 저장하기
        for channel in tqdm(channel_id):
            channel_response = youtube.channels().list(
                part='snippet',
                id=channel
                ).execute()
            try:
                channel_title.append(channel_response['items'][0]['snippet']['title'])
            except:
                channel_title.append('null')
            try:
                channel_description.append(channel_response['items'][0]['snippet']['description'])
            except:
                channel_description.append('null')
            try:
                channel_customUrl.append(channel_response['items'][0]['snippet']['customUrl'])
            except:
                channel_customUrl.append('null')
            try:
                channel_publishedAt.append(channel_response['items'][0]['snippet']['publishedAt'])
            except:
                channel_publishedAt.append('null')
            
        print('channelId를 읽어서 채널 통계를 가져오는 중입니다.')
        # channel_id에 저장된 channelId를 이용해서 구독자, 조회수, 영상수 가져오기
        for channel in tqdm(channel_id):
            channel_response = youtube.channels().list(
                part='statistics',
                id=channel
                ).execute()
            #구독자수가 없는 채널이 있는 경우 예외처리, 없는 경우 null값을 저장
            try:
                channel_subscriberCount.append(channel_response['items'][0]['statistics']['subscriberCount'])
            except:
                channel_subscriberCount.append('null')
                
            try:
                channel_viewCount.append(channel_response['items'][0]['statistics']['viewCount'])
            except:
                channel_viewCount.append('null')
            
            try: 
                channel_videoCount.append(channel_response['items'][0]['statistics']['videoCount'])
            except: 
                channel_videoCount.append('null')

        print('채널 정보를 읽어와 이메일 주소를 추출하는 중입니다.')
        #channel_description에 저장된 내용에 이메일 주소가 있으면, 이메일 주소를 추출해서 email_list에 저장하기 이메일이 없는 경우 null값을 저장
        email_list = []
        for description in tqdm(channel_description):
            email = re.findall(r'[\w\.-]+@[\w\.-]+', description)
            if email:
                email_list.append(email[0])
            else:
                email_list.append('null')

        print('채널 정보를 읽어와 url을 만드는 중입니다.')
        #channel_customUrl에 앞에 'https://www.youtube.com/' 를 붙여서 url_list에 저장하기, channel_customUrl 없는 경우 null값을 저장
        url_list = []
        for customUrl in tqdm(channel_customUrl):
            if customUrl:
                url_list.append('https://www.youtube.com/'+customUrl)
            else:
                url_list.append('null')    

        #publishedAt 형식을 yyyy-mm-dd로 변경하기
        publishedAt_list = []
        for publishedAt in channel_publishedAt:
            publishedAt_list.append(publishedAt[:10])

    today = datetime.today().strftime("%Y-%m-%d")

    # channel_info에 저장된 내용을 DataFrame으로 만들기
    channel_info = pd.DataFrame({'영상ID': video_list, '채널명':channel_title, '채널링크':url_list , 
                                '이메일':email_list, '누적구독자':channel_subscriberCount,'누적조회수':channel_viewCount, '누적영상수':channel_videoCount, 
                                '채널ID':channel_id, '채널커스텀ID':channel_customUrl, '채널소개':channel_description,  '채널개설일':publishedAt_list, '기준일': today})

    #youtube_search['영상ID'] 기준으로 channel_info 데이터를 합치기
    df3 = pd.merge(youtube_search, channel_info, on='영상ID', how='left')
    # onedrive를 읽어와서 해당 파일에 df3 데이터를 추가하기
    onedrive2 = pd.read_csv('./유튜브검색리스트.csv', encoding='utf-8-sig')
    onedrive2 = onedrive.append(df3)

    # onedrive에 저장하기
    onedrive2.to_csv('./유튜브검색리스트.csv', index=False, encoding='utf-8-sig')

    print('총 {}개의 데이터를 추가했습니다.'.format(len(df3)))
    print('수집이 완료되어 종료됩니다')

if start_exe == 'n' or start_exe == 'N':
    print('실행의사가 없으므로 종료됩니다')