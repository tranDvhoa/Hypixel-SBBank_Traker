import requests
import json
import sqlite3
from pprint import pprint
from datetime import datetime
import pytz
import json

def getInfo(call):
    r = requests.get(call)
    return r.json()

with open('config.json', 'r') as f:
    config = json.load(f)

uuid = ""
API_KEY = config['api_key']

url = f"https://api.hypixel.net/v2/skyblock/profiles?key={API_KEY}&uuid={uuid}"

data = getInfo(url)

conn = sqlite3.connect(r'C:\Users\Hoa\OneDrive\Desktop\code\bankmanager.db')
conn.cursor().execute("""CREATE TABLE IF NOT EXISTS bankmanager
                         (
                             id             INTEGER PRIMARY KEY AUTOINCREMENT,
                             timestamp      TEXT UNIQUE,
                             amount         REAL,
                             balance        INTEGER,
                             change         TEXT,
                             action         TEXT,
                             initiator_name TEXT
                         )
                      """)

profile = data['profiles'][0]
banking = profile['banking']
balance = round(banking['balance'])
detailed_balance = balance
sql = ('''INSERT OR IGNORE INTO bankmanager (timestamp, amount, balance, change, action, initiator_name)
          VALUES (?, ?, ?, ?, ?, ?)''')

transactions = banking['transactions']
all_transactions = len(transactions)
balance_history = []
new_rows_count = 0

for i in range(0, all_transactions):
    transaction = transactions[all_transactions - 1 - i]
    balance = detailed_balance
    balance_history.append(detailed_balance)
    if transaction['action'] == "DEPOSIT":
        detailed_balance = balance - round(transaction['amount'])
    else:
        detailed_balance = balance + round(transaction['amount'])
balance_history = list(reversed(balance_history))

for i in range(0, all_transactions):

    transaction = transactions[i]
    timestamp = transaction['timestamp']
    utc_time = datetime.fromtimestamp(timestamp / 1000, tz=pytz.utc)
    ca_time = utc_time.astimezone(pytz.timezone('US/Pacific'))
    transaction['timestamp'] = ca_time.strftime('%a, %D %H:%M:%S %p')

    transaction['amount'] = round(transaction['amount'])

    if transaction['action'] == "DEPOSIT":
        change = f"+{transaction['amount']:,}"
    else:
        change = f"-{transaction['amount']:,}"

    data_tuple = (
        transaction['timestamp'],
        transaction['amount'],
        balance_history[i],
        change,
        transaction['action'],
        transaction['initiator_name'],
    )
    cur = conn.execute(sql, data_tuple)
    new_rows_count += cur.rowcount

if new_rows_count > 0:
    print(f"🔥 Phê! Đã cập nhật thêm {new_rows_count} giao dịch mới vào kho dữ liệu")
else:
    print("✅ Dữ liệu đã mới nhất, không có gì thay đổi")
conn.commit()
conn.close()
