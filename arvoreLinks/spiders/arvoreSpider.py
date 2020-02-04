import scrapy
from datetime import datetime
from arvoreLinks.DAO.ConnectionDB import ConnectionDB
import re

class QuotesSpider(scrapy.Spider):
    name = "arvore"
    connectionDB = ConnectionDB()
    start_urls = []
  

    def start_requests(self):

        self.start_urls = self.connectionDB.selectSolr()
        print('Start ' + str(len(self.start_urls)))
        for link in self.start_urls:
            url = link['id']
            yield scrapy.Request(url, callback=self.parse, 
                cb_kwargs=dict(main_id = link['id_veiculo'],main_link = link ),
                meta={
                'splash': {
                    'endpoint': 'render.html',
                    'args': {'wait': 3}
                }
            })

    def  getListaRegex(self):
        return ['twitter.com','facebook.com','instagram.com','youtube.com','youtu.br','linkedin.com']
  
    def getLink(self,selector,urlVeiculo):
        try:
            link = selector.xpath("@href").extract_first().replace('whatsapp://send?text=','')
            for regex in self.getListaRegex():
                if link.find(regex) != -1:
                    return None
            urlBase = urlVeiculo.replace('http://','').replace('https://','')
            if link.find(urlBase) == -1 and link.find('http:') == -1 and link.find('https:')  == -1:
                if link[0] == '/' and urlVeiculo[-1] == '/':
                    return urlVeiculo + link[1:]
                elif link[0] != '/' and urlVeiculo[-1] == '/':
                    return urlVeiculo + link
                elif urlVeiculo[-1] != '/' and link[0] != '/':
                    return urlVeiculo + '/' + link
            elif link.find(urlBase) != -1 and link.find('http:') == -1 and link.find('https:')  == -1 and link[0:3].find('//') != -1:
                return 'http:' + link
            elif link.find(urlBase) != -1 and link.find('http://') == -1 and link.find('https://')  == -1:
                return 'http://' + link

            else:
                return link             


        except:
            return None
    def findIdLink(self,Id):
        for link in self.start_urls:
            if link['id'] == Id:
                return link
        return None

    def parse(self, response,main_id,main_link):
        a_selectors = response.xpath("//a")
        links = []
        print(type(main_id))
        main_id = re.sub('[^0-9]', '', str(main_id))
        print('Id ' + str(main_id))
        veiculo = self.connectionDB.selectVeiculoId(main_id)
        print(veiculo)
        if veiculo is not None:
            for selector in a_selectors:
                newLink = self.getLink(selector, veiculo[3])
                if newLink is not None:
                    json = {
                        "id": newLink,
                        "url_capturada":  newLink,
                        "capturada": False,
                        "veiculo": veiculo[1],
                        "url_veiculo": veiculo[3],
                        "id_veiculo": veiculo[0],
                        "tiragem": veiculo[2],
                        "data captura": datetime.now(),
                        "lido": False,
                    }
                    links.append(json)
                    print(json['url_veiculo'])
                    print(json['url_capturada'])
             
            main_link['lido'] = True
            self.connectionDB.updateLido(main_link)
            self.connectionDB.insertSolr(links)