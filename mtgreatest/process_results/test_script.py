#!/usr/bin/env python

import scrape_results

soup = scrape_results.event_soup('http://magic.wizards.com/en/events/coverage/gpny16')
scrape_results.scrape_standings(soup, 'gpny16');
