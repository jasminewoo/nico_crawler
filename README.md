# nico_crawler

- Python ≥ 3.6
- Crawls [nicovideo.jp](https://www.nicovideo.jp) and downloads '歌ってみた' audio files.
- (Optional) Downloaded files get uploaded to Google Drive and get deleted from local disk.
- (Optional) Uses Amazon DynamoDB to keep track of the downloads. This is especially useful if you want to avoid duplicates.
- (Optional) Emails the stacktrace when errors occur.

## Usage

### Start Crawler

```bash
./nico_crawler.sh start &
```

Note: If you plan to leave the process running for an extended period of time, consider using [nohup](https://linux.die.net/man/1/nohup).

### Download Videos Manually

```bash
./nico_crawler.sh download ${url}
```

where `url` is:

|Type|Example|Description|Notes|
|---|---|---|---|
|video_id|`.../sm12345678`|The video will be downloaded|
|mylist|`.../mylist/123456`|All videos in the list will be downloaded|
|search|`.../search/keyword`|All _popular_ videos in the serach result will be downloaded| A _popular_ video needs to satisfy `mylist_count` ≥ [`minimum_mylist`](config.json)|

### Kill Crawler

```bash
./nico_crawler.sh kill
```

### Setup Dependencies

```bash
./nico_crawler.sh google
./nico_crawler.sh aws
```

Note: This is a one-time configuration. 

## Digital Ocean Setup (Ubuntu 18.04)

```bash
# install pip3/venv
apt-get install software-properties-common
apt-add-repository universe
apt-get update
apt-get install python3-pip
apt-get install python3-venv

# install tools
apt install ffmpeg   # For audio conversion

# Clone code
git clone https://github.com/lekordable/nico_crawler.git
```
