from pyquery import PyQuery as pq
import requests
from collections import defaultdict


def parse(problematic_string, known_int=False):
    if problematic_string.endswith('Link'):
        problematic_string = problematic_string[:-4]

    cleaned_string = problematic_string.replace('$', '').replace(',', '').replace('\\', '').strip()
    try:
        return int(cleaned_string)
    except ValueError:
        if known_int and cleaned_string == '':
            return float('nan')
        else:
            return problematic_string


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
    INCUBATOR_KEY_IS_INT = {'Cohort Date': False,
                            'Company Name': False,
                            'Confidence': False,
                            'Employees': True,
                            'Exit Value': True,
                            'Funding': True,
                            'State': False,
                            'Website & Crunchbase links': False}

    def get_incubators(self):
        response = requests.get(self.LIST_INCUBATORS_URL)
        if not response.ok:
            raise Exception('Response code was {}'.format(response.status_code))

        d = pq(response.text)
        raw_record_labels = [x.text_content() for x in d('#accellist thead tr th')][1:] + ['id']
        record_labels = [x[:-4] if x.endswith('Find') or x.endswith('Link') else x for x in raw_record_labels]
        raw_rows = [x.findall('td')[1:] for x in d('#accellist tbody tr')]

        records = []
        for row in raw_rows:
            record = dict()
            for index, entry in enumerate(row):
                record[record_labels[index]] = parse(entry.text_content())
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
        record_labels = [x.text_content() for x in d('#seedcos thead tr th')]
        record_labels[record_labels.index('')] = 'Confidence'
        raw_rows = [x.findall('td') for x in d('#seedcos tbody tr')]

        records = []
        for row in raw_rows:
            record = dict()
            for index, entry in enumerate(row):
                record[record_labels[index]] = parse(entry.text_content().strip(), self.INCUBATOR_KEY_IS_INT[record_labels[index]])

            record.pop('Website & Crunchbase links', None)
            records.append(record)

        return records
