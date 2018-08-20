#!/usr/bin/python
# -*- coding: utf-8 -*-

from datapackage_utilities import building, processing

# clean directories to avoid errors
processing.clean_datapackage()

# get config file
config = building.get_config()

# initialize directories etc. based on config file
building.initialize_dpkg()

# get the meta-data from the datapackage data files
building.metadata_from_data(directory='data', name='e-highway-X7-simple')

# run scripts to add data
import electricity_hubs
import electricity_excess
import electricity_shortage
import ehighway_capacities
import ehighway_grid
import electricity_load_profiles
import capacity_factors_pv
import capacity_factors_wind
import hydro_edge_parameters
# import run_of_river_profiles

import update_metadata
