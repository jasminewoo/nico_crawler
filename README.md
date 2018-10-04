# nico_crawler

- Download & convert nico videos as audio files.
- Queue-based concurrent downloads (Up to 4 threads)
- Failed downloads get added back to the end of the queue

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
|video_id|`sm12345678`|The video will be downloaded|
|mylist|`mylist/123456`|All videos in the list will be downloaded|
|search|`search/keyword`|- All _popular_ videos in the serach result will be downloaded.| Refer to `minimum_mylist` in [`config.json`](config.json) |
