import logging
import os
import time
from datetime import datetime
from typing import Dict

import psycopg2
from tesla_api import ApiError, TeslaApiClient

logger = logging.getLogger(__name__)

# 230 volt, 3 phases, 16 amps
CHARGING_SPEED = (230 * 16 * 3) / 1000


def is_connected(charge_state: Dict) -> bool:
    if charge_state["charging_state"] in {"Disconnected", "Stopped"}:
        return False
    return True


def est_charge_for_this_hour() -> float:
    conn = None
    est_charge = 0.0
    try:
        # read database configuration
        # connect to the PostgreSQL database
        conn = psycopg2.connect(host="postgres", database="fokko", user="fokko", password="fokko")
        # create a new cursor
        cur = conn.cursor()
        cur.execute(
            """
            SELECT est_charge
            FROM tesla_charge_schema
            WHERE enabled AND created_at BETWEEN
                current_timestamp AND current_timestamp + interval '1h'
        """
        )

        for row in cur.fetchall():
            est_charge = row[0]

        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.info(error)
    finally:
        if conn is not None:
            conn.close()
    return est_charge


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
        logger.info(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    client = TeslaApiClient(os.getenv("TESLA_EMAIL"), os.getenv("TESLA_PASSWORD"))

    # There is just one car...
    oto = client.list_vehicles()[0]
    logger.info("Optimize charging for: %s", oto.display_name)

    oto.wake_up()
    inc = 0
    charge_state = {}
    while inc < 22:
        try:
            charge_state = oto.charge.get_state()
            break
        except ApiError as e:
            inc += 1
            logger.exception(e)
            time.sleep(1)

    # Summer saving
    dt = datetime.now()
    store_tesla_state(dt, charge_state)
    est_charge = est_charge_for_this_hour()
    should_charge = False
    # Check if we still need to charge for this hour
    if est_charge > dt.minute * CHARGING_SPEED:
        should_charge = True

    if charge_state["charging_state"] not in {"Disconnected"}:
        if should_charge and charge_state["charging_state"] == "Stopped":
            logger.info("Start charging")
            oto.charge.start_charging()
        elif not should_charge and charge_state["charging_state"] != "Stopped":
            logger.info("Stop charging")
            oto.charge.stop_charging()
        else:
            logger.info("Nothing to do here...")
    else:
        logger.info("Current state: %s", charge_state["charging_state"])
