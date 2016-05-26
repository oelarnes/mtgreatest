#!/usr/bin/env python

import scrape_results
from mtgreatest.rdb import Cursor

cursor = Cursor()

event_info = cursor.execute('select event_id, event_link from event_table where results_loaded = 1')
event_info = [dict(zip(('event_id','event_link'), item)) for item in event_info] #this should be a method (or default return structure) in rdb

failed = []

for row in event_info:
    soup = scrape_results.event_soup(row['event_link'])
    print 'scraping standings for event {}'.format(row['event_id'])
    try:
        scrape_results.scrape_standings(soup, row['event_id'])
    except:
        failed.append(row['event_id'])



        
