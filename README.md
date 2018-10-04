# nico_crawler

- Download & convert nico videos as audio files.
- Queue-based concurrent downloads (Recommended: up to 4)
- Failed downloads get added back to the end of the queue
- The queue periodically gets written to the disk in case of application/system shutdown

## Prerequisite

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
