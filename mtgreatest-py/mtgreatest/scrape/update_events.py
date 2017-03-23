import requests

from bs4 import BeautifulSoup
from mtgreatest.rdb import Cursor, serialize
from mtgreatest.rdb.table_cfg import table_definitions
from dateutil.parser import parse
from datetime import datetime, timedelta

MAGIC_URL = 'http://magic.wizards.com'
EVENTS_URL = MAGIC_URL + '/en/events/coverage'
EVENT_TABLE_COLUMNS = table_definitions['event_table']

def clean_magic_link(url):
    if url.startswith(('http://','https://')):
        return url
    elif url.startswith('/'):
        return MAGIC_URL + url

def event_id_from_link(url):
    event_id = url.rpartition('/')[2]
    if '=' in event_id:
        event_id = event_id.rpartition('=')[2]
    if event_id in ['welcome', 'Welcome']:
        event_id = url.rpartition('/')[0].rpartition('=')[2]
    if event_id == 'results':
        event_id = url.rpartition('/')[0].rpartition('/')[2]
    if '/' in event_id:
        event_id = event_id.rpartition('/')[2]
    return event_id

def info_text_to_date(text):
    if ')' not in text:
        return None
    date_str = text.partition(')')[0].lstrip(' (')
    dash_idx = date_str.find('-')
    comma_idx = date_str.rfind(',')
    if dash_idx < 0 or comma_idx < 0 or dash_idx > comma_idx:
        return None
    try:
        return parse(date_str[:dash_idx] + date_str[comma_idx:])
    except:
        return None

def info_text_to_fmt_desc(text):
    return text.partition(')')[2].lstrip(u'-\u2014\u2013 ')

def update_event(event_info, all_info):
    if 'event_link' not in event_info:
        return None
    all_info.append(event_info)
    cursor = Cursor()
    query = "select * from event_table where event_link = '{}'".format(event_info['event_link'])
    result = cursor.execute(query)
    if len(result) == 0:
        event_info['process_status'] = 0
        cursor.insert('event_table', [event_info])
    elif len(result) == 1:
        #results should be tables of dicts but for now we can just update with results
        cols = event_info.keys()
        vals = [serialize(val) for val in event_info.values()]
        query = "update event_table set "
        for i in range(len(cols)):
            if i > 0:
                query += ", "
            query += "{} = {}".format(cols[i], vals[i])
        query += " where event_link = {}".format(serialize(event_info['event_link']))
        cursor.execute(query)
    cursor.close()
    return

def clean_up_links(all_info):
    cursor = Cursor()
    table_info = cursor.execute('select event_link, event_id from event_table')
    all_links = [info["event_link"] for info in all_info]
    all_ids = [info['event_id'] for info in all_info]
    unused_info = [info for info in table_info if info[0] not in all_links]
    if len(unused_info) > 0:
        print unused_info
        proceed = raw_input('{} events found, event_table has {} obsolete links. Delete data for obsolete links?\n'.format(len(all_info), len(unused_info)))
        if proceed == 'y' or proceed == 'Y':
            for info in unused_info:
                if info[1] not in all_ids:
                    cursor.execute("delete from results_raw_table where event_id = '{}'".format(info[1]))
                cursor.execute("delete from event_table where event_link = '{}'".format(info[0]))
        cursor.close()

def update_events():
    all_info = []
    r = requests.get(EVENTS_URL)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'lxml')
        sections = soup.find_all('div', class_='bean_block')
        print 'found {} sections'.format(len(sections))
        for section in sections:
            if not section.find('span').text.endswith('Season'):
                continue
            season = section.find('span').text.partition(' ')[0]
            print 'season {}'.format(season)
            paragraphs =  section.find('div').find_all(['p', 'h4'])
            d = {'event_type' : 'Championship', 'season' : season}
            for paragraph in paragraphs:
                if paragraph.name == 'h4':
                    if 'Grand Prix' in paragraph.text:
                        d['event_type'] = 'Grand Prix'
                    if 'Pro Tour' in paragraph.text:
                        d['event_type'] = 'Pro Tour'
                        print 'found PT'
                    if 'Masters' in paragraph.text:
                        d['event_type'] = 'Masters'
                else:
                    for child in paragraph.children:
                        #print child
                        #print '/\/\/\/\/\/\/\/'
                        if child.name in ['b', 'strong']:
                            if 'Grand Prix' in child.text:
                                d['event_type'] = 'Grand Prix'
                            if 'Pro Tour' in child.text:
                                d['event_type'] = 'Pro Tour'
                            if 'Masters' in child.text:
                                d['event_type'] = 'Masters'
                        elif child.name in ['i','em']:
                            if 'fmt_desc' in d:
                                d['fmt_desc'] += child.text
                        elif child.name == 'br':
                            if 'event_link' in d:
                                update_event(d, all_info)
                                d = {'event_type' : d['event_type'], 'season' : season}
                        elif child.name == 'a':
                            if len(child.text) is 0:
                                continue
                            d['event_link'] = clean_magic_link(child['href'])
                            d['event_id'] = event_id_from_link(d['event_link'])
                            if d['event_type'] == 'Championship':
                                d['event_full_name'] = child.text
                            else:
                                d['event_full_name'] = d['event_type'] + ' ' + child.text
                        elif child.name is None:
                            if 'day_1_date' not in d:
                                d['day_1_date'] = info_text_to_date(child)
                                if d['event_type'] in ['Grand Prix', 'Pro Tour'] and d['day_1_date'] is not None:
                                    d['day_2_date'] = d['day_1_date'] + timedelta(1)
                                if d['event_type'] == 'Pro Tour' and d['day_1_date'] is not None:
                                    d['day_3_date'] = d['day_2_date'] + timedelta(1)
                                d['fmt_desc'] = info_text_to_fmt_desc(child)
                            elif 'fmt_desc' in d:
                                d['fmt_desc'] += child
                if 'event_link' in d:
                    update_event(d, all_info)
                    d = {'event_type' : d['event_type'], 'season' : season}
        clean_up_links(all_info) 
    else:
        r.raise_for_status()
    return


