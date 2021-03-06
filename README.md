# nico_crawler

nico_crawler is a serverless application that can be deployed to AWS Cloud. It crawls [nicovideo.jp](https://nicovideo.jp) and finds '歌ってみた' songs.

* Sends out a daily list of songs that satisfy [your set of conditions](config/user.json). See [Crawling Logic](#crawling-logic) for details.
* From the daily list, user can choose songs to save to the designated Amazon S3 bucket.
* Lambda, SQS, and DynamoDB are used in a very casual manner, and the costs should be covered by the [Free Tier](https://aws.amazon.com/free/) offers. However, you will have to pay for S3. See [S3 Cost Estimation](#s3-cost-estimation) for details. 


## Setup Guide

1. Create an SNS topic and subscribe yourself (email, SMS, etc). Make a note of the ARN.
1. Using the ARN from the previous step, modify [`This line`](nc_template.yaml). 
1. Install [sam](https://aws.amazon.com/serverless/sam/).
1. Run the following bash commands:
    ```bash
    aws cloudformation ... nc_bucket.yaml
    (sam command for the lambda function...TBD)
    ```
## Architecture

See the sequence diagram below to understand how this application is structured.

![Sequence Diagram](sequence_diagram.svg)

### Crawling Logic
Here is a little block of pseudo code that demonstrates what's happening behind the scenes. 
```python
def crawl_queue_handler(message):
    video = message.video
    
    if video.id not in download_history and is_satisfied(user_def_conditions, video):
        new_message = DownloadMessage(video=video)
        download_queue.put(new_message)
        
    if message.remaining_depth > 0:
        new_depth = message.remaining_depth - 1
        for related_video in get_related_videos(video):
            if video.id == related_video.id:
                continue
            new_message = CrawlMessage(video=related_video, remaining_depth=new_depth)
            crawl_queue.put(new_message)

def get_related_videos(video):
    more_by_uploader = nico_client.profile(video.uploader).get_all_videos()
    search_results = nico_client.search(video.title)
    return more_by_uploader + search_results
```


## S3 Cost Estimation

Assumptions:
* Your stack resides in the Tokyo region.
* You empty your bucket once a month.
* Request fees are not included in the calculation, because they are most likely negligible.

```python
# Adjust the values for your usage
SONGS_PER_MONTH = 50
GB_PER_SONG = 0.007
MONTHLY_STORAGE_COST_PER_GB = 0.019
TRANSFER_OUT_COST_PER_GB = 0.114

cost_store = sum(range(SONGS_PER_MONTH)) * GB_PER_SONG * MONTHLY_STORAGE_COST_PER_GB
cost_transfer = SONGS_PER_MONTH * GB_PER_SONG * TRANSFER_OUT_COST_PER_GB

print('Monthly Cost:')
print(f'Storage \t${round(cost_store, 2)}')
print(f'Transfer\t${round(cost_transfer, 2)}')
```

```
Monthly Cost:
Storage 	$0.16
Transfer	$0.04
```
