#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import click
import unicodecsv as csv
import splinter
from bs4 import BeautifulSoup
from collections import OrderedDict
from zenlog import log

OUTFILE = "datas-parlamento.csv"

BASE_URL = "http://www.parlamento.pt/DAR/Paginas/DAR1Serie.aspx"
LAST_LEG = 13
LAST_SESS = 1
WEBDRIVER = "phantomjs"

# URL para uma página:
# http://debates.parlamento.pt/page.aspx?cid=r3.dar&diary=s1l10sl2n56-0010&type=texto

FIELDNAMES = ['leg', 'sess', 'num', 'date', 'pub_date', 'published_date', 'notes']

browser = splinter.Browser(WEBDRIVER)


def get_dates(leg, sess):
    browser.visit(BASE_URL)

    leg_box = browser.find_by_id('ctl00_ctl43_g_322eea22_ecb3_49d3_aa7c_3a66576bec2e_ctl00_ddlLegislatura').first
    options = leg_box.find_by_tag('option')
    idx = LAST_LEG - leg
    browser.select("ctl00$ctl43$g_322eea22_ecb3_49d3_aa7c_3a66576bec2e$ctl00$ddlLegislatura", options[idx].value)
    print "selected"
    if browser.is_text_not_present("A carregar", wait_time=10):
        print "Loaded!"
        pass
    else:
        assert False

    sess_box = browser.find_by_id('ctl00_ctl43_g_322eea22_ecb3_49d3_aa7c_3a66576bec2e_ctl00_ddlSessaoLegislativa').first
    options = sess_box.find_by_tag('option')
    idx = len(options) - sess
    browser.select('ctl00$ctl43$g_322eea22_ecb3_49d3_aa7c_3a66576bec2e$ctl00$ddlSessaoLegislativa', options[idx].value)
    print "selected"
    if browser.is_text_not_present("A carregar", wait_time=10):
        print "Loaded!"
        pass
    else:
        assert False

    entries = []
    if browser.is_text_present(u"Não foram encontrados diários", wait_time=7):
        # esta combinação legislatura/sessão não existe
        return entries

    soup = BeautifulSoup(browser.html)
    rows = soup.find_all('tr', attrs={"class": ["ARTabResultadosLinhaImpar", "ARTabResultadosLinhaPar"]})
    rows.reverse()
    for row in rows:
        cols = row.find_all('td')
        entry = OrderedDict()
        entry['leg'] = leg
        entry['sess'] = sess
        try:
            entry['num'] = int(cols[0].find("a").text.split(" ")[-1])
        except ValueError:
            entry['num'] = cols[0].find("a").text.split(" ")[-1]
        if entry['num'] in ("Z", "Sumários"):
            # Sumários
            continue
        entry['date'] = cols[1].text.strip()
        entry['pub_date'] = cols[1].text.strip()
        entry['published_date'] = cols[2].text.strip()
        entry['notes'] = cols[3].text.strip()
        entries.append(entry)
    log.info("Parsed %d entries!" % len(entries))
    return entries


@click.command()
@click.option('-a', '--scrape-all', help='Download all archives (not just most recent legislature)', is_flag=True, default=False)
@click.option('-e', '--extend-file', help='Extend existing CSV file with new results', type=click.Path(exists=True))
def scrape(scrape_all, extend_file):
    entries = []
    if scrape_all:
        for leg in range(12, LAST_LEG + 1):
            for sess in range(1, 5):
                print leg, sess
                entries.extend(get_dates(leg, sess))
    else:
        entries.extend(get_dates(LAST_LEG, LAST_SESS))

    with open(OUTFILE, 'wb') as f:
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
