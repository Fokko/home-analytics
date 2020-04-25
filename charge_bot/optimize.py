import logging
from datetime import datetime
from math import ceil
from typing import List, Tuple

import psycopg2
from tabulate import tabulate

logger = logging.getLogger(__name__)


def compute_kwh_price_net(price_gross: float) -> float:
    tax = 0.0977
    ode = 0.0273
    btw = 1.21  # 21% btw
    return (price_gross + tax + ode) * btw


def cancel_schema() -> None:
    sql = "UPDATE tesla_charge_schema SET enabled = FALSE"
    conn = None
    try:
        # read database configuration
        # connect to the PostgreSQL database
        conn = psycopg2.connect(host="postgres", database="fokko", user="fokko", password="fokko")
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql)

        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def get_battery_level() -> float:
    sql = """
        SELECT battery_level
        FROM tesla_readings
        WHERE created_at = (
            SELECT MAX(created_at) FROM tesla_readings
        )
    """
    conn = None
    battery_level = None
    try:
        # read database configuration
        # connect to the PostgreSQL database
        conn = psycopg2.connect(host="postgres", database="fokko", user="fokko", password="fokko")
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql)

        battery_level = cur.fetchall()[0][0]

        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return battery_level


def store_charge_schema(now: datetime, slot_start: datetime, price_kwh: float, est_charge: float):
    sql = """
            INSERT INTO tesla_charge_schema (
                created_at,
                slot_start,
                price_kwh,
                est_charge
            )
            VALUES(
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
        cur.execute(sql, (now, slot_start, price_kwh, est_charge))
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def determine_slots(
    now: datetime, kwh_to_be_charged: float, kwh_per_hour: float, prices: List[Tuple[datetime, float]]
) -> str:
    prices = prices or []

    # Check how many slots we need to charge
    charging_hours_ahead = ceil(kwh_to_be_charged / kwh_per_hour)
    print(
        "%s kwh to be charged, battery will be full in %s hours",
        kwh_to_be_charged,
        kwh_to_be_charged / kwh_per_hour,
    )

    charging_hours_ahead_by_date = sorted(prices)  # Sort on tuple, primary sort on date, secondary on price
    charging_hours_ahead_by_price = sorted(prices, key=lambda tup: tup[1])

    # The prices come sorted from the database
    charging_slots = charging_hours_ahead_by_price[0:charging_hours_ahead]

    charge_schema = dict()
    # Compute the charging rates
    for slot in charging_slots:
        if kwh_to_be_charged < kwh_per_hour:
            charge_in_slot = kwh_to_be_charged
        else:
            charge_in_slot = kwh_per_hour
        charge_schema[slot[0]] = charge_in_slot
        kwh_to_be_charged -= charge_in_slot

    # Print a nice overview
    table = []
    for slot in charging_hours_ahead_by_date:
        kwhs = round(charge_schema.get(slot[0], 0.0), 2)
        rate = compute_kwh_price_net(slot[1])
        table.append([slot[0], round(rate, 4), "{} kwh".format(kwhs), kwhs * rate])
        store_charge_schema(now, slot[0], slot[1], kwhs)

    return tabulate(table, headers=["Slot start", "Price kwh", "Est. Charge", "Total price"], tablefmt="psql")


def optimize(now: datetime, battery_level: float, prices: List[Tuple[datetime, float]]) -> str:
    charge_amps = 16
    charge_volts = 230
    charge_phases = 3.0
    watt_per_hour = charge_amps * charge_volts * charge_phases
    kwh_per_hour = watt_per_hour / 1000
    # We're aiming for 90% charge, charge_limit_soc == 90
    to_be_charged = 90 - battery_level

    # 22 -> .22%
    to_be_charged_percentage = to_be_charged / 100.0

    # This is a big assumption, right now we need to estimate how long we still
    # need to charge. Up to 90% charging is more or less linear, the last 10% from
    # 90 to 100 takes much longer, we don't take that really into a count for this
    # algorithm since we're aiming for the bulk of the charging.

    # Standard range RWD around 50kwh
    kwh_to_be_charged = to_be_charged_percentage * 50.0

    return determine_slots(now, kwh_to_be_charged, kwh_per_hour, prices)


def fetch_prices() -> List[Tuple[datetime, float]]:
    conn = None
    try:
        # read database configuration
        # connect to the PostgreSQL database
        conn = psycopg2.connect(host="postgres", database="fokko", user="fokko", password="fokko")
        # create a new cursor
        cur = conn.cursor()

        # Fetch all the relevant prices, ordered by the cheapest hours first
        cur.execute(
            """
            SELECT
                price_at,
                price_raw_ex_vat
            FROM apx_prices
            WHERE price_at > current_timestamp
              AND price_at < now()::date + interval '32h'
            ORDER BY current_timestamp ASC
        """
        )

        prices = []
        for row in cur.fetchall():
            prices.append((row[0], row[1]))

        # close communication with the database
        cur.close()

        return prices
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def make_charging_schema() -> str:
    return optimize(datetime.now(), get_battery_level(), fetch_prices())
