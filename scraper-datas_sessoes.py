#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click
from splinter import Browser
from bs4 import BeautifulSoup
from collections import OrderedDict

OUTFILE = "datas_sessoes_plenarias.csv"

BASE_URL = "http://debates.parlamento.pt/index.aspx?cid=r3.dar"
MAX_LEG = 12
WEBDRIVER = "phantomjs"

# URL para uma página:
# http://debates.parlamento.pt/page.aspx?cid=r3.dar&diary=s1l10sl2n56-0010&type=texto

FIELDNAMES = ['leg', 'sess', 'number', 'session_date', 'pub_date', 'page_start', 'page_end']

browser = Browser(WEBDRIVER)


def get_dates(leg, sess):
    browser.visit(BASE_URL)
    browser.select('ctl00$ContentPlaceHolder1$IndexDiaries1$rpSearch$ctl00$ddlLegislature', 'l%02d' % leg)
    browser.select('ctl00$ContentPlaceHolder1$IndexDiaries1$rpSearch$ctl00$ddlSession', 'sl%d' % sess)
    browser.find_by_name("ctl00$ContentPlaceHolder1$IndexDiaries1$bttSearch").first.click()
    entries = []
    if browser.is_text_present(u"Não foram encontrados diários", wait_time=7):
        # esta combinação legislatura/sessão não existe
        return entries

    soup = BeautifulSoup(browser.html)
    rows = soup.find_all('tr', attrs={"class": ["resultseven", "resultsodd"]})
    for row in rows:
        cols = row.find_all('td')
        entry = OrderedDict()
        entry['leg'] = leg
        entry['sess'] = sess
        try:
            entry['number'] = int(cols[0].find("a").text)
        except ValueError:
            entry['number'] = cols[0].find("a").text
        entry['pub_date'] = cols[1].text
        entry['session_date'] = cols[2].text
        entry['page_start'] = int(cols[3].text.split('-')[0])
        entry['page_end'] = int(cols[3].text.split('-')[1])
        entries.append(entry)
    print "Parsed %d entries!" % len(entries)
    return entries


@click.command()
@click.option('-a', '--scrape-all', help='Download all archives (not just most recent legislature)', is_flag=True, default=False)
@click.option('-e', '--extend-file', help='Extend existing CSV file with new results', is_flag=True, default=False)
def scrape(scrape_all, extend_file):
    entries = []
    for leg in range(1, MAX_LEG + 1):
        for sess in range(1, 5):
            print leg, sess
            entries.extend(get_dates(leg, sess))
    import csv
    with open(OUTFILE, 'wb') as f:
        dw = csv.DictWriter(f, fieldnames=FIELDNAMES)
        dw.writeheader()
        for entry in entries:
            dw.writerow(entry)

    browser.quit()

if __name__ == "__main__":
    scrape()
