# Scraper das datas das sessões do Parlamento

Este scraper tem duas componentes: uma que descarrega a lista a partir do [site do Parlamento](http://www.parlamento.pt) e outra que a vai buscar ao [debates.parlamento.pt](http://debates.parlamento.pt). A razão para mantermos as duas é porque cada fonte tem campos de informação distintos que nos interessam.

## Como correr

    make scrape

## Dependências

* python
* click
* unicodecsv
* splinter
* BeautifulSoup
* zenlog
