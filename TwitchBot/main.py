import json
import os
import random
import shutil
import sys
import threading
import time
import traceback
import urllib.request

import imageio
import pytz
from PIL import Image
from django.contrib.auth.models import User
from imageio.plugins.ffmpeg import FNAME_PER_PLATFORM
from twitch import TwitchClient

from TwitchBot import util, twitterupload, settings
from TwitchBot.InstagramAPI import InstagramAPI
from TwitchBot.models import TwitchBot, Post, SocialMediaAccount
from TwitchBot.util import AuthenticationError

TWITTER = 1
INSTAGRAM = 2

account_types = {TWITTER: "Twitter", INSTAGRAM: "Instagram"}

languages = {
    "All": "",
    "English": "en",
    "Spanish": "es",
    "Portuguese": "pt",
    "French": "fr",
    "Russian": "ru",
    "Chinese": "zh",
    "Czech": "cs",
    "Danish": "da",
    "Dutch": "nl",
    "Finnish": "fi",
    "German": "de",
    "Hungarian": "hu",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Norwegian": "no",
    "Polish": "pl",
    "Slovak": "sk",
    "Swedish": "sv",
    "Turkish": "tr",
}

twitch_client_id = ""
games = {}
ffmpeg = FNAME_PER_PLATFORM[imageio.plugins.ffmpeg.get_platform()]


def run():
    global twitch_client_id
    User.objects.all().delete()

    with open("config/config.json") as file:
        data = json.load(file)
        twitch_client_id = data['twitch-client-id']
        util.timezone = pytz.timezone(data['timezone'])

        user = data['login']
        User.objects.create_user(username=user['username'],
                                 email='',
                                 password=user['password'])
    util.validate()
    imageio.plugins.ffmpeg.download(directory=settings.BASE_DIR)

    # Redirect STD out
    if not settings.DEBUG:
        debug = open('debug.log', 'a')
        sys.stdout = debug
        sys.stderr = debug

    # Reset tmp directory
    if os.path.exists("tmp"):
        shutil.rmtree("tmp")
    os.makedirs("tmp")

    # Remove any outdated posts that weren't posted for some reason
    current_day = util.get_current_time().day
    for queued_post in Post.objects.filter(posted=False):
        if queued_post.queued_time.day != current_day:
            queued_post.delete()

    th = threading.Thread(target=timer)
    th.daemon = True
    th.start()


def timer():
    # last_time = datetime.min
    last_time = util.get_current_time()
    while True:
        time.sleep(0.5)
        now = util.get_current_time()
        if last_time.minute != now.minute:
            minute = (60 * now.hour) + now.minute
            new_day = now.day != last_time.day
            last_time = now
            minutely(minute, new_day)


def minutely(minute, new_day):
    if minute % 10 == 0:
        # Update stats every 10 minutes
        print("Updating statistics!")
        for account in SocialMediaAccount.objects.all():
            try:
                util.update_stats(account)
                account.save()
            except AuthenticationError:
                traceback.print_exc()
                log_message("Failed to update stats for " + account.username + " (" + account.get_type_name() + ")")
        print("Done!")
    if new_day:
        generate_queue(minute)
    process_queue(minute)


def generate_queue(minute):
    Post.objects.filter(posted=False).delete()
    print("Generating Queue...")
    client = TwitchClient(client_id=twitch_client_id)
    account_queues = {}
    for bot in TwitchBot.objects.all().order_by("-priority"):
        if not bot.is_active():
            continue

        # max_daily_posts = 24 * 60 // bot.account.period
        account_id = bot.account.username + "." + str(bot.account.type)
        if account_id not in account_queues:
            account_queues[account_id] = 0
        account_queue_count = account_queues[account_id]


        def get_post_minute():
            return (minute + bot.account.period) + (account_queue_count * bot.account.period)


        # Don't run bot if its account is filled
        if get_post_minute() >= 24 * 60:
            continue

        # Find correct game name
        game = bot.game if bot.game else None
        if game:
            if game not in games:
                games[game] = client.search.games(query=game)[0]['name']
                if game != games[game]:
                    print("Adjusting " + bot.game + " to " + game)
            game = games[game]

        lang_code = languages.get(bot.language) if bot.language != "All" else None

        # Query top clips
        results = client.clips.get_top(
            channel=bot.channel if bot.channel is not "" else None,
            language=lang_code,
            game=game,
            trending=bot.trending,
            period='month',
            limit=100,
        )

        bot_queue_count = 0
        for clip_data in results:
            post_minute = get_post_minute()
            if bot_queue_count >= bot.max_posts or post_minute >= 24 * 60:
                # The post will not be posted today
                break

            # Check for curator and views and if has been posted before
            if (bot.curator is not "" and clip_data['curator']['name'] != bot.curator) \
                    or clip_data['views'] < bot.min_views \
                    or clip_data['created_at'].date() < bot.created_after \
                    or Post.objects.filter(clip_slug=clip_data['slug']).exists():
                continue

            clip_language = bot.language
            if bot.language == "All":
                clip_language = list(languages.keys())[list(languages.values()).index(clip_data['language'])]

            thumbnail_url = clip_data['thumbnails']['medium']
            download_url = thumbnail_url[0:thumbnail_url.index("-preview-")] + ".mp4"
            Post.objects.create(clip_url=clip_data['url'],
                                clip_slug=clip_data['slug'],
                                thumbnail_url=thumbnail_url,
                                download_url=download_url,
                                caption=get_random_caption(bot.captions, clip_language, clip_data),
                                post_minute=post_minute,
                                account=bot.account,
                                bot=bot)
            account_queue_count += 1
            account_queues[account_id] = account_queue_count
            bot_queue_count += 1
    print("Finished. Queued " + str(Post.objects.filter(posted=False).count()) + " posts!")


def get_random_caption(captions, language, clip_data):
    valid_captions = []
    capture = True
    for line in captions.splitlines():
        stripped = line.strip()

        # Don't add blank lines
        if not stripped:
            continue

        # Start or stop capturing lines
        for lang_name, lang_code in languages.items():
            if stripped == lang_name + ":":
                capture = False if capture else lang_name == language
                continue
        if capture:
            valid_captions.append(stripped)

    placeholders = {
        "channel": clip_data['broadcaster']['name'],
        "channel_link": clip_data['broadcaster']['channel_url'],
        "game": clip_data['game'],
        "language": clip_data['language'],
        "curator": clip_data['curator']['name'],
        "curator_link": clip_data['curator']['channel_url'],
        "vod_link": clip_data['vod']['url'] if clip_data['vod'] is not None else "None",
        "duration": clip_data['duration'],
        "created_at": clip_data['created_at'],
        "views": clip_data['views']
    }
    if not valid_captions:
        return clip_data['title']
    rand_index = random.randint(0, len(valid_captions) - 1)
    return valid_captions[rand_index].format(**placeholders)


def process_queue(minute):
    for post in Post.objects.filter(posted=False):
        # post_minute = (80 * post.post_time.hour) + post.post_time.minute
        if minute >= post.post_minute:
            try:
                print("Downloading...")
                local_video_path = "tmp/" + post.download_url.split("/")[-1]
                local_thumbnail_path = "tmp/" + post.thumbnail_url.split("/")[-1]
                resized_video_path = local_video_path + "-resized.mp4"
                urllib.request.urlretrieve(post.download_url, local_video_path)
                urllib.request.urlretrieve(post.thumbnail_url, local_thumbnail_path)
                print("Done!")
                if post.account.type == TWITTER:
                    twitterupload.VideoTweet(file_name=local_video_path,
                                             caption=post.caption,
                                             consumer_key=post.account.consumer_key,
                                             consumer_secret=post.account.consumer_key_secret,
                                             token=post.account.access_token,
                                             token_secret=post.account.access_token_secret).tweet()
                else:
                    # clip = moviepy.editor.VideoFileClip(local_video_path)
                    # # resize(clip, width=600)
                    # clip_resized = resize(clip, width=600)
                    # clip_resized.write_videofile(local_video_path, bitrate="50k")
                    # clip.close()
                    if imageio.plugins.ffmpeg.get_platform().startswith("win"):
                        os.system("cd ffmpeg && {ffmpeg} -i ../{source_video} "
                                  "-vf scale=1560:1080,setdar=13:9 ../{resized_video}"
                                  .format(ffmpeg=ffmpeg,
                                          source_video=local_video_path,
                                          resized_video=resized_video_path))
                    else:
                        os.system("./ffmpeg/{ffmpeg} -i {source_video} -vf scale=1560:1080,setdar=13:9 {resized_video}"
                                  .format(ffmpeg=ffmpeg,
                                          source_video=local_video_path,
                                          resized_video=resized_video_path))

                    image = Image.open(local_thumbnail_path)
                    # width, height = image.size
                    # size = max(256, width, height)
                    # print(width, height)
                    # resized = Image.new('RGB', (size, size))
                    # resized.paste(image, ((size - width) // 2, (size - height) // 2))
                    # resized.save(local_thumbnail_path)
                    resized = image.resize((600, 400), Image.ANTIALIAS)
                    resized.save(local_thumbnail_path)
                    image.close()

                    api = InstagramAPI(username=post.account.username, password=post.account.password)
                    if api.login():
                        time.sleep(3)
                        print("Uploading...")
                        api.uploadVideo(resized_video_path, local_thumbnail_path, caption=post.caption)
                        time.sleep(2)
                        api.logout()
                        print("Finished Uploading")
                        time.sleep(2)
                    else:
                        raise AuthenticationError("Failed to login to Instagram account: " + post.account.username)
                # Immediately update post data if there was no error
                post.post_time = util.get_current_time()
                post.posted = True
                post.save()

                # Delete temporary files
                os.remove(local_video_path)
                os.remove(local_thumbnail_path)
                if resized_video_path != local_video_path:
                    os.remove(resized_video_path)

                # Log result
                log_message(add_post_data("{time}) posted clip on {account} ({type}). Video URL: {clip}", post))
            except Exception as e:
                traceback.print_exc()
                log_message(add_post_data("{time}) FAILED TO POST ON {account} ({type}). VIDEO URL: {clip}", post)
                            + ", ERROR: " + str(e))
                # with open("application.log", "a+") as log_file:
                #     traceback.print_exc(file=log_file)
                post.delete()


def add_post_data(message, post):
    return message.format(clip=post.clip_url,
                          account=post.account.username,
                          type=account_types.get(post.account.type),
                          time=util.get_current_time().strftime("%Y-%m-%d %H:%M"))


def log_message(message):
    print(message)
    f = open("application.log", "a+")
    f.write(message + "\n")
    f.flush()
    f.close()


"""
{channel}: the name of the channel where the clip originated
{channel_link}: the url of the channel (twitch.tv/channel)
{game}: name of the game that the clip is in
{language}: language that the clip is in / played in
{curator_name}: name of the person who clipped it
{curator_link}: link to the channel of who clipped it
{vod_link}: links to the vod where the clip is from
{title}: title of the clip (or stream?)
{creation_date}: date created at
{duration}: length of the clip
{views}: number of views the clip has

Notes:
    - English is the default language
    - To switch languages type the language name followed by a colon on its own line 
    - To use braces in your message type two '{{'
    - Using curator or views may result in some less popular clips to be missed due to limitations of the Twitch API
"""

# minutely(5, False)
