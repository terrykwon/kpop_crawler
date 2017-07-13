import scrapy

class TopChartSpider(scrapy.Spider):
    name = 'top_chart'
    date = '20170711'
    unit = 'day'

    def start_requests(self):
        urls = [
            'http://music.bugs.co.kr/chart/track/' + self.unit + '/total?chartdate=' + self.date
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

        for index, info in enumerate(track_infos):
            yield scrapy.Request(info, meta={'rank': index + 1}, callback=self.parse_info)

    def parse_info(self, response):
        """
        Parses a table with information about the song.
        Information includes the title, lyrics, composers, etc.
        """
        rank = response.meta['rank']
        title = response.xpath('//header[contains(@class,"pgTitle")]//h1/text()').extract_first().strip()
        lyrics = response.xpath('//div[contains(@class, "lyricsContainer")]/xmp/text()').extract_first()
        # lyrics = lyrics.replace('\r\n', ' ')

        # Not cleanly extracted because the label differs from song to song.
        # i.e. in some songs, the first span might refer to the composers, in other songs - the album.
        # Therefore, we need to manually parse this.
        raw_info = response.xpath('//div[@class="basicInfo"]/table[@class="info"]//*/text()').extract()

        # Remove all newlines and tabs.
        raw_info = list(map(lambda x: x.strip(), raw_info))

        # Remove empty strings and commas.
        raw_info = list(filter(lambda x: x != '' and x != ',', raw_info))

        # Remove irrelevant tags.
        exclude = ['곡 정보', '참여 정보', '전체 보기']
        raw_info = list(filter(lambda x: x not in exclude, raw_info))

        keys = {
            '순위': 'rank',
            '제목': 'title',
            '아티스트': 'artist',
            '가사': 'lyrics',
            '피쳐링': 'featuring',
            '작곡': 'composer',
            '작사': 'lyricist',
            '편곡': 'arranger',
            '앨범': 'album',
            '재생 시간': 'time'
        }

        info_dict = {
            k: [] for k in keys.values()
        }

        current_category = ''

        for i in raw_info:
            if i in keys:
                current_category = keys[i]
                continue

            if current_category in keys.values():
                info_dict[current_category].append(i)

        info_dict['lyrics'].append(lyrics)
        info_dict['title'].append(title)
        info_dict['rank'].append(str(rank))

        yield info_dict
