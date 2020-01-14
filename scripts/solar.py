#!/usr/bin/env python3

# Script to scrape data from the inverter of the solar panel
# using a RS85 serial connection

from typing import Dict

import minimalmodbus
import psycopg2
import serial


def insert_pricing(measurement: Dict):
    sql = """
            INSERT INTO solar (
                ac_watt,
                dc_volt,
                dc_amps,
                ac_volts,
                ac_amps,
                ac_freq,
                temp
            )
            VALUES(
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )"""
    conn = None
    try:
        # read database configuration
        # connect to the PostgreSQL database
        conn = psycopg2.connect(
            host="192.168.1.123",
            database="fokko",
            user="fokko",
            password="fokko"
        )
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (
            measurement['ac_watt'],
            measurement['dc_volt'],
            measurement['dc_amps'],
            measurement['ac_volts'],
            measurement['ac_amps'],
            measurement['ac_freq'],
            measurement['temp']
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


def scale(value, scale):
    value = float(value) / scale
    return value


instrument = minimalmodbus.Instrument("/dev/serial0", 1)
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.parity = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 0.2
instrument.mode = minimalmodbus.MODE_RTU

fields = {
    "ac_watt": instrument.read_long(
        3004, functioncode=4, signed=False
    ),
    "dc_volt": scale(instrument.read_register(
        3021, number_of_decimals=0, functioncode=4, signed=False
    ), 10),
    "dc_amps": scale(instrument.read_register(
        3022, number_of_decimals=0, functioncode=4, signed=False
    ), 10),
    "ac_volts": scale(instrument.read_register(
        3035, number_of_decimals=0, functioncode=4, signed=False
    ), 10),
    "ac_amps": scale(instrument.read_register(
        3038, number_of_decimals=0, functioncode=4, signed=False
    ), 10),
    "ac_freq": scale(instrument.read_register(
        3042, number_of_decimals=0, functioncode=4, signed=False
    ), 100),
    "temp": scale(instrument.read_register(
        3004, number_of_decimals=0, functioncode=4, signed=True
    ), 10)
}

# {
#   'ac_watt': 18,
#   'dc_volt': 196.7,
#   'dc_amps': 0.1,
#   'ac_volts': 229.6,
#   'ac_amps': 0.3,
#   'ac_freq': 50.0,
#   'temp': 0.0
# }


insert_pricing(fields)
