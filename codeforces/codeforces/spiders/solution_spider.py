import scrapy
import json
import re

from codeforces.items import CodeforcesSolutionItem

class CodeforcesSolutionSpider(scrapy.Spider):
    name = "codeforces_solution"
    allowed_domains = ["codeforces.com"]
    start_urls = ["https://codeforces.com/problemset/"]

    p_id = re.compile(r'''/(\d+)/''')
    p_index = re.compile(r'''problem/(.+)\?''')

    def parse(self, response):
        for solution_href in response.selector.xpath('//a[@title="Participants solved the problem"]/@href'):
            solution_url = response.urljoin(
                solution_href.extract() + '?order=BY_CONSUMED_TIME_ASC')
            yield scrapy.Request(solution_url, callback=self.parse_problem_solution_list_page)

        if response.selector.xpath('//span[@class="inactive"]/text()').extract():
            if response.selector.xpath('//span[@class="inactive"]/text()')[0].extract() != u'\u2192':
                next_page_href = response.selector.xpath(
                    '//div[@class="pagination"]/ul/li/a[@class="arrow"]/@href')[0]
                next_page_url = response.urljoin(next_page_href.extract())
                yield scrapy.Request(next_page_url, callback=self.parse)
        else:
            next_page_href = response.selector.xpath(
                '//div[@class="pagination"]/ul/li/a[@class="arrow"]/@href')[1]
            next_page_url = response.urljoin(next_page_href.extract())
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_problem_solution_list_page(self, response):
        solution_id_list = response.xpath('//tr/@data-submission-id').extract()

        for solution_id in solution_id_list:
            solution_lang = response.xpath(
                '//tr[@data-submission-id=%s]/td[5]/text()' % solution_id)[0].extract().strip()
            yield scrapy.FormRequest.from_response(response, url='https://codeforces.com/data/submitSource',
                                                   formdata={
                                                       'submissionId': solution_id},
                                                   meta={'p_id': self.p_id.search(response.url).group(1),
                                                         'p_index': self.p_index.search(response.url).group(1),
                                                         's_lang': solution_lang,
                                                         's_sid': solution_id},
                                                   callback=self.parse_solution)

    def parse_solution(self, response):

        json_response = json.loads(response.body)

        item = CodeforcesSolutionItem()

        item['s_pid'] = response.meta['p_id']
        item['s_index'] = response.meta['p_index']
        item['s_source'] = json_response['source']
        item['s_lang'] = response.meta['s_lang']
        item['s_sid'] = response.meta['s_sid']

        yield item
