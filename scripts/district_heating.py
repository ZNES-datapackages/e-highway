# -*- coding: utf-8 -*-
"""
"""
import pandas as pd
from datapackage_utilities import building

# TODO:
# Add: Heat bus, fuel bus, investment costs, heat profile
investment_cost = {
    'heat-storage': 1000,
    'power-to-heat': 1000,
    'gas-backpressure': 1000,
    'gas-boiler': 1000}

p2h_elements = {
    'p2h': {
        'type': 'conversion',
        'bus': 'DE-heat',
        'tech': 'power-to-heat',
        'investment_cost': investment_cost['power-to-heat'],
        'capacity': None}}

building.write_elements(
    'power-to-heat.csv',
    pd.DataFrame.from_dict(p2h_elements, orient='index'))

backpressure = {
    'backpressure-DE': {
        'type': 'backpressure',
        'fuel_bus': 'DE-heat',
        'electricity_bus': 'DE-electricity',
        'heat_bus': 'DE-heat',
        'tech': 'gas-backpressure',
        'investment_cost': investment_cost['gas-backpressure'],
        'capacity': None}}

building.write_elements(
    'backpressure.csv',
    pd.DataFrame.from_dict(backpressure, orient='index'))

heat_storage = {
    'heat-storage-DE': {
        'type': 'heat_storage',
        'bus': 'DE-heat',
        'tech': 'heat-storage',
        'efficiency': 1,
        'loss': 0.05,
        'investment_cost': investment_cost['heat-storage'],
        'capacity': None}}

building.write_elements(
    'heat-storage.csv',
    pd.DataFrame.from_dict(heat_storage, orient='index'))

boiler = {
    'boiler-DE': {
        'type': 'generator',
        'bus': 'DE-heat',
        'tech': 'gas-boiler',
        'efficiency': 0.9,
        'investment_cost': investment_cost['gas-boiler'],
        'profile': None,
        'capacity': None}}

building.write_elements(
    'boiler.csv',
    pd.DataFrame.from_dict(boiler, orient='index'))

district_heat_demand = {
    'district-heat-demand-DE': {
        'type': 'demand',
        'bus': 'DE-heat',
        'amount': 190 * 1e6, # 190.000.000 MWh i.e. 190 TWh
        'profile': 'district-heat-demand-DE-profile'}}

building.write_elements(
    'district-heat-demand.csv',
    pd.DataFrame.from_dict(district_heat_demand, orient='index'))
