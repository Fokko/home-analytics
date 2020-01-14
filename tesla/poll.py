from math import ceil
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from tesla_api import TeslaApiClient, ApiError
import psycopg2
from tabulate import tabulate
import time


def fetch_prices() -> List[Tuple[datetime, float]]:
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

        # Fetch all the relevant prices, ordered by the cheapest hours first
        cur.execute("""
            SET timezone = 'Europe/Amsterdam';
            SELECT
                price_at + interval '1h',
                price_raw_ex_vat
            FROM apx_prices
            WHERE price_at > current_timestamp
            ORDER BY current_timestamp ASC
        """)

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


def is_charging_right_now(charge_state: Dict) -> bool:
    if charge_state['charging_state'] == 'Disconnected':
        return False
    return True


def optimize(now: datetime, charge_state: Dict, prices: List[Tuple[datetime, float]]) -> bool:
    if charge_state['charging_state'] == 'Disconnected':
        print("The car is not connected to a charger")
        return False

    charge_amps = charge_state['charge_current_request']
    # Sometime the API reports 2 volt when it is just connected
    # In The Netherlands, the voltage is normally around 230 volt
    # So we take the min of 220 to be on the safe side
    charge_volts = max(charge_state['charger_voltage'], 220)
    charge_phases = 3.0
    watt_per_hour = charge_amps * charge_volts * charge_phases
    kwh_per_hour = watt_per_hour / 1000
    # We're aiming for 90% charge, charge_limit_soc == 90
    to_be_charged = charge_state['charge_limit_soc'] - charge_state['battery_level']

    # 22 -> .22%
    to_be_charged_percentage = to_be_charged / 100.0

    # This is a big assumption, right now we need to estimate how long we still
    # need to charge. Up to 90% charging is more or less linear, the last 10% from
    # 90 to 100 takes much longer, we don't take that really into a count for this
    # algorithm since we're aiming for the bulk of the charging.

    # Standard range RWD around 50kwh
    kwh_to_be_charged = to_be_charged_percentage * 50.0

    if to_be_charged > 0:
        return determine_slots(now, kwh_to_be_charged, kwh_per_hour, prices)
    print("The battery is charged")
    return False


def determine_slots(now: datetime, kwh_to_be_charged: float, kwh_per_hour: float,
                    prices: List[Tuple[datetime, float]]) -> bool:
    prices = prices or []

    # Check how many slots we need to charge
    charging_hours_ahead = ceil(kwh_to_be_charged / kwh_per_hour)
    print("{} kwh to be charged, battery will be full in {} hours".format(
        kwh_to_be_charged, kwh_to_be_charged / kwh_per_hour))

    charging_hours_ahead_by_date = sorted(prices)  # Sort on tuple, primary sort on date, secondary on price
    charging_hours_ahead_by_price = sorted(prices, key=lambda tup: tup[1])

    # The prices come sorted from the database
    charging_slots = charging_hours_ahead_by_price[0:charging_hours_ahead]

    charging_rates = dict()
    # Compute the charging rates
    for slot in charging_slots:
        if kwh_to_be_charged < kwh_per_hour:
            charge_in_slot = kwh_to_be_charged
        else:
            charge_in_slot = kwh_per_hour

        charging_rates[slot[0]] = charge_in_slot
        kwh_to_be_charged -= charge_in_slot

    # Print a nice overview
    table = []
    for slot in charging_hours_ahead_by_date:
        table.append([
            slot[0],
            slot[1],
            "{} kwh".format(charging_rates.get(slot[0], 0.0)),
            slot in charging_slots
        ])
    print(tabulate(table, headers=["Slot start", "Price kwh (EUR)", "Est. Charge", "Charging"]))

    # Check if we have to charge now
    for slot in charging_slots:
        slot_begin = slot[0]
        slot_end = slot[0] + timedelta(hours=1)
        if slot_begin <= now < slot_end:
            print("{} is in [{}, {})".format(now, slot_begin, slot_end))
            return True
    print("We're not in a charging slot")
    return False


def store(charge_state: Dict):
    sql = """
            INSERT INTO tesla_readings (
                battery_level,
                charger_actual_current,
                charger_power,
                charger_voltage
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
        conn = psycopg2.connect(
            host="postgres",
            database="fokko",
            user="fokko",
            password="fokko"
        )
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (
            charge_state['battery_level'],
            charge_state['charger_actual_current'],
            charge_state['charger_power'],
            charge_state['charger_voltage']
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


if __name__ == '__main__':
    client = TeslaApiClient('fokkodriesprong@godatadriven.com', 'vo123')

    # There is just one car...
    oto = client.list_vehicles()[0]
    print("Optimize charging for: {}".format(oto.display_name))

    oto.wake_up()
    inc = 0
    charge_state = {}
    while inc < 22:
        try:
            charge_state = oto.charge.get_state()
            break
        except ApiError as e:
            inc += 1
            print("Try {} got error: {}".format(inc, e))
            time.sleep(1)

    store(charge_state)
    optimize(datetime.now(), charge_state, fetch_prices())
