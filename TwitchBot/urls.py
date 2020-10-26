"""TwitchBot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import urllib.request

import imageio
from PIL import Image
from django.urls import path
from imageio.plugins.ffmpeg import FNAME_PER_PLATFORM
from twitch import TwitchClient

from TwitchBot import views, main
from TwitchBot.InstagramAPI import InstagramAPI
from TwitchBot.twitterupload import *
from TwitchBot.util import AuthenticationError

urlpatterns = [
    path('', views.login),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('dashboard/remove', views.dashboard, name='delete_bot'),
    path('upcoming', views.upcoming, name='upcoming'),
    path('upcoming/edit', views.edit_upcoming, name='edit_post'),
    path('upcoming/remove', views.upcoming, name='delete_post'),
    path('bot/create', views.create_bot, name='create_bot'),
    path('bot/edit', views.edit_bot, name='edit_bot'),
    path('bot/edit/captions', views.dashboard, name='edit_bot_captions'),
    path('accounts', views.accounts, name='accounts'),
    path('accounts/edit', views.edit_account, name='edit_account'),
    path('accounts/remove', views.accounts, name='delete_account'),
    path('accounts/create', views.create_account, name='accounts_create'),

]

main.run()

# client = TwitchClient(client_id="eb7e5sgsbianyjnd1ry5r25twfxu18")
#
# results = client.clips.get_top(
#     limit=100,
#     language='es',
#     period='month'
# )
#
# clip_data = results[0]
# print(clip_data['language'])
# thumbnail_url = clip_data['thumbnails']['medium']
# download_url = thumbnail_url[0:thumbnail_url.index("-preview-")] + ".mp4"
# print("Downloading...")
# local_video_path = "tmp/" + download_url.split("/")[-1]
# local_thumbnail_path = "tmp/" + thumbnail_url.split("/")[-1]
# print(clip_data)
# print(download_url)
# urllib.request.urlretrieve(download_url, local_video_path)
# urllib.request.urlretrieve(thumbnail_url, local_thumbnail_path)
# image = Image.open(local_thumbnail_path)
# resized = image.resize((600, 400), Image.ANTIALIAS)
# resized.save(local_thumbnail_path)
# image.close()
# resized_video_path = local_video_path + "-resized.mp4"
# print(imageio.plugins.ffmpeg.get_platform())
# ffmpeg = FNAME_PER_PLATFORM[imageio.plugins.ffmpeg.get_platform()]
#
# os.system("cd ffmpeg && {ffmpeg} -i ../{source_video} -vf scale=1920:1080,setdar=13:9 ../{resized_video}"
#           .format(ffmpeg=ffmpeg,
#                   source_video=local_video_path,
#                   resized_video=resized_video_path))
#
# api = InstagramAPI(username="voidflamenet", password="supere$hew707106")
# if api.login():
#     time.sleep(3)
#     print("Uploading...")
#     api.uploadVideo(resized_video_path, local_thumbnail_path, caption="Test2")
#     time.sleep(2)
#     api.logout()
#     print("Finished Uploading")
#     time.sleep(2)
# else:
#     raise AuthenticationError("Failed to login to Instagram account!")
# print("Done!")

# print(len(results))
# for result in results:
#     if result['created_at'] < datetime.now():
#         print(type(result['created_at'])
#         print(type(result['created_at']))
# print(results)
# data = results[0]
# thumbnail_url = data['thumbnails']['medium']
# download_url = thumbnail_url[0:thumbnail_url.index("-preview-")] + ".mp4"
# print("Downloading...")
# local_video_path = "tmp/" + download_url.split("/")[-1]
# local_thumbnail_path = "tmp/" + thumbnail_url.split("/")[-1]
# request.urlretrieve(download_url, local_video_path)
# request.urlretrieve(thumbnail_url, local_thumbnail_path)
# print("Done!")
#
# image = Image.open(local_thumbnail_path)
# width, height = image.size
# image = image.resize((600, 400), Image.ANTIALIAS)
# image.save(local_thumbnail_path)
# image.save("test.jpg")
# image.close()
# print(results[0])
