import psycopg2
import requests

base_address = "http://192.168.1.245/"


def readings():
    output = requests.get(url=f"{base_address}e?f=j")
    reading_numbers = output.json()[0]

    output = requests.get(url=f"{base_address}f?c=2")
    reading_voltage_current_load = output.json()

    sql = """
            INSERT INTO youless_readings (
                net_counter,
                power,
                consumption_high,
                consumption_low,
                production_high,
                production_low,

                tarrif,

                current_phase_1,
                current_phase_2,
                current_phase_3,

                voltage_phase_1,
                voltage_phase_2,
                voltage_phase_3,

                load_phase_1,
                load_phase_2,
                load_phase_3
            )
            VALUES(
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,

                %s,

                %s,
                %s,
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
        conn = psycopg2.connect(host="postgres", database="postgres", user="postgres", password="postgres")
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(
            sql,
            (
                reading_numbers["net"],
                reading_numbers["pwr"],
                reading_numbers["p1"],
                reading_numbers["p2"],
                reading_numbers["n1"],
                reading_numbers["n2"],
                reading_voltage_current_load["tr"],
                reading_voltage_current_load["i1"],
                reading_voltage_current_load["i2"],
                reading_voltage_current_load["i3"],
                reading_voltage_current_load["v1"],
                reading_voltage_current_load["v2"],
                reading_voltage_current_load["v3"],
                reading_voltage_current_load["l1"],
                reading_voltage_current_load["l2"],
                reading_voltage_current_load["l3"],
            ),
        )
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


readings()
