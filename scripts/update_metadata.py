# -*- coding: utf-8 -*-
"""
"""
import os
from datapackage import Package, Resource

p = Package('datapackage.json')

p.descriptor['profile'] = 'tabular-data-package'

for f in os.listdir('resources'):
    path = os.path.join('resources', f)

    r = Resource(path)

    p.add_resource(r.descriptor)

    p.commit()

    os.remove(path)

os.rmdir('resources')

p.save('datapackage.json')
