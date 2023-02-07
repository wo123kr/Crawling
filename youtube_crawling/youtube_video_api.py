from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime
import datetime as dt
import key_config

class YoutubeVideoapi:
    def __init__(self):
        self.developer_key = key_config.DEVELOPER_KEY
        self.youtube_api_service_name = "youtube"
        self.youtube_api_version = 'v3'

    def videolist(self, keyword):
        youtube = build(self.youtube_api_service_name, self.youtube_api_version, developerKey=self.developer_key)

        search_response = youtube.search().list(
            q=keyword,
            order='viewCount',
            part='snippet',
            maxResults=50
        ).execute()
        # print(search_response)
        # 검색을 위한 videoID 추출
        video_ids = []
        for i in range(0, len(search_response['items'])):
            video_ids.append((search_response['items'][i]['id']['videoId']))

        search_date_list = []
        keyword_list = []
        channel_video_id = []
        channel_video_title = []
        channel_rating_view = []
        channel_rating_comments = []
        channel_rating_good = []
        channel_published_date = []
        data_dicts = {'검색날짜': [], '키워드': [], 'ID': [], '제목': [], '조회수': [], '댓글수': [], '좋아요수': [],
                 '게시일': []}
        # 영상이름, 조회수 , 좋아요수 등 정보 등 추출
        for k in range(0, len(search_response['items'])):
            video_ids_lists = youtube.videos().list(
                part='snippet, statistics',
                id=video_ids[k],
            ).execute()
            # print(video_ids_lists)

            # str_title = video_ids_lists['items'][0]['snippet'].get('channelTitle')

            str_video_id = video_ids_lists['items'][0]['id']
            str_video_title = video_ids_lists['items'][0]['snippet'].get('title')
            str_view_count = video_ids_lists['items'][0]['statistics'].get('viewCount')
            if str_view_count is None:
                str_view_count = "0"
            str_comment_count = video_ids_lists['items'][0]['statistics'].get('commentCount')
            if str_comment_count is None:
                str_comment_count = "0"
            str_like_count = video_ids_lists['items'][0]['statistics'].get('likeCount')
            if str_like_count is None:
                str_like_count = "0"
            str_published_date = str(video_ids_lists['items'][0]['snippet'].get('publishedAt'))
            #str_published_date # 2020-07-01T10:00:00Z -> '%Y-%m-%d %H:%M:%S'
            str_published_date = datetime.strptime(str_published_date, '%Y-%m-%dT%H:%M:%SZ')
            str_published_date = str_published_date.strftime('%Y-%m-%d %H:%M:%S')

            # 검색날짜 입력
            search_date_list.append(str(dt.date.today()))
            # 키워드 입력
            keyword_list.append(keyword)
            # 비디오 ID 입력
            channel_video_id.append(str_video_id)
            # 비디오 제목 입력
            channel_video_title.append(str_video_title)
            # 조회수 입력
            channel_rating_view.append(str_view_count)
            # 댓글수 입력
            channel_rating_comments.append(str_comment_count)
            # 좋아요 입력
            channel_rating_good.append(str_like_count)
            # 게시일 입력
            channel_published_date.append(str_published_date)

        data_dicts['검색날짜'] = search_date_list
        data_dicts['키워드'] = keyword_list
        data_dicts['비디오ID'] = channel_video_id
        data_dicts['제목'] = channel_video_title
        data_dicts['조회수'] = channel_rating_view
        data_dicts['댓글수'] = channel_rating_comments
        data_dicts['좋아요수'] = channel_rating_good
        data_dicts['게시일'] = channel_published_date
        
        print(data_dicts) # 딕셔너리 형태로 출력
        return data_dicts

    def save_csv(self, data_dicts):
        df = pd.DataFrame(data_dicts)
        df.to_csv('youtube_data.csv', encoding='utf-8-sig', index=False)


if __name__ == '__main__':
    youtube = YoutubeVideoapi()
    keyword = input('검색어를 입력하세요 : ')
    data_dicts = youtube.videolist(keyword)
    youtube.save_csv(data_dicts)


