#!/usr/bin/env python

import scrape_results
from mtgreatest.sql.mtgdb import Cursor

cursor = Cursor()

event_info = cursor.execute('select event_id, event_link from event_table where results_loaded = 1')

soups = [scrape_results.event_soup(row.event_link) for row in event_info]

failed = []

for i in range(len(soups)):
    try:
        scrape_results.scrape_standings(soups[i], event_info[i].event_id)
    except:
        failed.append(event_info[i].event_id)



        
