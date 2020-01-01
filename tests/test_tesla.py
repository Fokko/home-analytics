import sys

sys.path.append("..")

from tesla.poll import determine_slots, optimize
from datetime import datetime


def test_determine_slots():
    assert (determine_slots(
        datetime(year=2020, month=1, day=1, hour=20),
        22,  # We want to charge 22 kwh
        5.0,  # We charge 5 kwh
        [
            (datetime(year=2020, month=1, day=1, hour=20), 0.1),
            (datetime(year=2020, month=1, day=1, hour=21), 0.1),
            (datetime(year=2020, month=1, day=1, hour=22), 0.1),
            (datetime(year=2020, month=1, day=2, hour=23), 0.1),
            (datetime(year=2020, month=1, day=2, hour=0), 0.2),
            (datetime(year=2020, month=1, day=2, hour=1), 0.5),
            (datetime(year=2020, month=1, day=2, hour=2), 0.6)
        ]
    ))


def test_determine_slots_now_expensive():
    assert (determine_slots(
        datetime(year=2020, month=1, day=1, hour=20),
        22,  # We want to charge 22 kwh
        5.0,  # We charge 5 kwh
        [
            (datetime(year=2020, month=1, day=1, hour=20), 0.6),  # Right now it is rather expensive
            (datetime(year=2020, month=1, day=1, hour=21), 0.4),
            (datetime(year=2020, month=1, day=1, hour=22), 0.1),
            (datetime(year=2020, month=1, day=1, hour=23), 0.1),
            (datetime(year=2020, month=1, day=2, hour=0), 0.1),
            (datetime(year=2020, month=1, day=2, hour=1), 0.2),
            (datetime(year=2020, month=1, day=2, hour=2), 0.5),
            (datetime(year=2020, month=1, day=2, hour=3), 0.6)
        ]
    ) is False)  # Right now we don't want to charge


def test_optimize_connected():
    assert (optimize(
        datetime(year=2020, month=1, day=1, hour=20),
        {'battery_heater_on': False,
         'battery_level': 85,
         'battery_range': 193.06,
         'charge_current_request': 16,
         'charge_current_request_max': 16,
         'charge_enable_request': True,
         'charge_energy_added': 41.13,
         'charge_limit_soc': 90,
         'charge_limit_soc_max': 100,
         'charge_limit_soc_min': 50,
         'charge_limit_soc_std': 90,
         'charge_miles_added_ideal': 188.0,
         'charge_miles_added_rated': 188.0,
         'charge_port_cold_weather_mode': False,
         'charge_port_door_open': False,
         'charge_port_latch': 'Engaged',
         'charge_rate': 0.0,
         'charge_to_max_range': False,
         'charger_actual_current': 0,
         'charger_phases': 3,
         'charger_pilot_current': 16,
         'charger_power': 0,
         'charger_voltage': 230,
         'charging_state': 'Connected',
         'conn_charge_cable': '<invalid>',
         'est_battery_range': 157.35,
         'fast_charger_brand': '<invalid>',
         'fast_charger_present': False,
         'fast_charger_type': '<invalid>',
         'ideal_battery_range': 193.06,
         'managed_charging_active': False,
         'managed_charging_start_time': None,
         'managed_charging_user_canceled': False,
         'max_range_charge_counter': 0,
         'minutes_to_full_charge': 0,
         'not_enough_power_to_heat': None,
         'scheduled_charging_pending': False,
         'scheduled_charging_start_time': None,
         'time_to_full_charge': 0.0,
         'timestamp': 1577902337788,
         'trip_charging': False,
         'usable_battery_level': 85,
         'user_charge_enable_request': None},
        [
            (datetime(year=2020, month=1, day=1, hour=20), 0.1)
        ]
    ))


def test_optimize_disconnected():
    assert (optimize(
        datetime(year=2020, month=1, day=1, hour=20),
        {'battery_heater_on': False,
         'battery_level': 85,
         'battery_range': 193.06,
         'charge_current_request': 16,
         'charge_current_request_max': 16,
         'charge_enable_request': True,
         'charge_energy_added': 41.13,
         'charge_limit_soc': 90,
         'charge_limit_soc_max': 100,
         'charge_limit_soc_min': 50,
         'charge_limit_soc_std': 90,
         'charge_miles_added_ideal': 188.0,
         'charge_miles_added_rated': 188.0,
         'charge_port_cold_weather_mode': False,
         'charge_port_door_open': False,
         'charge_port_latch': 'Engaged',
         'charge_rate': 0.0,
         'charge_to_max_range': False,
         'charger_actual_current': 0,
         'charger_phases': None,
         'charger_pilot_current': 16,
         'charger_power': 0,
         'charger_voltage': 2,
         'charging_state': 'Disconnected',
         'conn_charge_cable': '<invalid>',
         'est_battery_range': 157.35,
         'fast_charger_brand': '<invalid>',
         'fast_charger_present': False,
         'fast_charger_type': '<invalid>',
         'ideal_battery_range': 193.06,
         'managed_charging_active': False,
         'managed_charging_start_time': None,
         'managed_charging_user_canceled': False,
         'max_range_charge_counter': 0,
         'minutes_to_full_charge': 0,
         'not_enough_power_to_heat': None,
         'scheduled_charging_pending': False,
         'scheduled_charging_start_time': None,
         'time_to_full_charge': 0.0,
         'timestamp': 1577902337788,
         'trip_charging': False,
         'usable_battery_level': 85,
         'user_charge_enable_request': None},
        []
    ) is False)


def test_optimize_charging():
    assert (optimize(
        datetime(year=2020, month=1, day=1, hour=20),
        {'battery_heater_on': False,
         'battery_level': 13,
         'battery_range': 28.67,
         'charge_current_request': 16,
         'charge_current_request_max': 16,
         'charge_enable_request': True,
         'charge_energy_added': 4.08,
         'charge_limit_soc': 100,
         'charge_limit_soc_max': 100,
         'charge_limit_soc_min': 50,
         'charge_limit_soc_std': 90,
         'charge_miles_added_ideal': 18.5,
         'charge_miles_added_rated': 18.5,
         'charge_port_cold_weather_mode': False,
         'charge_port_door_open': True,
         'charge_port_latch': 'Engaged',
         'charge_rate': 30.1,
         'charge_to_max_range': True,
         'charger_actual_current': 16,
         'charger_phases': 2,
         'charger_pilot_current': 16,
         'charger_power': 7,
         'charger_voltage': 233,
         'charging_state': 'Charging',
         'conn_charge_cable': 'IEC',
         'est_battery_range': 23.86,
         'fast_charger_brand': '<invalid>',
         'fast_charger_present': False,
         'fast_charger_type': '<invalid>',
         'ideal_battery_range': 28.67,
         'managed_charging_active': False,
         'managed_charging_start_time': None,
         'managed_charging_user_canceled': False,
         'max_range_charge_counter': 0,
         'minutes_to_full_charge': 410,
         'not_enough_power_to_heat': None,
         'scheduled_charging_pending': False,
         'scheduled_charging_start_time': None,
         'time_to_full_charge': 6.83,
         'timestamp': 1578144420847,
         'trip_charging': False,
         'usable_battery_level': 13,
         'user_charge_enable_request': None},
        [
            (datetime(year=2020, month=1, day=1, hour=20), 0.1),
            (datetime(year=2020, month=1, day=1, hour=21), 0.1),
            (datetime(year=2020, month=1, day=1, hour=22), 0.1),
            (datetime(year=2020, month=1, day=2, hour=23), 0.1),
            (datetime(year=2020, month=1, day=2, hour=0), 0.2),
            (datetime(year=2020, month=1, day=2, hour=1), 0.5),
            (datetime(year=2020, month=1, day=2, hour=2), 0.6)
        ]
    ) is False)
