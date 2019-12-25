import psycopg2
import requests
from datetime import date, timedelta, datetime

def insert_pricing(prices):
    sql = """
            INSERT INTO apx_prices (
                price_at,
                tariff_usage,
                tariff_return
            )
            VALUES(
                %s,
                %s,
                %s
            )
            ON CONFLICT (price_at) 
            DO NOTHING;"""
    conn = None
    try:
        # read database configuration
        # connect to the PostgreSQL database
        conn = psycopg2.connect(
            host="postgres",
            database="fokko",
            user="fokko",
            password="fokko"
        )
        # create a new cursor
        cur = conn.cursor()
        for price in prices:
            # execute the INSERT statement
            cur.execute(sql, (
                datetime.strptime(price['Timestamp'].split('+')[0], '%Y-%m-%dT%H:%M:%S'),
                price['TariffUsage'],
                price['TariffReturn']
            ))
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

today = date.today() - timedelta(days=1)
tomorrow = date.today()

url = "https://mijn.easyenergy.com/nl/api/tariff/getapxtariffslasttimestamp"

# Returns "2019-12-24T23:00:00+01:00"
dt = requests.get(url = url, verify=False).json()

# Gets 2019-12-24T23:00:00
date = dt.split('+')[0]

last_timestamp = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
day_before_last_timestamp = last_timestamp - timedelta(days=1)

url = "https://mijn.easyenergy.com/nl/api/tariff/getapxtariffs" \
      "?startTimestamp=" + day_before_last_timestamp.strftime("%Y-%m-%d") + "T23%3A00%3A00.000Z" \
      "&endTimestamp=" + last_timestamp.strftime("%Y-%m-%d") + "T23%3A00%3A00.000Z&grouping="

output = requests.get(url = url,verify=False)
prices = output.json()

insert_pricing(prices)
