import requests
from lxml import html
from bs4 import BeautifulSoup
import re

def find_all_kode():
    url = 'https://www.kody.su/mobile/'

    req = requests.get(url)
    with open('test.html', 'w') as output_file:
        output_file.write(req.text)
    kode_pool = []

    with open('test.html', 'r') as output_file:
        contents = output_file.read()

        soup = BeautifulSoup(contents, 'lxml')

        strings = soup.find_all(string=re.compile('\d\d\d'))

        for txt in strings:

            try:
                int(txt)
            except ValueError:
                pass
            else:
                kode_pool.append(txt)
    return kode_pool

region = {}

def get_base_of_number(kode_pool):
    url = 'https://www.kody.su/mobile/910'
    req = requests.get(url)
    with open('910.html', 'w') as output_file:
        output_file.write(req.text)
    with open('910.html', 'r') as output_file:
        contents = output_file.read()
        soup = BeautifulSoup(contents, 'lxml')
        parse = soup.find_all('tr')
        base = []
        for item in parse[1:]:
            buf = []
            information = item.find_all('td')
            for inf in information:
                buf.append(inf.text)

            base.append(buf)
        return base

#str = r'910-34xxxxx'
str = r'910-34xxxxx35xxxxx'
def replace(str):
    mass = re.findall(r'x{4,5}', str)
    str = str[4:]
    number = re.search(r'\d{2,3}', str)
    print(len(mass))
    num = number[0] + (len(mass) - 1)
    str = str(num)

    print(str)

replace(str)

#print(get_base_of_number(find_all_kode()))
