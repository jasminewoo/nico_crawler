# nico_crawler

Download & convert niconico videos as mp3 

## Prerequisite

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
deactivate
```

## Usage

### Individual download
```bash
source venv/bin/activate
pyton3 nico_crawler http://www.nicovideo.jp/watch/sm8059867
deactivate
```

### Bulk download

```bash
source venv/bin/activate
pyton3 nico_crawler http://www.nicovideo.jp/mylist/48382005
deactivate
```