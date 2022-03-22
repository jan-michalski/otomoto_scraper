from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import pandas as pd
import re

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

id_list = []
prod_list = []
mil_list = []
pagecount = []
# specify mileage start value for scraping
mil_start = 15000
mil_end = 19999
page = 1

def get_last_page(mil_start, mil_end):
    otomoto = "https://www.otomoto.pl/osobowe?search%5Border%5D=filter_float_mileage%3Aasc&search%5Bfilter_float_mileage%3Afrom%5D={mil_start}&search%5Bfilter_float_mileage%3Ato%5D={mil_end}&page={page}".format(mil_start=mil_start,mil_end=mil_end,page=page)
    html = urlopen(otomoto, context=ctx).read()
    soup = BeautifulSoup(html, "html.parser")
    last_page = "1"
    for elem in soup.find_all("ul", attrs={"om-pager rel"}):
        x = elem.find_all("span", attrs={"class":"page"})
        y = len(x)
        last_page = x[y-1].text
        print(last_page)
    if int(last_page) is None:
        return 1
    return int(last_page)

def scrap(last_page):
    for count in range (1, last_page+1):
        print("processing page " + str(count) + "/" + str(last_page))
        otomoto = "https://www.otomoto.pl/osobowe?search%5Border%5D=filter_float_mileage%3Aasc&search%5Bfilter_float_mileage%3Afrom%5D={mil_start}&search%5Bfilter_float_mileage%3Ato%5D={mil_end}&page={page}".format(mil_start=mil_start,mil_end=mil_end,page=count)
        
        html = urlopen(otomoto, context=ctx).read()
        soup = BeautifulSoup(html, "html.parser")

        filenam = "otomoto_%d.html"%(count,)
        with open(filenam, 'w', encoding='utf-8') as file:
            file.write(str(soup))
        
        for element in soup.findAll('ul', attrs={"class":"ds-params-block"}):
            milSoup = None
            for cell in element.findAll('li', attrs={"class":"ds-param", "data-code":"year"}):
                value = cell.text
                value = value.replace('\n','')
                if not value.strip():
                    prod_list.append('0')
                    continue
                prod_list.append(value.strip())

            milSoup = element.find('li', attrs={"class":"ds-param", "data-code":"mileage"})
            if milSoup is not None:
                value = milSoup.text
                value = value.replace('\n','')
                x = value.replace(" ", "")
                x = re.findall('[0-9]+', x)[0]
                mil_list.append(x)
            else:
                mil_list.append('0')
                
        for element in soup.find_all("article"):
            for stat in element.find_all('a', attrs={"class":"offer-title__link"}):
                id_list.append(stat.get("data-ad-id"))
                pagecount.append(count)

#specify mileage end value for scraping
while mil_end < 50000:
    print("processing range: " + str(mil_start) + "-" + str(mil_end))
    last_page = get_last_page(mil_start, mil_end)
    scrap(last_page)
    mil_start = mil_start + 5000
    mil_end = mil_end + 5000

df = pd.DataFrame()
df['id'] = pd.Series(id_list)
df['production'] = pd.Series(prod_list)
df['mileage'] = pd.Series(mil_list)
df['pagecount'] = pd.Series(pagecount)

print(df)
df.to_csv("mileage_data.csv")



