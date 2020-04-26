# Fokko's Home analytics

This repository contains the code that runs Fokko's home automation. It consists of several modules that together automate and monitor several things.

## APX

The APX (now called EPEX) module pulls the enery prices from the [European marketplace](https://www.epexspot.com/en/market-data). So we know which prices we pay per hour for one kWh. This is the raw price without any taxes or vat.

## Charge-bot

The charge-bot is a [Telegram](https://telegram.org/) integration to let the Tesla charge on a schema. For example, when I come home after a day on the road, I can enable the charging schema using the Telegram bot, and it will tell me when it will charge:

```
+---------------------+-------------+---------------+---------------+
| Slot start          |   Price kwh | Est. Charge   |   Total price |
|---------------------+-------------+---------------+---------------|
| 2020-04-25 22:00:00 |    0.182335 | 0.0 kwh       |      0        |
| 2020-04-25 23:00:00 |    0.178003 | 0.0 kwh       |      0        |
| 2020-04-26 00:00:00 |    0.177507 | 0.0 kwh       |      0        |
| 2020-04-26 01:00:00 |    0.174663 | 11.04 kwh     |      1.92829  |
| 2020-04-26 02:00:00 |    0.175728 | 0.0 kwh       |      0        |
| 2020-04-26 03:00:00 |    0.175571 | 5.38 kwh      |      0.944572 |
| 2020-04-26 04:00:00 |    0.177507 | 0.0 kwh       |      0        |
| 2020-04-26 05:00:00 |    0.176442 | 0.0 kwh       |      0        |
| 2020-04-26 06:00:00 |    0.173127 | 11.04 kwh     |      1.91132  |
| 2020-04-26 07:00:00 |    0.17234  | 11.04 kwh     |      1.90264  |
+---------------------+-------------+---------------+---------------+
```

This is an example for my Tesla Model 3 with a battery capacity of 50 kWh.

## OTGW

OTGW stands for Open-Therm gateway and is a network connected gateway that sniffs the open therm protocol between the heater and the thermostat.

## Postgres

A docker container with a postgres database, including all the tables that will be bootstrapped. In today's world there are many fancy databases, but often I prefer good ol' Postgres.

## Tesla

The Tesla integration, which will poll the battery status, and switch the charging on/off based on the schedule.

## Youless

A nifty device called [Youless LS120](https://www.youless.nl/winkel/product/ls120.html) to read the energy meter using the P1 cable, and exposes a json interface to the network. This docker container will poll the json endpoint every hour.
