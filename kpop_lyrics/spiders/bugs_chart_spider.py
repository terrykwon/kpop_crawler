import scrapy
import datetime
import re


class BugsChartSpider(scrapy.Spider):
    name = 'bugs_chart'
    start_date = datetime.date(2017, 6, 12)  # IMPORTANT: start date must be a MONDAY
    end_date = datetime.date(2017, 7, 3)   # IMPORTANT: end date must be a MONDAY
    unit = 'week'

    def start_requests(self):
        urls = []

        date = self.start_date
        while date <= self.end_date:
            date_string = str(date).replace('-', '')
            url = 'http://music.bugs.co.kr/chart/track/{}/total?chartdate={}'.format(self.unit, date_string)
            urls.append((date_string, url))

            # Increment date to the next week.
            date = date + datetime.timedelta(days=7)

        for d, u in urls:
            yield scrapy.Request(url=u, meta={'date': d}, callback=self.parse_chart, dont_filter=True)

    def parse_chart(self, response):
        """
        For each item (song) in the top 100 chart, this method fetches
        the link to the info page. The info page contains information such as the artist(s), lyrics, and composer(s).
        """

        # track_infos = response.css('a.trackInfo::attr(href)').extract()
        track_info_urls = response.xpath('//a[contains(@class, "trackInfo")]/@href').extract()

        for index, url in enumerate(track_info_urls):
            id = re.search(r'track/(\d+)?', url).group(1)

            yield scrapy.Request(url,
                                 meta={'id': id, 'rank': index + 1, 'date': response.meta['date']},
                                 callback=self.parse_info, dont_filter=True)

    def parse_info(self, response):
        """
        Parses a table with information about the song.
        Information includes the title, lyrics, composers, etc.
        """
        id = response.meta['id']
        rank = response.meta['rank']
        date = response.meta['date']
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
            '날짜': 'date',
            '순위': 'rank',
            '아이디': 'id',
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
        info_dict['date'].append(date)
        info_dict['id'].append(str(id))

        yield info_dict

    def get_date_next_week(self, date):
        """
        Returns the date one week from now.
        :param date: The reference point.
        :return: The date (YYYYMMDD format).
        """
        year = int(date[0:4])
        month = int(date[4:6])
        day = int(date[6:8])

        date = datetime.date(year, month, day)

        next_week = date + datetime.timedelta(days=7)
        next_week = str(next_week).replace('-', '')

        return next_week
