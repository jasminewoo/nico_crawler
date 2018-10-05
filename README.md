# nico_crawler

- Download & convert nico videos as audio files.
- Queue-based concurrent downloads (Recommended: up to 4)
- Failed downloads get added back to the end of the queue
- The queue periodically gets written to the disk in case of application/system shutdown

## One-time Setup

```bash
./initial_setup.sh
```

## Usage

```bash
./download.sh {url}
```

where `url` is:

|Type|Example|Description|Notes|
|---|---|---|---|
|video_id|`.../sm12345678`|The video will be downloaded|
|mylist|`.../mylist/123456`|All videos in the list will be downloaded|
|search|`.../search/keyword`|- All _popular_ videos in the serach result will be downloaded.| `minimum_mylist` in [`config.json`](config.json) is used to identify popular videos|

## Usage (Remote)

```bash
nohup ./download.sh {url} &
```

## Notes

```bash
url="..."
youtube-dl -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' -o '~/Downloads/%(title)s-%(id)s.%(ext)s' -i -x $url
```

```bash
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
git clone https://github.com/lekordable/nico_crawler.git
```
