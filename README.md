# kpop_lyrics
**kpop_lyrics** is a web crawler that fetches song lyrics and other information from Korean top chart websites. It implements the [Scrapy](https://scrapy.org/) framework and contains spiders that extend from `scrapy.Spider`.

> **Note**: This project is in its early stages and is subject to (very) frequent changes. However, feel free to use or refer to it for your own use!

## Output
The `top_chart` spider fetches information in the following structure:

|*attributes*|title|lyrics|artist|featuring|composer|lyricist|arranger|album|time|
|---|---|---|---|---|---|---|---|---|---|
|*example values*|팔레트 (Feat. G-DRAGON)|이상하게도 요즘엔 그냥 쉬운 게 좋아\r\n...|아이유(IU)|G-DRAGON|아이유(IU)|아이유(IU)|*[empty]*|Palette|03:37|

## Dependencies
* [Scrapy](https://scrapy.org/) `v1.4`

## Usage

From the base directory, run the following `Scrapy` command from your terminal.
```
scrapy crawl top-chart -o lyrics.csv
```

To save the output in `JSON` format,
```
scrapy crawl top-chart -o lyrics.json
```
