#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import click
import csv
import splinter
from bs4 import BeautifulSoup
from collections import OrderedDict
from zenlog import log

OUTFILE = "datas-debates.csv"

URL_FORMATTER = "http://debates.parlamento.pt/catalogo/r3/dar/01/%02d/%02d"
LAST_LEG = 16
LAST_SESS = 1
WEBDRIVER = "selenium"

# URL para uma página:
# http://debates.parlamento.pt/page.aspx?cid=r3.dar&diary=s1l10sl2n56-0010&type=texto

FIELDNAMES = ['leg', 'sess', 'num', 'date', 'published_date', 'pages', 'democratica_url', 'debates_url']

browser = splinter.Browser(user_agent="Mozilla/5.0 ;Windows NT 6.1; WOW64; Trident/7.0; rv:11.0; like Gecko")


def get_dates(leg, sess):
    entries = []
    try:
        browser.visit(URL_FORMATTER % (leg, sess))
    except splinter.request_handler.status_code.HttpResponseError:
        return entries

    soup = BeautifulSoup(browser.html, 'html.parser')
    try:
        rows = soup.find('div', id="painelNumeros").find_all('tr')
    except AttributeError:
        return entries
    for row in rows:
        cols = row.find_all('td')
        if not cols:
            continue
        entry = OrderedDict()
        entry['leg'] = leg
        entry['sess'] = sess
        try:
            num = entry['num'] = int(cols[0].text.strip().split(" ")[-1])
        except ValueError:
            num = entry['num'] = cols[0].text.strip().split(" ")[-1]
        entry['date'] = cols[1].text.strip()
        entry['published_date'] = cols[2].text.strip()
        entry['pages'] = int(cols[3].text.strip())
        entry['democratica_url'] = "http://demo.cratica.org/sessoes/%d/%d/%s/" % (leg, sess, str(num))
        entry['debates_url'] = "http://debates.parlamento.pt" + cols[0].find("a")['href']
        entries.append(entry)
    log.info("Parsed %d entries!" % len(entries))
    return entries


@click.command()
@click.option('-a', '--scrape-all', help='Download all archives (not just most recent legislature)', is_flag=True, default=False)
@click.option('-e', '--extend-file', help='Extend existing CSV file with new results', type=click.Path(exists=True))
def scrape(scrape_all, extend_file):
    entries = []
    if scrape_all:
        for leg in range(1, LAST_LEG + 1):
            for sess in range(1, 5):
                print(leg, sess)
                entries.extend(get_dates(leg, sess))
    else:
        entries.extend(get_dates(LAST_LEG, LAST_SESS))

    with open(OUTFILE, 'w') as f:
        dw = csv.DictWriter(f, fieldnames=FIELDNAMES)
        dw.writeheader()
        for entry in entries:
            dw.writerow(entry)

    if extend_file:
        rows = open(extend_file, 'r').readlines()
        newrows = open(OUTFILE, 'r').readlines()
        rows_to_save = []
        # check if each new row already exists on the file, append otherwise
        for newrow in newrows:
            leg, sess, num = newrow.split(',')[:3]
            exists = False
            for row in rows:
                if row.startswith("%s,%s,%s" % (leg, sess, num)):
                    exists = True
                    break
            if not exists:
                log.info("New entry for %s,%s,%s, appending..." % (leg, sess, num))
                rows_to_save.append(newrow)

        if rows_to_save:
            with open(extend_file, 'a') as f:
                f.writelines(rows_to_save)
        os.remove(OUTFILE)

    browser.quit()


if __name__ == "__main__":
    scrape()
