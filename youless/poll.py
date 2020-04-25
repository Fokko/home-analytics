from typing import Dict

import psycopg2
import requests


def insert_reading(reading: Dict):
    sql = """
            INSERT INTO youless_readings (
                created_at,
                net_counter,
                power,
                consumption_high,
                consumption_low,
                production_high,
                production_low,
                gas
            )
            VALUES(
                to_timestamp(%s) AT TIME ZONE 'UTC',
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            );"""
    conn = None
    try:
        # read database configuration
        # connect to the PostgreSQL database
        conn = psycopg2.connect(host="postgres", database="fokko", user="fokko", password="fokko")
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(
            sql,
            (
                reading["tm"],
                reading["net"],
                reading["pwr"],
                reading["p1"],
                reading["p2"],
                reading["n1"],
                reading["n2"],
                reading["gas"],
            ),
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


# "tm": unix-time-format (1489333828 => Sun, 12 Mar 2017 15:50:28 GMT)
# "net": Netto counter, as displayed in the web-interface of the LS-120.
#        It seems equal to: p1 + p2 - n1 - n2 Perhaps also includes some user set offset.
# "pwr": Actual power use in Watt (can be negative)
# "p1": P1 consumption counter (low tariff)
# "p2": P2 consumption counter (high tariff)
# "n1": N1 production counter (low tariff)
# "n2": N2 production counter (high tariff)
# "Gas": counter gas-meter (in m^3)

youless_address = "http://192.168.1.158/e?f=j"

output = requests.get(url=youless_address)
reading = output.json()[0]

insert_reading(reading)
