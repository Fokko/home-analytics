import os
import time
from datetime import datetime
from typing import Dict, Tuple

import psycopg2
from tesla_api import ApiError, TeslaApiClient

# 230 volt, 3 phases, 16 amps
CHARGING_SPEED_PER_MINUTE = ((230 * 16 * 3) / 1000)/60


def is_connected(charge_state: Dict) -> bool:
    if charge_state["charging_state"] in {"Disconnected", "Stopped"}:
        return False
    return True


def est_charge_for_this_hour() -> Tuple[float, bool]:
    conn = None
    est_charge = 0.0
    enabled = False
    try:
        # read database configuration
        # connect to the PostgreSQL database
        conn = psycopg2.connect(host="postgres", database="fokko", user="fokko", password="fokko")
        # create a new cursor
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                est_charge,
                enabled
            FROM tesla_charge_schema
            WHERE slot_start BETWEEN
                current_timestamp AND current_timestamp + interval '1h'
            ORDER BY enabled DESC, created_at DESC
            LIMIT 1
        """
        )

        for row in cur.fetchall():
            est_charge = row[0]
            enabled = row[1]

        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return est_charge, enabled


def store_tesla_state(now: datetime, charge_state: Dict):
    sql = """
            INSERT INTO tesla_readings (
                created_at,
                battery_level,
                charger_actual_current,
                charger_power,
                charger_voltage
            )
            VALUES(
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
                now,
                charge_state["battery_level"],
                charge_state["charger_actual_current"],
                charge_state["charger_power"],
                charge_state["charger_voltage"],
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


if __name__ == "__main__":
    client = TeslaApiClient(os.getenv("TESLA_EMAIL"), os.getenv("TESLA_PASSWORD"))

    # There is just one car...
    oto = client.list_vehicles()[0]
    print("Optimize charging for: " + oto.display_name)

    oto.wake_up()
    inc = 0
    charge_state = {}
    while inc < 22:
        try:
            charge_state = oto.charge.get_state()
            break
        except ApiError as e:
            inc += 1
            print(str(e))
            time.sleep(1)

    # Summer saving
    dt = datetime.now()
    store_tesla_state(dt, charge_state)
    est_charge, enabled = est_charge_for_this_hour()
    # If there is no schema active, we don't want to do anything
    if enabled:
        should_charge = False
        # Check if we still need to charge for this hour
        charged_until_now = dt.minute * CHARGING_SPEED_PER_MINUTE

        print("Charged until now: " + str(charged_until_now))
        print("Expected charge: " + str(est_charge))
        print("Remaining kWh for this hour: " + str(charged_until_now - est_charge))

        if est_charge > charged_until_now:
            should_charge = True

        print("Current state: " + charge_state["charging_state"])

        if charge_state["charging_state"] not in {"Disconnected"}:
            if should_charge and charge_state["charging_state"] == "Stopped":
                print("Start charging")
                oto.charge.start_charging()
            elif not should_charge and charge_state["charging_state"] != "Stopped":
                print("Stop charging")
                oto.charge.stop_charging()
            else:
                print("Nothing to do here...")
    else:
        print("No schedule active")
