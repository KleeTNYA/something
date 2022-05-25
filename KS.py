# Подключаем библиотеки
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

import requests

data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
dol = data['Valute']['USD']['Value']

CREDENTIALS_FILE = '.json'  # Имя файла с закрытым ключом, вы должны подставить свое

# Читаем ключи из файла
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API

spreadsheet = service.spreadsheets().create(body = {
    'properties': {'title': 'Первый тестовый документ', 'locale': 'ru_RU'},
    'sheets': [{'properties': {'sheetType': 'GRID',
                               'sheetId': 0,
                               'title': 'Лист номер один',
                               'gridProperties': {'rowCount': 100, 'columnCount': 15}}}]
}).execute()
spreadsheetId = spreadsheet['spreadsheetId'] # сохраняем идентификатор файла
print('https://docs.google.com/spreadsheets/d/' + spreadsheetId)

driveService = apiclient.discovery.build('drive', 'v3', http = httpAuth) # Выбираем работу с Google Drive и 3 версию API
access = driveService.permissions().create(
    fileId = spreadsheetId,
    body = {'type': 'user', 'role': 'writer', 'emailAddress': '@gmail.com'},  # Открываем доступ на редактирование
    fields = 'id'
).execute()

# Добавление листа
results = service.spreadsheets().batchUpdate(
    spreadsheetId = spreadsheetId,
    body =
{
  "requests": [
    {
      "addSheet": {
        "properties": {
          "title": "Еще один лист",
          "gridProperties": {
            "rowCount": 20,
            "columnCount": 12
          }
        }
      }
    }
  ]
}).execute()

results = service.spreadsheets().values().batchUpdate(spreadsheetId = spreadsheetId, body = {
    "valueInputOption": "USER_ENTERED",
    "data": [
        {"range": "A1:E51",
         "majorDimension": "ROWS",
         "values": [
                    ["№", "заказ №", "стоимость,$", "срок поставки"],
                    ['1', "1249708", "675", "24.05.2022"]  # Заполнение строк данных с заказами
                   ]}
    ]
}).execute()

ranges = ["A1:E51"] # Вывод строк в консоли

results = service.spreadsheets().values().batchGet(spreadsheetId = spreadsheetId,
                                     ranges = ranges,
                                     valueRenderOption = 'FORMATTED_VALUE',
                                     dateTimeRenderOption = 'FORMATTED_STRING').execute()
sheet_values = results['valueRanges'][0]['values']
print(sheet_values)

""" Создаем базу данных
    Столбцы копируем из гугл таблицы
    С помощью SQL запросов переводим доллары в рубли путем умножения на 'dol' """
import psycopg2
from pprint import pprint

con = psycopg2.connect(
  database="postgres",
  user="postgres",
  password="1234",
  host="127.0.0.1",
  port="5432"
)

print("Database opened successfully")
cur = con.cursor()
cur.execute(
  "INSERT INTO KANALSERVICE (NUMBER,ZAKAZ,DOLLARS,DATA) VALUES ('1', '1249708', '675', '24.05.2022')"
)

con.commit()
print("Record inserted successfully")

con.close()

cur.execute("SELECT NUMBER, ZAKAZ, DOLLARS, RUBLS, DATA from KANALSERVICE")

rows = cur.fetchall()
for row in rows:
   print("NUMBER =", row[1])
   print("ZAKAZ =", row[1])
   print("DOLLARS =", row[1])
   print("RUBLS =", row[1])
   print("DATA =", row[4], "\n")

print("Operation done successfully")
con.close()
