import pdb
import requests
import mtgreatest.utils as utils
import re

from mtgreatest.rdb import Cursor, serialize
from bs4 import BeautifulSoup
from update_events import clean_magic_link
from players import fix_name_and_country
from mtgreatest.rdb.table_cfg import table_definitions

RAW_TABLE_NAME = 'results_raw_table'

def get_new_results(num_events):
    cursor = Cursor()
    query = "select event_link, event_id from event_table where process_status=0 order by day_1_date desc limit {}".format(num_events)
    event_infos = cursor.execute(query)
    cursor.close()
    for event_info in event_infos:
        mark_event(*event_info, result=process_event_link(*event_info))

def mark_event(event_link, event_id, result):
    cursor = Cursor()
    entries = [serialize(entry) for entry in [result['value'], result['error'], event_id, event_link]]
    query = "UPDATE event_table set process_status={}, last_error={} where event_id={} and event_link={}".format(*entries)
    cursor.execute(query)
    cursor.close()
    return

def upload_round_results(results_table, event_id, round_num):
    # results_table must all have same round_num and represent all results for that round!!
    print
    print '==========Processing Results for Event {}, Round {}=========='.format(event_id, round_num)
    cursor = Cursor()
    print 'Writing {} rows'.format(len(results_table))
    cursor.insert(RAW_TABLE_NAME, results_table)
    cursor.close()
    cursor = Cursor()
    print 'New {} row count: {}'.format(RAW_TABLE_NAME, cursor.execute('select count(1) from {}'.format(RAW_TABLE_NAME))[0][0])
    cursor.close(commit=False)

def parse_elim_name(name_and_result):
    split = name_and_result.split(', ')
    if len(split) == 1:
        return [split[0], '']
    if len(split) == 2:
        #could be either last, first or first last, result
        result_chars = ['012- ']
        if min([char in result_chars for char in split[1]]):
            return [split[0], split[1]]
        else:
            return [name_and_result, '']
    if len(split) == 3:
        return [', '.join(split[:2]), split[2]]
    else:
        raise 'too many commas in elimination text' 


def elim_results(soup, event_id, max_round_num):
    ELIM_ERR_MSG = 'Could not interpret elimation round results for event {}'.format(event_id)
    bracket_pairs = soup.find('div', class_='top-bracket-slider').find_all('div', class_='dual-players')
    use_winners = False
    winners = []
    if len(bracket_pairs) in [4, 8]:
        #sometimes the winner is listed on the next level of the bracket, sometimes on the same level.
        #this is for when its on the next level
        use_winners = True
        player = bracket_pairs.pop().find_all('div', class_='player')
        assert len(player) is 1
        p = player[0].text.strip().lstrip('()123456789 ')
        p_part = parse_elim_name(p)
        p_name_raw = utils.standardize_name(p_part[0])
        winners.append({'name': utils.standardize_name(p_part[0]), 'result': p_part[1]})
    bracket_pairs.reverse()
    results_table = []
    print '{} matches found in elimination rounds'.format(len(bracket_pairs))
    for idx, pair in enumerate(bracket_pairs):
        players = list(pair.find_all('div', class_='player'))
        p1 = players[0].text.strip().lstrip('()123456789 ')
        p2 = players[1].text.strip().lstrip('()123456789 ')
        p1_part = parse_elim_name(p1)
        p2_part = parse_elim_name(p2)
        p1_name_raw = utils.standardize_name(p1_part[0])
        p2_name_raw = utils.standardize_name(p2_part[0])

        if use_winners:
            if p1_name_raw in [row['name'] for row in winners]:
                ind = [row['name'] for row in winners].index(p1_name_raw)
                result_raw = 'Won ' + [row['result'] for row in winners][ind]
            elif p2_name_raw in [row['name'] for row in winners]:
                ind = [row['name'] for row in winners].index(p2_name_raw)
                result_raw = 'Lost ' + [row['result'] for row in winners][ind]
            else:
                raise Exception(ELIM_ERR_MSG)
            winners.insert(0, {'name': p1_name_raw, 'result': p1_part[1]})
            winners.insert(0, {'name': p2_name_raw, 'result': p2_part[1]})
        else:
            strong = pair.find('strong')
            srong = strong.text.strip().lstrip('()12345678 ')
            result_raw = ''
            if strong == p1 or len(p1_part[1]) > 0 and len(p2_part[1]) == 0:
                result_raw = 'Won ' + p1_part[2]
            if strong == p2 or len(p2_part[1]) > 0 and len(p2_part[1]) == 0:
                if len(result_raw) > 0:
                    raise Exception(ELIM_ERR_MSG)
                result_raw = 'Lost ' + utils.str_reverse(p2_part[1])
            if len(result_raw)==0:
                raise Exception(ELIM_ERR_MSG)

        if len(bracket_pairs) == 7:
            if idx > 2:
                round_num = max_round_num + 1
            elif idx > 0:
                round_num = max_round_num + 2
            else:
                round_num = max_round_num + 3
        elif len(bracket_pairs) == 3:
            if idx > 0:
                round_num = max_round_num + 1
            else:
                round_num = max_round_num + 2
        else:
            round_num = max_round_num + 1

        row = {
            'p1_name_raw' : p1_name_raw,
            'p2_name_raw' : p2_name_raw,
            'result_raw' : result_raw,
            'round_num' : round_num,
            'event_id' : event_id,
            'elim' : 1,
            'vs' : 'vs.'
        }
        results_table.append(row)

    upload_round_results(results_table, event_id, max_round_num + 1)

def all_rounds_info(soup, event_id):
    results = [el for el in soup.find_all('p') if 'RESULTS' in el.text or 'Results' in el.text]
    #please forgive me
    round_infos = []
    for result in results:
        round_infos.extend([(clean_magic_link(el['href']), event_id, re.search('[0-9]+', el.text) and int(re.search('[0-9]+', el.text).group())) \
            for el in result.parent.find_all('a')])
    return round_infos

def event_soup(event_link):
    r = requests.get(event_link)
    if r.status_code is 200:
        soup = BeautifulSoup(r.text, 'lxml')
        return soup
    else:
        r.raise_for_status()
        return

def process_event_link(event_link, event_id):
    failed_links = []
    try:
        soup = event_soup(event_link)
        print 'Deleting existing rows for event {}'.format(event_id)
        cursor = Cursor()
        cursor.execute("delete from {} where event_id='{}'".format(RAW_TABLE_NAME, event_id))
        cursor.close()
        rounds_info = all_rounds_info(soup, event_id)
        print 'Round info parsed for event {}'.format(rounds_info[0][1])
        for round_ in rounds_info:
            try:
                process_results_link(*round_)
                print '>>>>>>{} Round {} Successfully Processed<<<<<<'.format(round_[1], round_[2])
            except Exception as error:
                print error
                print 'XXXXXX{} Round {} Failed XXXXXXX'.format(round_[1], round_[2])
                failed_links.append(round_[0])
        elim_results(soup, event_id, max([info[2] for info in rounds_info]))
        if len(failed_links) > 0:
            print 'Event {} Incomplete :('.format(rounds_info[0][1])
            return {'value': -1, 'error': unicode(error)}
        else:
            print 'Event {} Successfully Processed!'.format(rounds_info[0][1]) 
            return {'value': 1, 'error': None}
    except Exception as error:
        print error
        print 'Event Link {} Failed :('.format(event_link)
        return {'value': -1, 'error': unicode(error)}

def parse_row(soup, round_num, event_id):
    # we assume rows are either of the format table_definitions[RAW_TABLE_NAME] or 'table_id','p1_name_raw','results_raw',('vs',)'p2_name_raw'
    values = [item.get_text() for item in soup.find_all('td')]
    if len(values) == 4:
        values.insert(3, 'vs')
    if len(values) == 5:
        values.insert(2, None)
        values.insert(6, None)
    if len(values) != 7:
        return None
    if 'Table' in values[0]:
        return None
    values[0] = re.search('[0-9]+', values[0])
    values[0] = values[0] and int(values[0].group())
    values.insert(0, round_num)
    values.insert(0, event_id)
    values.append(0)
    values.append(0)
    results = dict(zip(table_definitions[RAW_TABLE_NAME], values))
    name_and_country_1 = fix_name_and_country(results['p1_name_raw'], results['p1_country'])
    name_and_country_2 = fix_name_and_country(results['p2_name_raw'], results['p2_country'])
    results['p1_name_raw'] = name_and_country_1[0]
    results['p1_country'] = name_and_country_1[1]
    results['p2_name_raw'] = name_and_country_2[0]
    results['p2_country'] = name_and_country_2[1]
    return results

def process_results_link(link, event_id, round_num):
    r = requests.get(link)
    if r.status_code is 200:
        soup = BeautifulSoup(r.text, 'lxml')
    else:
        r.raise_for_status()
        return
    results_table = [parse_row(row, round_num, event_id) for row in soup.find('table').find_all('tr') if parse_row(row, round_num, event_id) is not None]
    assert len(results_table) > 0, 'no results for event {}, round {}'.format(event_id, round_num)
    upload_round_results(results_table, event_id, round_num)



