# -*- coding: utf-8 -*-
"""
"""
import json
import os

from datapackage import Package, Resource
import pandas as pd

from datapackage_utilities import building


def create_resource(path):
    """
    """

    mapper = {}

    from datapackage import Resource
    resource = Resource({'path': path})
    resource.infer()
    resource.descriptor['schema']['primaryKey'] = 'name'
    resource.descriptor['description'] = 'Installed capacities, costs and technical parameters for components'
    resource.descriptor['title'] = '{} components'.format(resource.name.title())
    resource.descriptor['sources'] = [{
        'title': 'E-Highway 2050 installed capacities',
        'path': 'http://www.e-highway2050.eu/fileadmin/documents/Results/e-Highway2050_2050_Country_and_cluster_installed_capacities_31-03-2015.xlsx'}]


    resource.descriptor['schema']['foreignKeys'] =   [{
        "fields": "bus",
        "reference": {
            "resource": "bus",
            "fields": "name"}}]


    if 'demand' in resource.name:
        resource.descriptor['schema']['foreignKeys'] .append({
            "fields": "profile",
            "reference": {
                "resource": "demand-profiles"}})

    elif 'volatile-generator' in resource.name:
        resource.descriptor['schema']['foreignKeys'] .append({
            "fields": "profile",
            "reference": {
                "resource": "generator-profiles"}})



    resource.commit()

    if resource.valid:
        resource.save('resources/'+ resource.name + '.json')
    else:
        print('Resource is not valid, writing resource anyway...')
        resource.save('resources/'+ resource.name + '.json')



config = building.get_config()

filepath = building.download_data(
    'http://www.e-highway2050.eu/fileadmin/documents/Results/'  +
    'e-Highway2050_2050_Country_and_cluster_installed_capacities_31-03-2015.xlsx')

df = pd.read_excel(filepath, sheet_name='Country_X-7', index_col=[0])

df = df.loc[config['countries']]

marginal_cost = {
    'reservoir': 0,
    'octg': 130,
    'biomass': 80
}

volatile_mapper = {
    'Wind (MW)': 'wind',
    'PV (MW)': 'pv'}

dispatchable_mapper = {
    'OCGT, CCGT without CCS, other peaking units (MW)': 'octg',
    'TOTAL biomass (MW)': 'biomass'}

ror_mapper = {
    'RoR (MW)': 'run-of-river'}

storage_mapper = {
    'PSP (MW)': 'pumped-storage'}

reservoir_mapper = {
    'Hydro with reservoir (MW)': 'reservoir'}

demand_mapper = {
    'Demand (GWh)': 'demand'}

types = ['volatile-generator', 'dispatchable-generator', 'pumped-storage',
         'reservoir', 'run-of-river', 'demand']

mappers = dict(zip(types,
                   [volatile_mapper, dispatchable_mapper, storage_mapper,
                    reservoir_mapper, ror_mapper, demand_mapper]))

element_dfs = dict(zip(types,
                       [building.read_elements('volatile-generator.csv'),
                        building.read_elements('dispatchable-generator.csv'),
                        building.read_elements('pumped-storage.csv'),
                        building.read_elements('reservoir.csv'),
                        building.read_elements('run-of-river.csv'),
                        building.read_elements('demand.csv')]))

elements = dict(zip(types, [{}, {}, {}, {}, {}, {}]))


for country in df.index:
    for element_type, mapper in mappers.items():
        for tech_key, tech in mapper.items():
            element_name = tech + '-' + country

            if element_name in element_dfs[element_type].index:
                raise ValueError(('Element with name {}' +
                                  ' already exists!').format(element_name))

            if element_type == 'volatile-generator':
                sequence_name = element_name + '-profile'

                elements[element_type][element_name] = {
                    'type': 'generator',
                    'bus': country + '-electricity',
                    'tech': tech,
                    'dispatchable': False,
                    'capacity': round(df.at[country, tech_key], 4),
                    'profile':  sequence_name}

            elif element_type == 'run-of-river':
                sequence_name = element_name + '-profile'

                elements[element_type][element_name] = {
                    'type': 'generator',
                    'bus': country + '-electricity',
                    'dispatchable': True,
                    'tech': tech,
                    'capacity': round(df.at[country, tech_key], 4)}


            elif element_type == 'dispatchable-generator':
                # set restriction on maximal production of biomass units 
                if tech == 'biomass':
                    edge_parameters = json.dumps({'summed_max': 3500})
                else:
                    edge_parameters = json.dumps({})

                elements[element_type][element_name] = {
                    'type': 'generator',
                    'tech': tech,
                    'bus': country + '-electricity',
                    'marginal_cost': marginal_cost[tech],
                    'edge_parameters': edge_parameters,
                    'capacity': round(df.at[country, tech_key], 4)}

            elif element_type == 'pumped-storage':
                if df.at[country, tech_key] > 0:
                    elements[element_type][element_name] = {
                        'type': 'storage',
                        'tech': tech,
                        'bus': country + '-electricity',
                        'marginal_cost': 0,
                        'efficiency': 0.8,
                        'loss': 0,
                        'power': df.at[country, tech_key],
                        'capacity': df.at[country, 'PSP reservoir (GWh)'] * 1000}

            elif element_type == 'reservoir':
                elements[element_type][element_name] = {
                    'type': 'generator',
                    'tech': tech,
                    'bus': country + '-electricity',
                    'capacity': df.at[country, tech_key],
                    'dispatchable': True,
                    'marginal_cost': marginal_cost['reservoir']}

            elif element_type == 'demand':
                sequence_name = element_name + '-profile'

                elements[element_type][element_name] = {
                    'type': 'demand',
                    'tech': tech,
                    'bus': country + '-electricity',
                    'amount': round(df.at[country, tech_key], 4) * 1000,
                    'profile':  sequence_name}

for element_type in element_dfs:
    path = building.write_elements(
            element_type + '.csv',
            pd.DataFrame.from_dict(elements[element_type], orient='index'))
    create_resource(path)
