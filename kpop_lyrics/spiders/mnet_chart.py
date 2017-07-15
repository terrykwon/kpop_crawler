import scrapy
import datetime

class MnetChartSpider(scrapy.Spider):
    name = 'mnet_chart'
    chart_url = 'http://www.mnet.com/chart/TOP100/{}?pNum={}'

    def start_requests(self):
        urls = []
        dates = [i for i in range(2008, 2018)]
        for d in dates:
            for i in (1, 2):
                urls.append((d, i, self.chart_url.format(d, i)))

        for date, page, url in urls:
            yield scrapy.Request(url=url, meta={'date': date, 'page': page}, callback=self.parse_chart)

    def parse_chart(self, response):
        print(response.meta['date'], response.meta['page'])
        page = response.meta['page']

        info_urls = response.xpath(
            '//div[contains(@class, "MnetMusicList")]//a[@class="MMLI_SongInfo"]/@href').extract()

        for index, url in enumerate(info_urls):
            if page == 1:
                rank = index + 1
            else:
                rank = index + 51

            next_page = response.urljoin(url)

            yield scrapy.Request(next_page,
                                 meta={'rank': rank, 'date': response.meta['date']},
                                 callback=self.parse_song_info)

    # def parse_song_info(self, response):
    #     print(response.meta['rank'])
