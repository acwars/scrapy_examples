# Define your item pipelines here

import json

class CodeforcesspiderPipeline(object):

    def __init__(self):
        self.file = open('data.json', 'wb')

    def process_item(self, item, spider):
        data = json.dumps(
                dict(item),
                ensure_ascii = False,
                indent = 4,
                sort_keys = True,
                separators = (',',': ')
        ) + ",\n"
        self.file.write(data.encode('utf-8'))
        return item

    def spider_closed(self, spider):
        self.file.write("]")
        self.file.close()
