""" Build power generation timeseries with Atlite (https://github.com/FRESNA/atlite/)
"""

import os
import atlite
import pandas as pd
from datapackage_utilities import building, geometry

config = building.get_config()

# nuts0 for european countries
filepath = os.path.join(config['directories']['cache'], 'NUTS_2013_10M_SH/data/NUTS_RG_10M_2013.shp')
nuts0 = pd.Series(geometry.nuts(filepath, nuts=0)).filter(config['countries'])

filepath = building.download_data(
    'sftp://atlite.openmod.net/home/atlite/cutouts/eu-2014.zip', unzip_file='eu-2014/')

cutout = atlite.Cutout(name='eu-2014/', cutout_dir=config['directories']['cache'])

trans_matrix = geometry.Shapes2Shapes(nuts0.values, cutout.grid_cells())
darrays = {}


def mkindex(pre):  # convenience function
    wrap = lambda x: '-'.join([pre, x, 'profile'])
    return list(map(wrap, nuts0.keys()))

darrays['wind'] = cutout.wind(
    matrix=trans_matrix.T, index=mkindex('wind'),
    turbine=config['windturbine_onshore'])
darrays['solar'] = cutout.pv(
    matrix=trans_matrix.T, index=mkindex('solar'), panel=config['solarpanel'],
    orientation='latitude_optimal')
darrays['ror'] = cutout.runoff(matrix=trans_matrix.T, index=mkindex('ror'))

for name, da in darrays.items():
    df = da.T.to_pandas()
    building.write_sequences(name + '-profiles.csv', df)
