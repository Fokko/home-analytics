from typing import Dict
from xml.dom.minidom import parseString

import psycopg2
import requests

IP = "192.168.1.246"


# SG Ready connection
# A = 1
# B = 2


def fetch_current_state() -> Dict[int, bool]:
    """Get the current states of the relay"""
    response = requests.get(f"http://{IP}/index.xml")
    response.raise_for_status()
    document = parseString(response.text)
    return {
        idx: document.getElementsByTagName(f"Rly{idx}")[0].firstChild.nodeValue != "0" for idx in range(1, 3)
    }


def toggle_state(relay_idx: int):
    response = requests.get(f"http://{IP}/dscript.cgi?V20448={relay_idx}")
    response.raise_for_status()


def fetch_desired_state() -> Dict[int, bool]:
    # Simple rules for now, when it drops below or equal to 0.05EUR the compressor kicks in,
    # and below or equal to zero the heating element starts burning power
    # When the price is above average + 1 variance, the compressor will be blocked to avoid
    # running the compressor when the prices are high
    sql = """
        WITH price_cap AS (
            SELECT
                date(price_at) dt,
                AVG(price_raw_ex_vat) + VARIANCE(price_raw_ex_vat) cutoff
            FROM
                apx_prices
            GROUP BY 1
        )

        SELECT
            price_raw_ex_vat < 0.01 OR price_raw_ex_vat >= price_cap.cutoff AS A,
            price_raw_ex_vat <= 0.05                                        AS B
        FROM
            apx_prices
        JOIN price_cap ON price_cap.dt = date(apx_prices.price_at)
        WHERE price_at BETWEEN NOW() + interval '1 hour' AND NOW() + interval '2 hour'
    """
    desired_state = {}
    conn = None
    try:
        conn = psycopg2.connect(host="postgres", database="postgres", user="postgres", password="postgres")
        cur = conn.cursor()
        cur.execute(sql)
        res = cur.fetchone()
        desired_state = {idx + 1: res[idx] for idx in range(2)}
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return desired_state


def check_state():
    current_state = fetch_current_state()
    desired_state = fetch_desired_state()
    for idx, idx_state in current_state.items():
        if idx_state != desired_state[idx]:
            toggle_state(idx)


check_state()
