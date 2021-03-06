# -*- coding: utf-8 -*-
"""
"""
import json
import pandas as pd

from datapackage_utilities import building

config = building.get_config()

def create_resource(path):
    from datapackage import Resource
    resource = Resource({'path': path})
    resource.infer()
    resource.descriptor['schema']['primaryKey'] = 'timeindex'
    resource.descriptor['description'] = 'PV profiles (capacity factors) from renewables ninja for each country'
    resource.descriptor['title'] = 'PV profiles'
    resource.descriptor['sources'] = [{
        'title': 'Renewables Ninja PV Capacity Factors',
        'path': 'https://www.renewables.ninja/static/downloads/ninja_europe_pv_v1.1.zip'}]
    resource.commit()

    if resource.valid:
        resource.save('resources/'+ resource.name + '.json')


filepath = building.download_data(
    "https://www.renewables.ninja/static/downloads/ninja_europe_pv_v1.1.zip",
    unzip_file='ninja_pv_europe_v1.1_merra2.csv')

year = str(config['weather_year'])

countries = config['countries']

raw_data = pd.read_csv(filepath, index_col=[0], parse_dates=True)

df = raw_data.loc[year][countries]

sequences_df = pd.DataFrame(index=df.index)

for c in df.columns:
    sequence_name = 'pv-' + c + '-profile'
    sequences_df[sequence_name] = df[c].values

sequences_df.index = building.timeindex()
path = building.write_sequences('generator-profiles.csv', sequences_df)

create_resource(path)
