# nico_crawler

- Python ≥ 3.6
- Download & convert nico videos as audio files in parallel
- Failed downloads get added back to the end of the queue so they get tried again
- The in-memory queue periodically gets written to the disk in case of application/system shutdown

## Usage

### Start Daemon Process

```bash
./nico_crawler.sh start &
```

Note: If you are downloading a large collection of videos, consider using it remotely with [nohup](https://linux.die.net/man/1/nohup).

### Download Videos

```bash
./nico_crawler.sh add ${url}
```

where `url` is:

|Type|Example|Description|Notes|
|---|---|---|---|
|video_id|`.../sm12345678`|The video will be downloaded|
|mylist|`.../mylist/123456`|All videos in the list will be downloaded|
|search|`.../search/keyword`|All _popular_ videos in the serach result will be downloaded| A _popular_ video needs to satisfy `mylist_count` ≥ [`minimum_mylist`](config.json)|

### Kill process

```bash
./nico_crawler.sh kill
```

### Auto-upload to Google Drive

```bash
./nico_crawler.sh gd
```

Note: This is a one-time configuration. 

## Digital Ocean Setup (Ubuntu 18.04)

```bash
# install pip3
apt-get install software-properties-common
apt-add-repository universe
apt-get update
apt-get install python3-pip
apt-get install python3-venv

# install tools
apt install ffmpeg   # For audio conversion
apt install zip      # Only if you are zipping the audio files after

# Clone code
git clone https://github.com/lekordable/nico_crawler.git
```
