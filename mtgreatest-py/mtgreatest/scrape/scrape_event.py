import requests
import os
from bs4 import BeautifulSoup

os.chdir('../../../html')

def validate(text, page_type):
    return true

def write_as(text, filename):
    f = open(filename, 'a')
    f.write(text)
    f.close()

def scrape_info_type(info_type, soup, event_id):
    if info_type not in os.listdir():
        os.mkdir(info_type)
    os.chdir(info_type)

    for f in os.listdir():
        os.remove(f)

    results = [el for el in soup.find_all('p') if info_type.upper() in el.text or info_type.capitalize() in el.text]
    for result in results:
        for el in result.parent.find_all('a'):
            r = requests.get(clean_magic_link(el['href'])
            if r.status_code is not 200:
                r.raise_for_status()
            #undo this decision tomorrow!
            write_as(r.text, el.text)




        round_infos.extend([(clean_magic_link(el['href']), event_id, re.search('[0-9]+', el.text) and int(re.search('[0-9]+', el.text).group())) \
            for el in result.parent.find_all('a')])
    os.chdir('..')
    

def scrape_link(event_link, event_id):
    r = requests.get(event_link)
     
    try:
        if r.status_code is not 200:
            r.raise_for_status()

        if event_id not in os.listdir():
            os.mkdir(event_id)
        os.chdir(event_id)

        if not validate(r.text, 'main'):
            r.raise_for_status('invalid main event page for event_id {}'.format(event_id))

        write_as(r.text, 'index.html')
        soup = BeautifulSoup(r.text, 'lxml')

        scrape_results(soup, event_id)
        scrape_standings(soup, event_id)
        scrape_pairings(soup, event_id)
    except Exception as error:
        return (False, error)

    return 

def get_new_results(num_events):
    cursor = Cursor()
    query = "select event_link, event_id from event_table where process_status=0 order by day_1_date desc limit {}".format(num_events)
    event_infos = cursor.execute(query)
    cursor.close()
    for event_info in event_infos:
        mark_event(*event_info, result=scrape_link(*event_info))


