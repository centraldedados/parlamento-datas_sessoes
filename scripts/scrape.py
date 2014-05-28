#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scraperwiki
import urllib, urllib2
import BeautifulSoup
from dateutil.parser import parse as date_parse

url = "http://debates.parlamento.pt/index.aspx?cid=r3.dar"

def scrape_indexes(leg, sess):
    # Get Viewstate and Eventvalidation from base URL
    response = urllib2.urlopen(url)
    r = response.read()
    soup = BeautifulSoup.BeautifulSoup(r)
    params = {"ctl00$ContentPlaceHolder1$IndexDiaries1$rpSearch$ctl00$ddlLegislature": "l%d" % leg,
              "ctl00$ContentPlaceHolder1$IndexDiaries1$rpSearch$ctl00$ddlSession": "sl%d" % sess,
              "ctl00$ContentPlaceHolder1$IndexDiaries1$bttSearch": "procurar",
              "ctl00$ContentPlaceHolder1$IndexDiaries1$hdPage": "",
             }
    params["__VIEWSTATE"] = soup.find('input', id="__VIEWSTATE")["value"]
    params["__EVENTVALIDATION"] = soup.find('input', id="__EVENTVALIDATION")["value"]
    data = urllib.urlencode(params)

    # Now make a proper POST request
    response = urllib2.urlopen(url, data)
    r = response.read()

    # Get the table rows with results
    soup = BeautifulSoup.BeautifulSoup(r)
    rows = soup.findAll(True, {'class': ['resultseven', 'resultsodd']})
    for row in rows:
        cols = row.findAll('td')
        number = int(cols[0].text)
        leg = int(leg)
        sess = int(sess)
        id = "l%02ds%02dn%03d" % (leg, sess, number)

        entry = {}
        entry["id"] = id
        entry["leg"] = leg
        entry["sess"] = sess
        entry["number"] = number
        entry["pub_date"] = date_parse(cols[1].text)
        entry["session_date"] = date_parse(cols[2].text)
        page_range = cols[3].text
        page_start, page_end = page_range.split('-')
        entry["page_start"] = int(page_start)
        entry["page_end"] = int(page_end)


        scraperwiki.sqlite.save(unique_keys=["id"], table_name="data", data=entry)

    return len(rows)

# number of sessions per legislature
SESSIONS = {12:3, 11: 2, 10: 4, 9: 3, 8: 3, 7: 4, 6: 4, 5: 4, 4: 2, 3: 2, 2: 3, 1: 4,}

for leg in SESSIONS:
    for sess in range(1, SESSIONS[leg]+1):
        leg = int(leg)
        sess = int(sess)
        id = "l%02ds%02d" % (leg, sess)
        result = scrape_indexes(leg, sess)
        if not result:
            print id, "No results, retrying..."
            result2 = scrape_indexes(leg, sess)
            if not result2:
                print id, "No results again. Giving up."
            else:
                print id, "Second try worked!"
        else:
            print id, "Saved results!"
