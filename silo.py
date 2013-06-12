from pyquery import PyQuery as pq
import requests


def parse_dollar_value(dollar_string):
    cleaned_string = dollar_string.replace('$', '').replace(',', '').strip()
    try:
        return int(cleaned_string)
    except:
        return dollar_string


def parse_incubator_id(incubator_info):
    if isinstance(incubator_info, int):
        return incubator_info
    elif isinstance(incubator_info, dict):
        try:
            return int(incubator_info['id'])
        except:
            pass
    else:
        raise Exception('Unable to parse an incubator id from the input {}'.format(incubator_info))


class SeedDBClient(object):
    LIST_INCUBATORS_URL = 'http://www.seed-db.com/accelerators'
    GET_INCUBATOR_URL_BASE = 'http://www.seed-db.com/accelerators/view?acceleratorid={incubator_id}'
    
    def get_incubators(self):
        response = requests.get(self.LIST_INCUBATORS_URL)
        if not response.ok:
            raise Exception('Response code was {}'.format(response.status_code))
        
        d = pq(response.text)
        raw_record_labels = [x.text_content() for x in d('#accellist thead tr th')][1:] + ['id']
        record_labels = [x[:-4] if x.endswith('Find') or x.endswith('Link') else x for x in raw_record_labels]
        raw_rows = [x.findall('td')[1:] for x in  d('#accellist tbody tr')]
        
        records = []
        for row in raw_rows:
            record = dict()
            for index, entry in enumerate(row):
                record[record_labels[index]] = parse_dollar_value(entry.text_content())
            link = row[0].findall('a')[0].values()[0]
            link_id = link[link.rfind('id=') + 3:]
            record['id'] = link_id
            
            records.append(record)
        
        return records
    
    def get_incubator(self, incubator_info):
        incubator_id = parse_incubator_id(incubator_info)
        
        response = requests.get(self.GET_INCUBATOR_URL_BASE.format(incubator_id=incubator_id))
        if not response.ok:
            raise Exception('Response code was {}'.format(response.status_code))
        
        d = pq(response.text)
        record_labels = [x.text_content() for x in d('#seedcos thead tr th')[1:]]
        record_labels[record_labels.index('')] = 'Confidence'
        raw_rows = [x.findall('td')[1:] for x in d('#seedcos tbody tr')]
        
        records = []
        for row in raw_rows:
            record = dict()
            for index, entry in enumerate(row):
                record[record_labels[index]] = parse_dollar_value(entry.text_content().strip())
            
            records.append(record)
            
        return records
        
if __name__ == '__main__':
    client = SeedDBClient()
    print client.get_incubators()
        