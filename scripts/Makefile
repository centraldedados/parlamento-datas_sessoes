scrape:
	. `pwd`/.env/bin/activate; python scraper-datas-debates.py -e ../data/datas-debates-novo.csv

install:
	virtualenv .env --no-site-packages --distribute --prompt=\(scraper\)
	. `pwd`/.env/bin/activate; pip install -r requirements.txt

deploy:
	git add ../data/datas-debates-novo.csv
	git commit -m "Atualização automática"
	git push origin master
