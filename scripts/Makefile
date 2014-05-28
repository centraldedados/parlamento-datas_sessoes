fetch:
	mkdir -p ../data/
	python scrape.py
	sql2csv --db "sqlite:///scraperwiki.sqlite" --query "select * from data" > ../data/parlamento-datas_sessoes_plenarias.csv
	rm scraperwiki.sqlite
