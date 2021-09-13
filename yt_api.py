import pandas as pd
import requests
import json
import googleapiclient.discovery


class yt_extract:

    def __init__(self,api_key,channel_id):
        self.channel_id=channel_id
        self.api_key=api_key
        self.channel_stats=None

    def get_data(self):
        url=f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id={self.channel_id}&key={self.api_key}'
        json_url= requests.get(url)
        data=json.loads(json_url.text)
        try:
            data=data["items"][0]["statistics"]
        except:
            data=None
        
        self.channel_stats=data
        return data
        

    def dump(self):
        if self.channel_stats is None:
            return
        
        channel_title="Crypto"
        channel_title.replace(" ","_").lower()
        file_name=channel_title+".json"
        with open(file_name,"w") as f:
            json.dump(self.channel_stats,f,indent=4)
        
        print("Success")
        



    def video_list(self, limit=None,start_date=None,end_date=None):
        url=f'https://www.googleapis.com/youtube/v3/search?channelId={self.channel_id}&key={self.api_key}&part=id,snippet&order=date&publishedAfter={start_date}T00%3A00%3A00Z&publishedBefore={end_date}T00%3A00%3A00Z'
        if limit is not None and start_date is not None and end_date is not None and isinstance(limit,int):
            url = url + "&maxResults=" + str(50)
            
            json_url=requests.get(url)
            data=json.loads(json_url.text)

            #get "totalResults" value
            #result_count=data["pageInfo"]["totalResults"]
            

            #extract "nextPageToken"
            next_token=data.get("nextPageToken",None)
            

            #copy data in variable
            items=data["items"]
            video_ids=[]
            description=[]
            title=[]
            publish_date=[]

            for item in items:
                try:
                    video_ids.append(item["id"]["videoId"])
                    description.append(item["snippet"]["description"])
                    title.append(item["snippet"]["title"])
                    publish_date.append(item["snippet"]["publishedAt"])
                except Exception:
                    pass
                    
            stp=2

            while next_token is not None and stp<=limit:
                url=url+"&page_token="+next_token

                json_url=requests.get(url)
                data=json.loads(json_url.text)
                next_token=data.get("nextPageToken",None)

                items=data["items"]
                
                stp=stp+1
                for item in items:
                    try:
                        video_ids.append(item["id"]["videoId"])
                        description.append(item["snippet"]["description"])
                        title.append(item["snippet"]["title"])
                        publish_date.append(item["snippet"]["publishedAt"])
                    except Exception:
                        pass
            

            data={}

            data['videoId']=video_ids
            data['publishedAt']=publish_date
            data['title']=title
            data['description']=description

            video_list=pd.DataFrame.from_dict(data)

            video_list.drop_duplicates()
            
        return video_list



    def video_data(self,video_key):
        
        stats=[]
        view=[]
        like=[]
        disl=[]
        fav=[]
        comm=[]
        vid_key=[]
        statistics={}
        
        
        for video_id in video_key:
            url=f'https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={self.api_key}'
            
            try:
                json_url=requests.get(url)
                data=json.loads(json_url.text)

                #snip=data["items"][0]["snippet"]
                
                stats=data["items"][0]["statistics"]
                vid_key.append(video_id)
                try:
                    view.append(stats['viewCount'])
                except:
                    view.append(0)
                    
                try:
                    like.append(stats['likeCount'])
                except:
                    like.append(0)

                try:
                    disl.append(stats['dislikeCount'])
                except:
                    disl.append(0)
                
                try:
                    fav.append(stats['favoriteCount'])
                except:
                    fav.append(0)

                try:
                    comm.append(stats['commentCount'])
                except:
                    comm.append(0)
            except Exception:
                
                pass
            
        statistics['Video_key']=vid_key
        statistics['ViewCount']=view
        statistics['likeCount']=like
        statistics['dislikeCount']=disl
        statistics['favoriteCount']=fav
        statistics['commentCount']=comm
        
        
        st=pd.DataFrame.from_dict(statistics)
        
        
            #content=data["items"][0]["contentDetails"]
            #print(content)
            
        return st


    def get_comments(self,video_key,max_comments):

        api_service_name = "youtube"
        api_version = "v3"
        DEVELOPER_KEY = self.api_key

        comment=[]
        name=[]
        id=[]
        auth_id=[]
        like=[]
        pub_date=[]
        reply_cnt=[]

        nexttoken=None

        youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

        request = youtube.commentThreads().list(
        part="snippet,replies",
        videoId=video_key
        )
        response = request.execute()

        cnt=response['pageInfo']['totalResults']

        for i in range(cnt):
            comment.append(response['items'][i]['snippet']['topLevelComment']['snippet']['textDisplay'])
            name.append(response['items'][i]['snippet']['topLevelComment']['snippet']['authorDisplayName'])
            try:
                auth_id.append(response['items'][i]['snippet']['topLevelComment']['snippet']['authorChannelId']['value'])
            except:
                auth_id.append("NA")
                
            id.append(response['items'][i]['id'])
            like.append(response['items'][i]['snippet']['topLevelComment']['snippet']['likeCount'])
            pub_date.append(response['items'][i]['snippet']['topLevelComment']['snippet']['publishedAt'])
            reply_cnt.append(response['items'][i]['snippet']['totalReplyCount'])
        try:
            nexttoken=response['nextPageToken']
        except:
            nexttoken=None

        stp=0

        while nexttoken is not None and stp<=max_comments:
            request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_key,
            pageToken=nexttoken
            )
            response = request.execute()

            cnt=response['pageInfo']['totalResults']

            try:
                nexttoken=response['nextPageToken']
            except:
                nexttoken=None

            for i in range(cnt):
                comment.append(response['items'][i]['snippet']['topLevelComment']['snippet']['textDisplay'])
                name.append(response['items'][i]['snippet']['topLevelComment']['snippet']['authorDisplayName'])
               
                try:
                    auth_id.append(response['items'][i]['snippet']['topLevelComment']['snippet']['authorChannelId']['value'])
                except:
                    auth_id.append("NA")
                id.append(response['items'][i]['id'])
                like.append(response['items'][i]['snippet']['topLevelComment']['snippet']['likeCount'])
                pub_date.append(response['items'][i]['snippet']['topLevelComment']['snippet']['publishedAt'])
                reply_cnt.append(response['items'][i]['snippet']['totalReplyCount'])
            stp=stp+1

        data={}

        data['id']=id
        data['auth_id']=auth_id
        data['name']=name
        data['comment']=comment
        data['like_count']=like
        data['reply_count']=reply_cnt
        data['published_date']=pub_date

        comments=pd.DataFrame.from_dict(data)
        
        return comments
