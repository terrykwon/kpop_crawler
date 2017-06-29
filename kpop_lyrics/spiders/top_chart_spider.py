import scrapy

class TopChartSpider(scrapy.Spider):
    name = 'top_chart'

    def start_requests(self):
        urls = [
            'http://music.bugs.co.kr/chart/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # def parse(self, response):
    #     page = response.url.split('/')[-2]
    #     filename = 'bugs-%s.html' % page
    #     with open(filename, 'wb') as f:
    #         f.write(response.body)
    #     self.log('Saved file %s' % filename)

    def parse(self, response):
        # Gets list of 100 titles in chart
        # titles = response.css('#CHARTday table tbody tr th p.title a::text').extract()

        # Gets list of artists in chart
        # But more than 100 because some collaborations -> dropdowns
        artists = response.css('#CHARTday table tbody tr td p.artist a::text').extract()

        track_infos = response.css('a.trackInfo::attr(href)').extract()

        for track in track_infos:
            yield scrapy.Request(track, callback=self.parse2)



    def parse2(self, response):
        self.spans = response.css('div.basicInfo table.info td span')

        yield {
            'lyric': response.css('div.lyricsContainer xmp::text').extract_first(),
            'artists': response.css('div.basicInfo table.info td a::text').extract(),
            'composers': self.spans[1].css('a::text').extract(),
            'lyricists': self.spans[4].css('a::text').extract(),
            'arrangers': self.spans[7].css('a::text').extract()
        }