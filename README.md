# kpop_crawler
**kpop_crawler** is a web crawler that fetches song details and lyrics from Korean top chart websites.
It implements the [Scrapy](https://scrapy.org/) framework and contains spiders that extend from `scrapy.Spider`.

> **Note**: This project is in its early stages and is subject to (very) frequent changes. However, feel free to use or refer to it for your own use!

## Output
The `bugs_chart` spider fetches information in the following structure:

|*attributes*|date|rank|title|lyrics|artist|featuring|composer|lyricist|arranger|album|time|
|---|---|---|---|---|---|---|---|---|---|---|---|
|*example values*|20170706|1|팔레트 (Feat. G-DRAGON)|이상하게도 요즘엔 그냥 쉬운 게 좋아\r\n...|아이유(IU)|G-DRAGON|아이유(IU)|아이유(IU)|*[empty]*|Palette|03:37|

## Sources
Information is scraped from the following websites:
* http://www.bugs.co.kr
* http://www.mnet.com

## Dependencies
* Python `v3.6`
* [Scrapy](https://scrapy.org/) `v1.4`

## Usage

From the base directory, run the following `Scrapy` command from your terminal:
```
scrapy crawl bugs-chart -o lyrics.csv
```

To save the output in `JSON` format,
```
scrapy crawl bugs-chart -o lyrics.json
```

## Disclaimer
The crawler is meant to be used for non-commercial purposes only (e.g. for sating one's own curiosity), 
and the information fetched should not be shared without permission of the rightful owners. When using the crawler,
one should send requests at a reasonable rate.