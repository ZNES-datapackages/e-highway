# -*- coding: utf-8 -*-
"""
"""
import json

import pandas as pd

from datapackage_utilities import building

def create_resource(path):
    from datapackage import Resource
    resource = Resource({'path': path})
    resource.infer()
    resource.descriptor['schema']['primaryKey'] = 'timeindex'
    resource.descriptor['description'] = 'Demand profiles per country'
    resource.descriptor['title'] = 'Demand profiles'
    resource.descriptor['sources'] = [{
        'title': 'OPSD timeseries',
        'path': 'https://data.open-power-system-data.org/time_series/2017-07-09/' +
                'time_series_60min_singleindex.csv'}]
    resource.commit()

    if resource.valid:
        resource.save('resources/'+ resource.name + '.json')



config = building.get_config()

filepath = building.download_data(
    'https://data.open-power-system-data.org/time_series/2017-07-09/' +
    'time_series_60min_singleindex.csv')

raw_data = pd.read_csv(filepath, index_col=[0], parse_dates=True)

suffix = '_load_old'

year = str(config['demand_year'])

countries = config['countries']

columns = [c + suffix for c in countries]

timeseries = raw_data[year][columns]

demand_total = timeseries.sum()

demand_profile = timeseries / demand_total

sequences_df = pd.DataFrame(index=demand_profile.index)
elements = building.read_elements('demand.csv')
for c in countries:
    # get sequence name from elements edge_parameters (include re-exp to also
    # check for 'elec' or similar)
    sequence_name = elements.at[
            elements.index[elements.index.str.contains(c)][0],
            'profile']

    sequences_df[sequence_name] = demand_profile[c + suffix].values

sequences_df.index = building.timeindex()

path = building.write_sequences('demand-profiles.csv', sequences_df)

create_resource(path)
