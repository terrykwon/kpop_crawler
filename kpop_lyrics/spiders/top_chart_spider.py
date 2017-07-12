from collections import defaultdict

import scrapy

class TopChartSpider(scrapy.Spider):
    name = 'top_chart'

    def start_requests(self):
        urls = [
            'http://music.bugs.co.kr/chart/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_chart)

    # def parse(self, response):
    #     page = response.url.split('/')[-2]
    #     filename = 'bugs-%s.html' % page
    #     with open(filename, 'wb') as f:
    #         f.write(response.body)
    #     self.log('Saved file %s' % filename)

    def parse_chart(self, response):
        """
        For each item (song) in the top 100 chart, this method fetches
        the link to the info page. The info page contains information such as the artist(s), lyrics, and composer(s).
        """

        # track_infos = response.css('a.trackInfo::attr(href)').extract()
        track_infos = response.xpath('//a[contains(@class, "trackInfo")]/@href').extract()

        for info in track_infos:
            yield scrapy.Request(info, callback=self.parse_info)

    def parse_info(self, response):
        self.spans = response.css('div.basicInfo table.info td span')

        title = response.xpath('//header[contains(@class,"pgTitle")]//h1/text()').extract_first().strip()
        lyrics = response.xpath('//div[contains(@class, "lyricsContainer")]/xmp/text()').extract_first()
        # lyrics = lyrics.replace('\r\n', ' ')

        # Not cleanly extracted because the label differs from song to song.
        # i.e. in some songs, the first span might refer to the composers, in other songs - the album.
        # Therefore, we need to manually parse this.
        info = response.xpath('//div[@class="basicInfo"]/table[@class="info"]//*/text()').extract()

        # Remove all newlines and tabs.
        info = list(map(lambda x: x.strip(), info))

        # Remove empty strings and commas.
        info = list(filter(lambda x: x != '' and x != ',', info))

        if '곡 정보' in info:
            info.remove('곡 정보')
        if '참여 정보' in info:
            info.remove('참여 정보')
        if '전체 보기' in info:
            info.remove('전체 보기')

        current_category = ''
        arr = defaultdict(list)
        for i in info:
            if i == '아티스트' \
                    or i == '피쳐링' \
                    or i == '작곡' \
                    or i == '작사' \
                    or i == '편곡' \
                    or i == '앨범' \
                    or i == '재생 시간':
                current_category = i
            else:
                # if current_category != '':
                arr[current_category].append(i)

        arr['가사'].append(lyrics)
        arr['제목'].append(title)

        yield arr
