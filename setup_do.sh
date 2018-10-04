#
# Note: run this script as a super user
#

# install pip3
apt-get install software-properties-common
apt-add-repository universe
apt-get update
apt-get install python3-pip

# install tools
curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
chmod a+rx /usr/local/bin/youtube-dl
apt install ffmpeg
apt install zip

# Clone code

https://github.com/lekordable/nico_crawler.git

#
# nohup nico_crawler/download_audio.sh $URL &
#