from django.shortcuts import render
from votingapp.models import Songs
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from slackclient import SlackClient

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
SLACK_BOT_USER_TOKEN = getattr(settings,                          #2
'SLACK_BOT_USER_TOKEN', None)                                     #
Client = SlackClient(SLACK_BOT_USER_TOKEN)

def get_youtube_link(event_message):
    youtube_urls = []
    if 'message' in event_message:
        if 'attachments' in event_message['message']:
            attachments = event_message['message']['attachments']
            # Getting the youtube urls for the app
            for i in range(len(attachments)):
                if attachments[i]['service_name'] == 'YouTube':
                    urls = attachments[i]['from_url']
                    youtube_urls.extend(urls)
                    youtube_urls.extend("\n")
    return youtube_urls
            

class Events(APIView):
    def post(self, request, *args, **kwargs):
        if not request.data.get("event", {}).get("attachments"):
            slack_message = request.data

            if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
                return Response(status=status.HTTP_403_FORBIDDEN)

            # verification challenge
            if slack_message.get('type') == 'url_verification':
                return Response(data=slack_message,
                                status=status.HTTP_200_OK)
            
            if 'event' in slack_message:                              
                event_message = slack_message.get('event')            
                
                # ignore bot's own message
                if event_message.get('subtype') == 'bot_message':     
                    return Response(status=status.HTTP_200_OK)        
                
                # process user's message
                user = event_message.get('user')                                          
                channel = event_message.get('channel')   
                youtube_urls = []             
                bot_text = 'Hi :wave: Youtube links added to the jukebox playlist.'            #
                youtube_url = "".join(get_youtube_link(event_message))
                #splitting the multiple links into a list
                youtube_urls = youtube_url.split("\n") 
                for i in (range(len(youtube_urls))):
                    # To check the link is of youtube and to check if the youtube link exists in database
                    if "youtube.com" in youtube_urls[i] and not Songs.objects.filter(YoutubeLink=youtube_urls[i]).exists():
                        song = Songs(YoutubeLink=youtube_urls[i], SongName=str(youtube_urls[i]))
                        song.save()
                    if(i == len(youtube_urls)-1):
                        Client.api_call(method='chat.postMessage',       
                                channel=channel,                  
                                text=bot_text)                    
                        break                 
        return Response(status=status.HTTP_200_OK)