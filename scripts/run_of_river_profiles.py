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
    resource.descriptor['description'] = (
        'Profiles for Run of River (ROR) components. The profile is assumed' +
        ' to be constant during the year.')
    resource.descriptor['title'] = 'ROR profiles'
    resource.descriptor['sources'] = [{
        'title': 'Assumption'}]
    resource.commit()

    if resource.valid:
        resource.save('resources/'+ resource.name + '.json')

year = str(config['weather_year'])

countries = config['countries']

sequences_df = pd.DataFrame(index=building.timeindex())

elements = building.read_elements('run-of-river.csv')
for c in countries:
    # get sequence name from elements edge_parameters (include re-exp to also
    # check for 'elec' or similar)
    sequence_name = elements.at[
            elements.index[elements.index.str.contains(c)][0],
            'profile']

    sequences_df[sequence_name] = 0.65

sequences_df.index = building.timeindex()

path = building.write_sequences('ror-profiles.csv', sequences_df)

create_resource(path)
