import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook, load_workbook
import re
import time
import os

def find_all_kode():
    '''
    Get all mobile codes from https://www.kody.su/mobile/
    '''
    url = 'https://www.kody.su/mobile/'
    req = requests.get(url)
    # Создание файла .html
    with open('kody.html', 'w') as output_file:
        output_file.write(req.text)
    kode_pool = []
    with open('kody.html', 'r') as output_file:
        contents = output_file.read()
        # Конвертация файла в lxml
        soup = BeautifulSoup(contents, 'lxml')
        strings = soup.find_all(string=re.compile('\d\d\d'))
        for txt in strings:
            try:
                int(txt)
            except ValueError:
                pass
            else:
                kode_pool.append(txt)
    os.remove('kody.html')
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
    # Получение страницы
    req = requests.get(url)
    # Создание файла .html
    with open(f'html\{kod}.html', 'w') as output_file:
        output_file.write(req.text)
    with open(f'html\{kod}.html', 'r') as output_file:
        contents = output_file.read()
        # Конвертация файла в lxml
        soup = BeautifulSoup(contents, 'lxml')
        # Поиск всех тэгов "tr"
        parse = soup.find_all('tr')
        base = []
        for item in parse[1:]:
            buf = []
            # Поиск всех тэгов "td"
            information = item.find_all('td')
            # На некоторых страницах есть пустые поля
            if information[0].text[4:] == '':
                continue
            # На некоторых страницах нетипичный формат записи
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
            # Разбивка строки по 7 символов  
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
    os.remove(f'html\{kod}.html')
    return base

def to_xls(array, row):
    '''
    Write array to xls
    '''
    # Создать рабочую книгу в Excel:
    filename = 'ABC_DEF_new_base.xlsx'
    # Проверка наличия файла и создание/присоединение, в зависимости от результата
    if not os.path.exists(filename):
        wb = Workbook()
    else:
        wb = load_workbook(filename)
    sheet = wb.active
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

def cut_kods_pool(kods_pool):
    new_kods_pool = []
    for element in range(1, len(kods_pool)):
        if int(kods_pool[element-1]) > int(kods_pool[element]):
            new_kods_pool.append(kods_pool[element-1])
            break
        new_kods_pool.append(kods_pool[element-1])
    return new_kods_pool

def main():
    kods_pool = cut_kods_pool(find_all_kode())
    row = 1
    for i, kod in enumerate(kods_pool[:5]):
        row = to_xls(get_base_of_number(kod), row)
        print(f'{i+1} step. {kod} done')
        time.sleep(2)

if __name__ == "__main__":
    main()