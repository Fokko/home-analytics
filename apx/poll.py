from datetime import datetime
from typing import Dict, List

import psycopg2
import requests


def insert_pricing(prices: List[Dict]):
    sql = """
            INSERT INTO apx_prices (
                price_at,
                price_raw_ex_vat
            )
            VALUES(
                %s at time zone 'utc' at time zone 'cet',
                %s
            )
            ON CONFLICT (price_at)
            DO NOTHING;"""
    conn = None
    try:
        # read database configuration
        # connect to the PostgreSQL database
        conn = psycopg2.connect(host="postgres", database="postgres", user="postgres", password="postgres")
        # create a new cursor
        cur = conn.cursor()
        for price in prices:
            # {
            #    "raw_date": "2020-01-05 00:00:00",
            #    "delivery_date": "00:00",
            #    "price_raw_ex_vat": "0.03310",
            #    "price_raw_incl_vat": 0.040050999999999996,
            #    "price_ex_vat": "&euro; 0,03310",
            #    "price_incl_vat": "&euro; 0,04005"
            # }
            print("Inserting: " + str(price["raw_date"]))
            # execute the INSERT statement
            cur.execute(
                sql, (datetime.strptime(price["raw_date"], "%Y-%m-%d %H:%M:%S"), price["price_raw_ex_vat"])
            )
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def download_path(url: str):
    output = requests.get(url=url)
    result = output.json()

    prices = result["data"]
    insert_pricing(prices)


for url in {
    "https://flextarieven.energyzero.nl/prices?type=electricity&period=today",
    "https://flextarieven.energyzero.nl/prices?type=electricity&period=tomorrow",
}:
    download_path(url)
