#/usr/bin/env python
import sys
from update_events import update_events
from scrape_event import scrape_new_links
from raw_results import get_new_results

#update_events()
scrape_new_links(sys.argv[1])
get_new_results(sys.argv[1])
