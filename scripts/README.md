# Scraper das datas das sessões do Parlamento

Este scraper tem duas componentes: uma que descarrega a lista a partir do [site do Parlamento](http://www.parlamento.pt) e outra que a vai buscar ao [debates.parlamento.pt](http://debates.parlamento.pt). 

Usamos como fonte o `debates.parlamento.pt`, mas mantivemos o scraper do Parlamento porque lá encontramos o campo da data de publicação, que não está presente no Debates.

## Como correr

Primeiro, é preciso instalar as dependências:

    make install

Este comando cria um virtualenv (presente em `.env`) e trata de instalar todos os módulos necessários. Para fazer o scrape e atualizar o dataset, só é preciso:

    make scrape

