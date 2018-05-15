# -*- coding: utf-8 -*-
"""
"""

from datapackage import Resource
import pandas as pd
from datapackage_utilities import building

def annuity(capex, n, wacc):
    """Calculate the annuity.

    annuity = capex * (wacc * (1 + wacc) ** n) / ((1 + wacc) ** n - 1)

    Parameters
    ----------
    capex : float
        Capital expenditure (NPV of investment)
    n : int
        Number of years that the investment is used (economic lifetime)
    wacc : float
        Weighted average cost of capital

    Returns
    -------
    float : annuity

    """
    return capex * (wacc * (1 + wacc) ** n) / ((1 + wacc) ** n - 1)


def create_resource_path(path):
    """
    """
    r = Resource({'path': path})
    r.infer()

    if 'storage' in r.name  or 'district-heat-demand' == r.name or 'boiler' in r.name:
        r.descriptor['schema']['foreignKeys'] =   [{
            "fields": "bus",
            "reference": {
                "resource": "bus",
                "fields": "name"}}]

    if 'backpressure' in r.name:
        r.descriptor['schema']['foreignKeys'] =   [
            {
            "fields": "electricity_bus",
            "reference": {
                "resource": "bus",
                "fields": "name"}
            },
            {
            "fields": "heat_bus",
            "reference": {
                "resource": "bus",
                "fields": "name"}
            },
            {
            "fields": "fuel_bus",
            "reference": {
                "resource": "bus",
                "fields": "name"}
            }]

    if 'power-to-heat' in r.name:
        r.descriptor['schema']['foreignKeys'] = [
            {
            "fields": "from_bus",
            "reference": {
                "resource": "bus",
                "fields": "name"}
            },
            {
            "fields": "to_bus",
            "reference": {
                "resource": "bus",
                "fields": "name"}
            }]

    if 'district-heat-demand' == r.name:
        r.descriptor['schema']['foreignKeys'].append({
            "fields": "profile",
            "reference": {
                "resource": "heat-demand-profiles"}})

    r.commit()
    r.save('resources/' + r.name + '.json')

config = building.get_config()


building.write_elements(
    'bus.csv',
    pd.DataFrame.from_dict({
        'DE-heat': {
            'type': 'bus',
            'balanced': True,
            'geometry': None
            },
        'GL-gas': {
            'type': 'bus',
            'balanced': False,
            'geometry': None
            }
        }, orient='index'))


investment_cost = {
    'heat-storage': annuity(capex=1000*1e3, n=20, wacc=0.05),
    'power-to-heat': annuity(capex=400*1e3, n=20, wacc=0.05),
    'gas-backpressure': annuity(capex=1000*1e3, n=20, wacc=0.05),
    'gas-boiler': annuity(capex=100*1e3, n=20, wacc=0.05)}

p2h_elements = {
    'p2h': {
        'type': 'conversion',
        'from_bus': 'DE-electricity',
        'to_bus': 'DE-heat',
        'tech': 'power-to-heat',
        'investment_cost': investment_cost['power-to-heat'],
        'capacity': None}}

path = building.write_elements(
    'power-to-heat.csv',
    pd.DataFrame.from_dict(p2h_elements, orient='index'))
create_resource_path(path)

backpressure = {
    'backpressure-DE': {
        'type': 'backpressure',
        'fuel_bus': 'GL-gas',
        'fuel_cost': 80,
        'electricity_bus': 'DE-electricity',
        'heat_bus': 'DE-heat',
        'thermal_efficiency': 0.4,
        'electric_efficiency': 0.4,
        'tech': 'gas-backpressure',
        'investment_cost': investment_cost['gas-backpressure'],
        'capacity': None}}

path = building.write_elements(
    'backpressure.csv',
    pd.DataFrame.from_dict(backpressure, orient='index'))
create_resource_path(path)

heat_storage = {
    'heat-storage-DE': {
        'type': 'storage',
        'bus': 'DE-heat',
        'tech': 'heat-storage',
        'efficiency': 1,
        'loss': 0.0,
        'ep_ratio': 1/6,
        'investment_cost': investment_cost['heat-storage'],
        'capacity': None}}

path = building.write_elements(
    'heat-storage.csv',
    pd.DataFrame.from_dict(heat_storage, orient='index'))
create_resource_path(path)

boiler = {
    'boiler-DE': {
        'type': 'generator',
        'bus': 'DE-heat',
        'tech': 'gas-boiler',
        'efficiency': 0.9,
        'marginal_cost': 80 / 0.9,
        'investment_cost': investment_cost['gas-boiler'],
        'profile': None,
        'capacity': None}}

path = building.write_elements(
    'boiler.csv',
    pd.DataFrame.from_dict(boiler, orient='index'))
create_resource_path(path)

district_heat_demand = {
    'district-heat-demand-DE': {
        'type': 'demand',
        'bus': 'DE-heat',
        'amount': 190 * 1e6, # 190.000.000 MWh i.e. 190 TWh
        'profile': 'district-heat-demand-DE-profile'}}

path = building.write_elements(
    'district-heat-demand.csv',
    pd.DataFrame.from_dict(district_heat_demand, orient='index'))
create_resource_path(path)


heat_demand_profile = pd.Series(
    data=pd.read_csv('archive/thermal_load_profile.csv', sep=";")['thermal_load'].values,
    index=pd.date_range(str(config['year']), periods=8760, freq='H'))
heat_demand_profile.rename('district-heat-demand-DE-profile', inplace=True)

path = building.write_sequences('heat-demand-profiles.csv', heat_demand_profile)
create_resource_path(path)
