import requests
from bs4 import BeautifulSoup as bs


def calculate(date):
    try:
        arr = date.split('.')
        d = arr[0]
        m = arr[1]
        y = arr[2]
        url = "https://moshiach.ru/jdates/date.php?day=" + d + "&month=" + m + "&year=" + y + "&shkia=before"
        r = requests.get(url)
        soup = bs(r.text, "html.parser")
        res = soup.find_all('strong')[1].text
        return res
    except Exception as ex:
        return "Ошибка: " + str(ex)
