import requests
import mtgreatest.utils

from mtgreatest.rdb import Cursor
from mtgreatest.rdb.table_cfg import table_definitions
from bs4 import BeautifulSoup
from update_events import clean_magic_link
from players import fix_name_and_country

RAW_TABLE_NAME = 'standings_raw_table'

def parse_standings_row(soup, event_id):
    values = [item.get_text() for item in soup.find_all('td')]
    if len(values) == 5:
        values.insert(2, None)
    if len(values) != 6:
        return None
    if 'Match Points' in values[3]:
        return None
    values.append(event_id)
    results = dict(zip(table_definitions[RAW_TABLE_NAME], values))
    name_and_country = fix_name_and_country(results['player_name_raw'], results['player_country'])
    results['player_name_raw'] = name_and_country[0]
    results['player_country'] = name_and_country[1]
    return results

def process_standings_link(link, event_id):
    r = requests.get(link)
    if r.status_code is 200:
        soup = BeautifulSoup(r.text)
    else:
        r.raise_for_status()
        return
    standings_table = [parse_standings_row(row, event_id) for row in soup.find('table').find_all('tr') if parse_standings_row(row, event_id) is not None]
    assert len(standings_table) > 0, 'no standings for event {}'.format(event_id)
    upload_standings(standings_table, event_id)

def final_standings_info(soup, event_id):
    final_standings = [el for el in soup.find_all('a') if 'FINAL STANDINGS' in el.text or 'Final Standings' in el.text]
    if len(final_standings) == 0:
      final_standings = [el for el in soup.find_all('a') if ('FINAL' in el.text or 'Final' in el.text) and 'standings' in el.href]
    assert len(final_standings) == 1
    return [clean_magic_link(final_standings[0]['href']), event_id]

def upload_standings(standings_table, event_id):
    print
    print '==========Processing Standings Page for Event{}============'.format(event_id)
    cursor = Cursor()
    print 'Deleting existing rows'
    cursor.execute("delete from {} where event_id='{}'".format(RAW_TABLE_NAME, event_id))
    print 'Writing {} rows'.format(len(standings_table))
    cursor.insert(RAW_TABLE_NAME, standings_table)
    cursor.close()
    cursor = Cursor()
    print 'New {} row count: {}'.format(RAW_TABLE_NAME, cursor.execute('select count(1) from {}'.format(RAW_TABLE_NAME))[0][0])
    cursor.close(commit=False)

def scrape_standings(soup, event_id):
    print 'get info'
    info = final_standings_info(soup, event_id)
    print 'process'
    process_standings_link(info[0], info[1])

def scrape_standings_for_event_link(event_link, event_id):
    try:
        process_standings_link(event_link, event_id)
        return {'value': 2, 'error': None}
    except Exception as error:
        print error
        print "scrape standings for event {} failed".format(event_id)
        return {'value': -2, 'error': error}

def get_new_standings(num_events):
    cursor = Cursor()
    query = "select event_link, event_id from event_table where process_status=1 order by day_1_date desc limit {}".format(num_events)
    event_infos = cursor.execute(query)
    cursor.close()
    for event_info in event_infos:
        mark_event(*event_info, result=scrape_standings_for_event_link(*event_info))

def mark_event(event_link, event_id, result):
    cursor = Cursor()
    query = "UPDATE event_table set process_status={}, last_error={}  where event_id='{}' and event_link='{}'".format(result.value, result.error, event_id, event_link)
    cursor.close()
