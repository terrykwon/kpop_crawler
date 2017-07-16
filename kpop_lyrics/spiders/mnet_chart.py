import scrapy
import re


class MnetChartSpider(scrapy.Spider):
    """Fetches song information and lyrics from the Mnet annual top 100 chart.
    """
    name = 'mnet_chart'
    chart_url = 'http://www.mnet.com/chart/TOP100/{}?pNum={}'
    start_year = 2008
    end_year = 2016

    def start_requests(self):
        """For each specified year, starts a request to the corresponding chart URL.
        """
        urls = []
        dates = [i for i in range(self.start_year, self.end_year + 1)]
        for d in dates:
            for i in (1, 2):
                urls.append((d, i, self.chart_url.format(d, i)))

        for date, page, url in urls:
            yield scrapy.Request(url=url, meta={'date': date, 'page': page}, callback=self.parse_chart)

    def parse_chart(self, response):
        """For a chart, gets the list of all 100 songs and starts a request for each of them.
        """
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

    def parse_song_info(self, response):
        """Gets relevant information from a song.
        """
        song_info = {
            'date': int,
            'rank': int,
            'id': int,
            'title': str,
            'artist': str,
            'vocals': [],
            'featuring': [],
            'composer': [],
            'lyricist': [],
            'arranger': [],
            'time': str
        }

        song_info['date'] = response.meta['date']
        song_info['rank'] = response.meta['rank']
        song_info['id'] = re.split('/+', response.url)[3]
        song_info['title'] = response.xpath('//dd[@class="title"]/text()').extract_first()

        time = response.xpath('//dd[@class="title"]/span/text()').extract_first()
        time = time.replace('(', '').replace(')', '')
        song_info['time'] = time

        song_info['artist'] = response.xpath('//dd[@class="title"]/span/a/text()').extract_first()

        info_list = response.xpath('//div[@class="line_info"][2]//*/text()').extract()
        info_list = list(filter(lambda i: '\r\n\t\t' not in i and '&nbsp' not in i, info_list))
        info_list.remove('참여스탭')

        attr_map = {
            '보컬': 'vocals',
            '피쳐링': 'featuring',
            '작사': 'lyricist',
            '작곡': 'composer',
            '편곡': 'arranger'
        }

        current_key = ''
        for item in info_list:
            if item in attr_map:
                current_key = item
            else:
                song_info[attr_map[current_key]].append(item)

        yield song_info

