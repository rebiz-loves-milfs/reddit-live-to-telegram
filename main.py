from pyrogram.types import InputMediaPhoto, InputMediaVideo
from pyrogram import Client
import praw
import os
from dotenv import load_dotenv
import tweepy
import prawcore
import wget
import time
import re
from datetime import datetime

import random
print ('imported')


load_dotenv()  
print("loaded to fire")
consumer_key = os.environ.get("TWITTER_CONSUMER_KEY")
consumer_secret = os.environ.get("TWITTER_CONSUMER_SECRET")
access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
res = random.randint(10000, 99999999999)
reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=res)
print ('made reddit client')
chat_id = int(os.environ.get("CHAT_ID"))
bot = Client(
    api_id=os.environ.get("API_ID"),
    api_hash=os.environ.get("HASH"),
    bot_token=os.environ.get("TOKEN"),
    name=":memory:",
)
print ('telegram client')



def listToString(s):
    str1 = " "
    return str1.join(s)

print ('ready to run')

pictures = []
videos = []
tosents = []
npictures = []
nvideos = []
downloads = []

def run():
    global pics, vids, tosents, npics, nvids
    print ('start')
    print("running")
    live_thread = reddit.live(os.environ.get("THREAD_ID"))
    try:
     for live_update in live_thread.stream.updates(skip_existing=True):
        bot.start()
        print(live_update.body)
        twims = ["https://twitter.com", "twitter.com", "http://twitter.com"]
        if any(twim in live_update.body for twim in twims):
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            live = live_update.body.split("/")[-1]
            temp = re.findall(r"\d+", live)
            #print(temp)
            temp = temp[:1]
            temp = listToString(temp)
            #print(temp)
            id = temp.replace(" ", "")
            #print(id)
            api = tweepy.API(auth)
            status = api.get_status(id, tweet_mode="extended")
            user_re = re.compile(r"@([A-Za-z0-9_]+)")
            tgml = user_re.sub(
                lambda m: '<a href="http://twitter.com/%s">%s</a>'
                % (m.group(1), m.group(0)),
                status.full_text,
            )
            #print(tgml)
            stat = api.get_status(id)
            print(stat.created_at)
            created = str(stat.created_at)
            created = time.strftime("%B %d,%Y %H:%M:%S")
            if (live_update.body).startswith(tuple(twims)):
                blog = ""
            else:
                blog = re.sub(r"https://twitter\S+", "", live_update.body)
                blog = re.sub(r"https://www.twitter\S+", "",blog)
                blog = re.sub(">", "", blog)
            caption = f"{blog}\n{tgml}\n\n⁡— __{status.author.name} (<a href=https://twitter.com/{status.author.screen_name}>@{status.author.screen_name}</a>), <a href=https://twitter.com/{status.author.screen_name}/status/{id}/>{created}</a>__"
            #print(status.entities)
            #print(status.full_text)
            if "media" in status.entities:
                if status.extended_entities["media"][0]["type"] == "video":
                    for video in status.extended_entities["media"]:
                        url = (video["media_url"])
                        print(video["type"])
                        print(video["video_info"]["variants"][0]["url"])
                        videos.append(video["video_info"]["variants"][0]["url"])
                        fvid = videos[0]                      
                    print(videos)
                    if len(videos) == 1:
                       pass
                    else:
                      videos.remove(videos[0])
                elif status.extended_entities["media"][0]["type"] == "photo":
                    for photo in status.extended_entities["media"]:
                        purl = (photo["media_url"])
                        print(photo["type"])
                        pictures.append(photo["media_url"])
                        fpic = pictures[0]                             
                    print(pictures)
                    if len(pictures) == 1:
                       pass
                    else:
                      pictures.remove(pictures[0])
                else:
                    try:
                        for photo in status.extended_entities["media"]:
                            print(photo["type"])
                            print("error")
                    except Exception as e:
                        print(e)
                        os._exit(1)
                print(pictures)
                if len(videos) == 0:
                        pass
                elif len(videos) == 1 and len(pictures) == 0:
                        r = listToString(videos)
                        print(r)
                        try:
                          bot.send_video(chat_id, r, caption=caption)       
                        except Exception as e:
                          print(e)
                          time.sleep(2)
                          file = wget.download(r)
                          bot.send_video(chat_id, file, caption=caption)  
                          try:
                            os.remove(file)
                          except:
                            pass     
                          
                else:
                        fdl = wget.download(fvid)
                        
                        nvideos.append(InputMediaVideo(fdl, caption=caption))
                        for video in videos:
                            file = wget.download(video)
                            time.sleep(2)
                            downloads.append(file)
                        for download in downloads:
                            r = InputMediaVideo(download)                           
                            nvideos.append(r)
                        for nvideo in nvideos:
                            tosents.append(nvideo)
                        print(tosents)
                        

                if len(pictures) == 0:
                        pass
                elif len(pictures) == 1 and len(videos) == 0:
                        r = listToString(npictures)
                        print(r)  
                        try: 
                          bot.send_photo(chat_id, purl, caption=caption)
                        except Exception as e:
                          print(e)      
                          file = wget.download(purl)
                          time.sleep(2)
                          bot.send_photo(chat_id, file, caption=caption) 
                          try:
                            os.remove(file)
                          except:
                            pass
                else:
                      fdlp = wget.download(fpic)
                      
                      npictures.append(InputMediaPhoto(fdlp, caption=caption))
                      for picture in pictures:
                          filepic = wget.download(picture)
                          time.sleep(2)
                          downloads.append(filepic)
                      for download in downloads:
                          r = InputMediaPhoto(download)                   
                          npictures.append(r)
                      for npicture in npictures:
                          tosents.append(npicture)
                      print(tosents)

                if len(tosents) == 0:
                     pass
                elif len(tosents) == 1:
                    print("got 1 to sent expected atleast 2")
                    print(tosents)
                else:
                    print(tosents)
                    bot.send_media_group(chat_id, media=tosents)
                try:
                  for download in downloads:
                    os.remove(download)
                  if os.path.isfile(fdlp):
                    os.remove(fdlp)
                  else:
                    pass
                  if os.path.isfile(fdl):              
                    os.remove(fdl)
                  else:
                    pass
         
                except Exception as e:
                   print(e)
                   pass
                
                pictures.clear()
                videos.clear()
                tosents.clear()
                npictures.clear()
                nvideos.clear()
                downloads.clear()
            else:
                print("false")
                print(live_update.author)
                print(live_update.body)
                bot.send_message(chat_id, caption, disable_web_page_preview=True)
        else:
            bot.send_message(chat_id, live_update.body, disable_web_page_preview=True)
        bot.stop()
    except prawcore.exceptions.ServerError as e:
        #wait for 30 seconds since sending more requests to overloaded server might not be helping
        time.sleep(60)
        print(e)
        run()
        


run()

