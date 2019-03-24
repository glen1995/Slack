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
            if attachments[0]['service_name'] == 'YouTube':
                urls = attachments[0]['from_url']
                youtube_urls.extend(urls)
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
            # greet bot
            if 'event' in slack_message:                              #4
                event_message = slack_message.get('event')            #
                
                # ignore bot's own message
                if event_message.get('subtype') == 'bot_message':     #5
                    return Response(status=status.HTTP_200_OK)        #
                
                # process user's message
                # print(event_message)
                user = event_message.get('user')                      #6
                # text = event_message.get('text')                      #
                channel = event_message.get('channel')                #
                bot_text = 'Hi :wave: Youtube links added to the jukebox playlist.'            #
                youtube_url = "".join(get_youtube_link(event_message))
                if "youtube.com" in youtube_url and not Songs.objects.filter(YoutubeLink=youtube_url).exists():
                    song = Songs(YoutubeLink=youtube_url, SongName=str(youtube_url))
                    song.save()
                    Client.api_call(method='chat.postMessage',        #8
                                    channel=channel,                  #
                                    text=bot_text)                    #
                    return Response(status=status.HTTP_200_OK)        #9

        return Response(status=status.HTTP_200_OK)