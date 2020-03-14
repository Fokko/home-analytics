#!/usr/bin/env python3

import asyncio
from typing import Dict

import psycopg2
from pyotgw import pyotgw

PORT = 'socket://192.168.1.157:23'


async def insert_status(status: Dict[str, str]):
    sql = """
            INSERT INTO otgw (
                relative_mod_level,
                control_setpoint,
                ch_water_temp,
                slave_flame_on,
                slave_ch_active
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
        conn = psycopg2.connect(
            host="postgres",
            database="fokko",
            user="fokko",
            password="fokko"
        )
        # create a new cursor
        cur = conn.cursor()
        cur.execute(sql, (
            status['relative_mod_level'],
            status['control_setpoint'],
            status['ch_water_temp'],
            status['slave_flame_on'] == 1,
            status['slave_ch_active'] == 1
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


async def connect_and_subscribe():
    """Connect to the OpenTherm Gateway and subscribe to status updates."""

    # Create the object
    gw = pyotgw()

    # Connect to OpenTherm Gateway on PORT
    status = await gw.connect(asyncio.get_event_loop(), PORT)
    print("Initial status after connecting:\n{}".format(status))

    # Subscribe to updates from the gateway
    if not gw.subscribe(insert_status):
        print("Could not subscribe to status updates.")

    # Keep the event loop alive...
    while True:
        await asyncio.sleep(1)


# Set up the event loop and run the connect_and_subscribe coroutine.
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(connect_and_subscribe())
except KeyboardInterrupt:
    print("Exiting")
