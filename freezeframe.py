from moviepy.editor import *
from pytube import YouTube
import os, urllib, urllib2, random
from bs4 import BeautifulSoup
from twython import Twython


# DELETE OLD VIDEO 

try:
    os.remove('input.mp4')
except OSError:
    pass

try:
    os.remove('input_2.mp4')
except OSError:
    pass

try:
    os.remove('input_early.mp4')
except OSError:
    pass



# SEARCH YOUTUBE

def youTubeSearch():

	# choose a random dictionary word to search
	word_file = "/usr/share/dict/words"
	WORDS = open(word_file).read().splitlines()
	videoSearch = random.choice(WORDS);

	# search for, and randomly select YouTube videos in search
	print "SEARCHING: "+videoSearch+"\n"
	videos = []
	query = urllib.quote(videoSearch)
	url = "https://www.youtube.com/results?search_query=" + query + "+-music+-game+-math" # music/game/math gives us uninteresting videos, remove from search. (still tweaking this)
	response = urllib2.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html)
	for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
	    videos.append('https://www.youtube.com' + vid['href'])
	videos.pop(0)
	videos = [i for i in videos if not ("channel" in i)] # don't want channels
	videoChoice = random.choice(videos)
	print "YOUTUBE SEARCH: Downloading "+videoChoice+"\n"
	return videoChoice

# Try to download a clip
i = 0
videoChoice = youTubeSearch()
yt = None

while yt is None:
    try:
        yt = YouTube(videoChoice)
    except:
		print "YOUTUBE SEARCH: Trying again..."
		i = i+1
		if i > 5:
			print "YOUTUBE SEARCH: Trying something else... \n"
			videoChoice = youTubeSearch()
			i = 0
		pass


# Choose the lowest quality we can find & download
quality = str(yt.filter('mp4')[-1])

if "360p" in quality:
	print "YOUTUBE: Choosing 360p \n"
	yt.set_filename('input_early')
	video = yt.get('mp4','360p')
	video.download('')

elif "720p" in quality: 
	print "YOUTUBE: Choosing 720p \n"
	yt.set_filename('input_early')
	video = yt.get('mp4','720p')
	video.download('')




# EDIT VIDEO

clipArea = int(VideoFileClip("input_early.mp4").duration/2) # pick from the middle of the video

# clip to 5 sec
command = "ffmpeg-3.2-64bit-static/ffmpeg -i input_early.mp4 -ss "+str(clipArea)+" -t 5 input_2.mp4"
print "FFMPEG: Clipping down to 5 sec \n"
os.system(command)

# convert to 360p (easier to manage)
command2 = "ffmpeg-3.2-64bit-static/ffmpeg -i input_2.mp4 -vf scale=-2:360 input.mp4"
print "FFMPEG: Resizing to 360p \n"
os.system(command2)

# pull it in for manipulation
clip = VideoFileClip("input.mp4")

# add in our audio clip
audioclip = AudioFileClip("recordscratch_vo.wav")
comp = concatenate_audioclips([clip.audio,audioclip])


# make that freeze frame
endtime = clip.duration - 0.1 # the videos ffmpeg exports aren't always exact in time, this ensures we get a freeze frame as close to the end as possible
freezeframe = clip.to_ImageClip(t=endtime)
screensize = VideoFileClip("input.mp4").size
freezeclip = (freezeframe
            .resize(height=screensize[1]*4)
            .resize(lambda t : 1+0.02*t)
            .set_position(('center', 'center'))
            .set_duration(8)
            )
freezeclip = CompositeVideoClip([freezeclip]).resize(width=screensize[0])
freezevid = CompositeVideoClip([freezeclip.set_position(('center', 'center'))], 
                         size=screensize)


# combine and export video
final_clip = concatenate_videoclips([clip,freezevid]).set_duration(13).set_audio(comp)
final_clip.write_videofile("final.mp4",audio_codec='aac')


# TWEET IT

APP_KEY = ''
APP_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''

twitter = Twython(APP_KEY, APP_SECRET, ACCESS_KEY, ACCESS_SECRET)

tweetCopy = ["*record scratch*","*freeze frame*","Yup, that's me.","You're probably wondering how I ended up in this situation."]
 
video = open('final.mp4', 'rb')
response = twitter.upload_video(media=video, media_type='video/mp4')
twitter.update_status(status=random.choice(tweetCopy), media_ids=[response['media_id']])

