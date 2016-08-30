import requests
import os
import codecs
from bs4 import BeautifulSoup

from mtgreatest.rdb import Cursor, serialize
from update_events import clean_magic_link

def write_as(text, filename):
    f = codecs.open(filename, 'w', 'utf-8')
    f.write(text)
    f.close()

def scrape_info_type(info_type, soup, event_id):
    if info_type not in os.listdir('.'):
        os.mkdir(info_type)
    os.chdir(info_type)
    alts = ['-a', '-b', '-c']
    round_inds = dict()

    for f in os.listdir('.'):
        os.remove(f)

    results = [el for el in soup.find_all('p') if info_type.upper() in el.text or info_type.capitalize() in el.text]
    for result in results:
        for el in result.parent.find_all('a'):
            r = requests.get(clean_magic_link(el['href']))
            if r.status_code is not 200:
                r.raise_for_status()
            if el.text in round_inds:
                filename = el.text + alts[round_inds[el.text]]
                round_inds[el.text] += 1
            else:
                filename = el.text
                round_inds[el.text] = 0
            filename += '.html'
            write_as(r.text, filename)

    assert len(os.listdir('.')) > 11, 'fewer than 12 rounds detected for type {}'.format(info_type)
    os.chdir('..')

def scrape_link(event_link, event_id):
    os.chdir('/home/ec2-user/mtgreatest/html')
    r = requests.get(event_link)
     
    try:
        if r.status_code is not 200:
            r.raise_for_status()

        if event_id not in os.listdir('.'):
            os.mkdir(event_id)
        os.chdir(event_id)

        write_as(r.text, 'index.html')
        soup = BeautifulSoup(r.text, 'lxml')

        scrape_info_type('results', soup, event_id)
        scrape_info_type('pairings', soup, event_id)
        scrape_info_type('standings', soup, event_id)
    except Exception as error:
        return {'value': -1, 'error': unicode(error)}

    return {'value': 1, 'error': None}

def mark_event(event_link, event_id, result):
    cursor = Cursor()
    entries = [serialize(entry) for entry in [result['value'], result['error'], event_id, event_link]]
    query = "UPDATE event_table set process_status={}, last_error={} where event_id={} and event_link={}".format(*entries)
    cursor.execute(query)
    cursor.close()
    return

def scrape_new_links(num_events):
    cursor = Cursor()
    query = "select event_link, event_id from event_table where process_status=0 order by day_1_date desc limit {}".format(num_events)
    event_infos = cursor.execute(query)
    cursor.close()
    for event_info in event_infos:
        mark_event(*event_info, result=scrape_link(*event_info))


