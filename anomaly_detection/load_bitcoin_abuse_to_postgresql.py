import psycopg2
import pandas as pd
import requests
import json
import io

# Initializes the table to fetch anomalous labels from bitcoin_abuse database into postgresql

# Database configurations
with open("/home/ec2-user/etl/extract/config.json") as config_file:
    config = json.load(config_file)

# Connecting to Database
conn = psycopg2.connect(database = config['postgre']['database'],
                            host = config['postgre']['host'],
                            user = config['postgre']['user'],
                            password = config['postgre']['password'],
                            port = config['postgre']['port'])

# To execute queries and retrieve data
cursor = conn.cursor()

def writeToJSONFile(path, fileName, data):
    filePathNameWExt = './' + path + '/' + fileName + '.json'
    with open(filePathNameWExt, 'w') as fp:
        json.dump(data, fp)

from datetime import date
abuse_today = requests.get("https://www.bitcoinabuse.com/api/download/1d?", params={'api_token': "vSRr9j7VkNyrQrZqOs3drvBqUAh3pnqqoOjNMZai"})
if (abuse_today.ok):
    data = abuse_today.content.decode('utf8')
    df = pd.read_csv(io.StringIO(data))

    today = date.today().strftime("%b-%d-%Y")
    path = 'bitcoin_anomaly/bitcoin_abuse/bitcoin_abuse_daily/' + today + '.csv'
    df.to_csv(path)

sql = """INSERT INTO illicit_label (account, label)
            VALUES(%s, %s) RETURNING index;"""

for index, row in df.iterrows():
    address = row['address']
    label = str(1)
    cursor.execute(sql, (address, label, ))
    conn.commit()

#Check if duplicates exists
select_sql = "SELECT account FROM ILLICIT_LABEL WHERE LABEL = 1"
df_abuse = pd.read_sql(select_sql, conn)
temp = df_abuse.groupby(df_abuse.columns.tolist(),as_index=False).size()
print(temp[temp['size'] > 1])

def clean_duplicates():
    query = """
    WITH cte AS ( SELECT index, account, ROW_NUMBER() OVER (PARTITION BY account ORDER BY account) row_num
    FROM 
    illicit_label
    )
    DELETE FROM illicit_label
    WHERE index in (select index from cte where row_num > 1)
    """

    cursor.execute(query)
    conn.commit()
    cursor.close()

clean_duplicates()

#Check if duplicates still exists, should be empty
select_sql = "SELECT account FROM ILLICIT_LABEL WHERE LABEL = 1"
df_abuse = pd.read_sql(select_sql, conn)
dups = df_abuse.groupby(df_abuse.columns.tolist(),as_index=False).size()
print(dups[dups['size'] > 1])

cursor.close()
conn.close()