# Fokko's Home analytics

This repository contains the code that runs Fokko's home automation. It consists of several modules that together
automate and monitor several things.

## APX

The APX (now called EPEX) module pulls the enery prices from
the [European marketplace](https://www.epexspot.com/en/market-data). So we know which prices we pay per hour for one
kWh. This is the raw price without any taxes or vat.

## Postgres

A docker container with a postgres database, including all the tables that will be bootstrapped. In today's world there
are many fancy databases, but often I prefer good ol' Postgres.

## Youless

A nifty device called [Youless LS120](https://www.youless.nl/winkel/product/ls120.html) to read the energy meter using
the P1 cable, and exposes a json interface to the network. This docker container will poll the json endpoint every hour.

## Relay

For opening-closing the relay to control the Smart Grid ready energy pumps.
