import pickle
from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import HttpResponse,JsonResponse, HttpRequest
from django.core.serializers.json import DjangoJSONEncoder
# youtube imports
import pprint as pp
from googleapiclient.discovery import build

import json
from mediaApp.models import VideoFile


# creating a home view
def home(request):
    return render(request,'mediaApp/home.html',)

# Get Local Videos apis
def get_videos(query):
    try:
        data =list(VideoFile.objects.filter(title__icontains=query).values())  # wrap in list(), because QuerySet is not JSON serializable
        #return JsonResponse(data, safe=False)  # or JsonResponse({'data': data}
        for q in data:
            q['timestamp']=str(q['timestamp'])
            q['Video_file']=q['Video_file'][9:]
        return data
    except:
        data = json.dumps([{ 'Error': 'No video with that name'}])
        return data  # or JsonResponse({'data': data}

def youtube_query(request):
    query = request.POST['query']
    api_key = "AIzaSyC1VK59Wb3NW4nWo6m-lSmrCA-leTFfi0I"
    youtube = build('youtube', 'v3', developerKey=api_key)
    youtube_req = youtube.search().list(q=query, part='snippet', type='video', maxResults=5)
    response = youtube_req.execute()
    videos = []
    for id in range(5):
        videos.append({
                'video_id': response['items'][id]['id']['videoId'],
                'video_title': response['items'][id]['snippet']['title'],
                'thumbnail': response['items'][id]['snippet']['thumbnails']['default']['url'],
                'page_link': id,
        })
    # context = {'videoId' : "https://www.youtube.com/embed/" + str(videoId)}
    context = {
            'videos': videos,
            'show_more_link': "https://www.youtube.com/results?search_query="+query,
            'original_query': query,
    }
    
    context['api_response']=get_videos(query)
    request.session['context'] = context
    return render(request, 'mediaApp/home.html', context)
    #return JsonResponse(context)

def show_video(request, vid=None):
    vid = int(vid)
    context = request.session['context']
    context['current_video_id'] = "https://www.youtube.com/embed/" + context['videos'][vid]['video_id']
    return render(request, 'mediaApp/home.html', context)

def show_local_video(request, vid=None):
    context = request.session['context']
    context['current_api_video_id'] = vid
    return render(request, 'mediaApp/home.html', context)




