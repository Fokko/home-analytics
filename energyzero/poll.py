import logging
import time
from abc import ABC, abstractmethod
from dataclasses import astuple, dataclass
from datetime import datetime
from typing import List

import psycopg2
import requests

# Wait until postgres is up
time.sleep(1)

import os

token = os.environ["TOKEN"]


class Usage(ABC):
    usage: int
    sql: str

    def fetch_json(self):
        return requests.get(
            f"https://api.energyzero.nl/v1/cost/?dateFrom=2010-01-01T00:00:00.000Z&dateTill=2030-10-31T23:00:00.000Z&intervalType=3&snapshotID=18420d3c-993b-427b-89fe-db348607301c&usageType={self.usage}&calculationDetails=true",
            headers={
                "authority": "api.energyzero.nl",
                "accept": "application/json, text/plain, */*",
                "x-auth": f"Bearer {token}",
            },
        ).json()

    def write_results(self, prices: List):
        logging.info("Writing %s lines", len(prices))
        conn = None
        try:
            # read database configuration
            # connect to the PostgreSQL database
            conn = psycopg2.connect(host="postgres", database="fokko", user="fokko", password="fokko")
            # create a new cursor
            cur = conn.cursor()
            for price in prices:
                # execute the INSERT statement
                cur.execute(self.sql, astuple(price))
            # commit the changes to the database
            conn.commit()
            # close communication with the database
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

    @abstractmethod
    def fetch(self):
        pass


@dataclass
class EnergyMeasurement:
    date_measured: datetime
    epex_price: float
    energy_tax: float
    trade_cost: float
    ode_tax: float
    network_cost: float
    delivery_cost: float
    deduction_tax: float
    kwh_used: float
    kwh_price: float


class EnergyUsage(Usage):
    usage = 1
    sql = """
        INSERT INTO energy_usage (
            date_measured,
            epex_price,
            energy_tax,
            trade_cost,
            ode_tax,
            network_cost,
            delivery_cost,
            deduction_tax,
            kwh_used,
            kwh_price
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
            %s
        )
        ON CONFLICT (date_measured)
        DO NOTHING;"""

    # {
    #     "business": false,
    #     "id": "00000000-0000-0000-0000-000000000000",
    #     "interval_type": 3,
    #     "reading_date": "2020-10-05T22:00:00+02:00",
    #     "total_excl": 0.0221143744292238,
    #     "total_per_setting": {
    #         "Dagprijs EPEX per kWh": "0.008112",
    #         "Energiebelasting per kWh": "0.025402",
    #         "Inkoopkosten per kWh": "0.00143",
    #         "Netbeheerkosten stroom": "0.02415",
    #         "ODE per kWh": "0.007098",
    #         "Vaste leveringskosten": "0.0056575342465754",
    #         "Vermindering Energiebelasting": "-0.0497351598173516"
    #     },
    #     "unit_price": 0.0312,
    #     "usage": 0.26,
    #     "usage_type": 1
    # },

    def fetch(self):
        prices = self.fetch_json()
        parsed_price = list()
        for price in prices:
            # Strip the timezone of 2020-09-25T00:00:00+02:00
            raw_date = price.get("reading_date").split("+")[0]
            date = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S")
            usage = price.get("total_per_setting")

            logging.info("Got a Energy reading at %s", date)

            # Prices per interval, so not per kwh as the name suggests
            parsed_price.append(
                EnergyMeasurement(
                    date,
                    float(usage.get("Dagprijs EPEX per kWh")),
                    float(usage.get("Energiebelasting per kWh")),
                    float(usage.get("Inkoopkosten per kWh")),
                    float(usage.get("ODE per kWh")),
                    float(usage.get("Netbeheerkosten stroom")),
                    float(usage.get("Vaste leveringskosten")),
                    float(usage.get("Vermindering Energiebelasting")),
                    float(price.get("usage")),
                    float(price.get("unit_price")),
                )
            )
        self.write_results(parsed_price)


@dataclass
class SunMeasurement:
    date_measured: datetime
    epex_price: float
    energy_tax: float
    trade_cost: float
    ode_tax: float
    kwh_used: float
    kwh_price: float


class SunUsage(Usage):
    usage = 2
    sql = """
         INSERT INTO solar_production (
             date_measured,
             epex_price,
             energy_tax,
             trade_cost,
             ode_tax,
             kwh_used,
             kwh_price
         )
         VALUES(
             %s,
             %s,
             %s,
             %s,
             %s,
             %s,
             %s
         )
         ON CONFLICT (date_measured)
         DO NOTHING;"""

    # {
    #     "business": false,
    #     "id": "00000000-0000-0000-0000-000000000000",
    #     "interval_type": 3,
    #     "reading_date": "2020-10-05T17:00:00+02:00",
    #     "total_excl": 0.00017194,
    #     "total_per_setting": {
    #         "Dagprijs EPEX per kWh": "0.00004144",
    #         "Energiebelasting per kWh": "0.0000977",
    #         "Inkoopkosten per kWh": "0.0000055",
    #         "ODE per kWh": "0.0000273"
    #     },
    #     "unit_price": 0.04144,
    #     "usage": 0.001,
    #     "usage_type": 2
    # },

    def fetch(self):
        prices = self.fetch_json()
        parsed_prices = list()
        for price in prices:
            # Strip the timezone of 2020-09-25T00:00:00+02:00
            raw_date = price.get("reading_date").split("+")[0]
            date = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S")
            usage = price.get("total_per_setting")

            logging.info("Got a Sun reading at %s", date)

            # Prices per interval, so not per kwh as the name suggests
            parsed_prices.append(
                SunMeasurement(
                    date,
                    float(usage.get("Dagprijs EPEX per kWh")),
                    float(usage.get("Energiebelasting per kWh")),
                    float(usage.get("Inkoopkosten per kWh")),
                    float(usage.get("ODE per kWh")),
                    float(price.get("usage")),
                    float(price.get("unit_price")),
                )
            )
        self.write_results(parsed_prices)


@dataclass
class GasMeasurement:
    date_measured: datetime
    leba_price: float
    energy_tax: float
    trade_cost: float
    network_cost: float
    ode_tax: float
    region_tax: float
    delivery_cost: float
    m3_used: float
    m3_price: float


class GasUsage(Usage):
    usage = 3
    sql = """
         INSERT INTO gas_usage (
             date_measured,
             leba_price,
             energy_tax,
             trade_cost,
             network_cost,
             ode_tax,
             region_tax,
             delivery_cost,
             kwh_used,
             kwh_price
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
             %s
         )
         ON CONFLICT (date_measured)
         DO NOTHING;"""

    # {
    #     "business": false,
    #     "id": "00000000-0000-0000-0000-000000000000",
    #     "interval_type": 3,
    #     "reading_date": "2020-10-05T22:00:00+02:00",
    #     "total_excl": 0.0610705448839754,
    #     "total_per_setting": {
    #         "Dagprijs LEBA per m³": "0.0073598106374",
    #         "Energiebelasting per m³": "0.02164955",
    #         "Inkoopkosten per m³": "0.0012441",
    #         "Netbeheerkosten gas": "0.01885",
    #         "ODE per m³": "0.0050375",
    #         "Regiotoeslag per m³": "0.00127205",
    #         "Vaste leveringskosten": "0.0056575342465754"
    #     },
    #     "unit_price": 0.11322785596,
    #     "usage": 0.065,
    #     "usage_type": 3
    # },

    def fetch(self):
        prices = self.fetch_json()
        parsed_price = list()
        for price in prices:
            # Strip the timezone of 2020-09-25T00:00:00+02:00
            raw_date = price.get("reading_date").split("+")[0]
            date = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S")
            usage = price.get("total_per_setting")

            logging.info("Got a Gas reading at %s", date)

            # Prices per interval, so not per kwh as the name suggests
            parsed_price.append(
                GasMeasurement(
                    date,
                    float(usage.get("Dagprijs LEBA per m³")),
                    float(usage.get("Energiebelasting per m³")),
                    float(usage.get("Inkoopkosten per m³")),
                    float(usage.get("Netbeheerkosten gas")),
                    float(usage.get("ODE per m³")),
                    float(usage.get("Regiotoeslag per m³")),
                    float(usage.get("Vaste leveringskosten")),
                    float(price.get("usage")),
                    float(price.get("unit_price")),
                )
            )
        self.write_results(parsed_price)


for usage in {EnergyUsage(), SunUsage(), GasUsage()}:
    # Fetch each category
    usage.fetch()
