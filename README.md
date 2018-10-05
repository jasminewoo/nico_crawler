# nico_crawler

Python >= 3.6

- Download & convert nico videos as audio files.
- Mutithread support (Recommended: 4 threads)
- Failed downloads get added back to the end of the queue so they get tried again
- The in-memory queue periodically gets written to the disk in case of application/system shutdown

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
|search|`.../search/keyword`|All _popular_ videos in the serach result will be downloaded.| A _popular_ video needs to satisfy `mylist_count` > [`minimum_mylist`](config.json)|

## Usage (Remote)

```bash
nohup ./download.sh {url} &
```

## Digital Ocean Setup (Ubuntu 18.04)

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
