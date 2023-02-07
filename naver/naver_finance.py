import requests
from bs4 import BeautifulSoup
import pandas as pd

def crawl(code):
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    res = requests.get(url)
    bsobj = BeautifulSoup(res.text, "html.parser")

    div_today = bsobj.find("div", {"class":"today"}) # 현재가
    em = div_today.find("em")

    prics = em.find("span", {"class":"blind"}).text

    h_company = bsobj.find("div", {"class":"h_company"}) # 회사명
    name = h_company.a.text

    div_description = h_company.find("div", {"class":"description"}) # 회사정보
    code = div_description.span.text

    table_no_info = bsobj.find("table", {"class":"no_info"}) # 전일, 시가, 고가, 저가, 거래량, 거래대금
    tds = table_no_info.tr.findAll("td")
    volume = tds[2].find("span", {"class":"blind"}).text

    dic = {"현재가":prics, "기업명":name, "code":code, "거래량":volume}
    return dic 

codes = ["035720", "005930", "000660"]

r = []
for code in codes:
    dic = crawl(code)
    r.append(dic)
    
#print(r)

df = pd.DataFrame(r)
df.to_excel("crawl.xlsx")