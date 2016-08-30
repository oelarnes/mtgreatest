#/usr/bin/env python
import sys
from update_events import update_events
from scrape_event import scrape_new_links

update_events()
scrape_new_links(sys.argv[1])
