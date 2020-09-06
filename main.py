import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook, load_workbook
import re
import time

def find_all_kode():
    '''
    Get all mobile codes from https://www.kody.su/mobile/
    '''
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

def get_base_of_number(kod):
    '''
    Input data: mobile code like '977'
    Сutput data: [
                    [977, [1000000, 1999999], 1xxxxxx, MTC, Липецкая область], 
                    [977, [2000000, 2999999], 2xxxxxx, Мегафон, Москва], 
                    [977, [3000000, 3999999], 3xxxxxx, Билайн, Рязанская область]
                 ]
    Return [code, [interval], mask, operator, region]
    '''
    url = f'https://www.kody.su/mobile/{kod}'
    req = requests.get(url)
    with open(f'{kod}.html', 'w') as output_file:
        output_file.write(req.text)
    with open(f'{kod}.html', 'r') as output_file:
        contents = output_file.read()
        soup = BeautifulSoup(contents, 'lxml')
        parse = soup.find_all('tr')
        base = []
        for item in parse[1:]:
            buf = []
            information = item.find_all('td')
            if information[0].text[4:] == '':
                continue
            point = re.search(r'\.\.\.', information[0].text[4:])
            if point:
                buf.append(kod)
                buf.append(re.split(r'\.\.\.', information[0].text[4:]))
                buf.append(information[0].text[4:])
                for inf in information[1:]:
                    buf.append(inf.text)
                continue
            f = 0
            mass = []    
            for i in range(int(len(information[0].text[4:]) / 7)):
                mass.append(information[0].text[4:][f:f+7])
                f += 7
                newmass = []
            for element in mass:
                buf=[]
                buf.append(kod)
                el = re.sub(r'x+', r'', element)
                start = el + ('0' * (7 - len(el)))
                finish = el + ('9' * (7 - len(el)))
                buf.append([start, finish])
                buf.append(information[0].text[4:])
                for inf in information[1:]:
                    buf.append(inf.text)               
                base.append(buf)
        return base

def to_xls(array, row):
    # Создать рабочую книгу в Excel:
    filename = 'ABC_DEF_new_base.xlsx'
    wb = load_workbook(filename)
    sheet = wb.active
    #sheet = wb.create_sheet('data')
    #sheet.title = 'data'

    # Добавить заголовки в рабочую книгу Excel:
    #row = 1
    if row < 2:
        sheet['A'+str(row)] = 'ABC'
        sheet['B'+str(row)] = 'from'
        sheet['C'+str(row)] = 'to'
        sheet['D'+str(row)] = 'mask'
        sheet['E'+str(row)] = 'operator'
        sheet['F'+str(row)] = 'region'

    # Заполнить данными
    
    for item in array:
        row += 1
        sheet['A'+str(row)] = item[0]
        sheet['B'+str(row)] = item[1][0]
        sheet['C'+str(row)] = item[1][1]
        sheet['D'+str(row)] = item[2]
        sheet['E'+str(row)] = item[3]
        sheet['F'+str(row)] = item[4]
    # Сохранить файл:
    wb.save(filename)
    return row

#string = r'910-34xxxxx'
#string = r'910-34xxxxx35xxxxx'
#kode = '910'
def replace(string):
    '''
    Replace string like '910-34xxxxx35xxxxx' to interval ['3400000', '3599999']
    '''
    buf = []
    f = 0
    point = re.search(r'\.\.\.', string)
    if point:
        return re.split(r'\.\.\.', string)
    for i in range(int(len(string) / 7)):
        buf.append(string[f:f+7])
        f += 7
    mass = re.sub(r'x+', r'', buf[0])
    start = mass + ('0' * (7 - len(mass)))
    mass = re.sub(r'x+', r'', buf[len(buf)-1])
    finish = mass + ('9' * (7 - len(mass)))
    if len(finish) < 7:
        finish = '0' * (7 - len(finish)) + finish
    return [start, finish]

#print(replace('0000xxx0001xxx0002xxx0003xxx'))
kods_pool = find_all_kode()
print(kods_pool)
#print(replace('''777000x777001x777002x777003x777004x777006x777007x777008x777009x77701xx77702xx77703xx77704xx77705xx77706xx77707xx77708xx77709xx7771xxx7772xxx7773xxx777400x777401x777402x777403x7774040777404177740427774043'''))
row = 1
for i, kod in enumerate(kods_pool):
    row = to_xls(get_base_of_number(kod), row)
    print(f'{i+1} step. {kod} done')
    time.sleep(2)

