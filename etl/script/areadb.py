# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os

from ddf_utils.str import to_concept_id
from ddf_utils.index import create_index_file


# configuration of file path
data_file = '../source/GDL-AreaData200.csv'
desc_file = '../source/GDL-AreaData200-Variabledescription.csv'
out_dir = '../../'


def extract_entities_region(data):
    region = data[['GDLCODE', 'iso_code', 'ISO2', 'country', 'region', 'level']].drop_duplicates().copy()
    # Adding country name into region name
    region['region_name'] = region['country'] + ' - ' + region['region']
    # we use GDLCODE as concept id
    region['GDLCODE'] = region['GDLCODE'].apply(to_concept_id)

    # setting up the entity sets
    region['is--country'] = 0
    region['is--sub_nation'] = 0
    region['is--urb_rur'] = 0

    region.loc[region['level'] == 'National', 'is--country'] = 1
    region.loc[region['level'] == 'Subnat', 'is--sub_nation'] = 1
    region.loc[region['level'] == 'Urb/rur', 'is--urb_rur'] = 1

    region_ddf = region[['GDLCODE', 'region_name', 'iso_code', 'ISO2',
                         'is--country', 'is--sub_nation', 'is--urb_rur']].copy()

    region_ddf = region_ddf.rename(columns={'GDLCODE': 'region', 'region_name': 'name', 'ISO2': 'iso2'})

    return region_ddf


def extract_concepts(data, desc):
    # we use Variable column as concept ids
    desc['Variable'] = desc['Variable'].map(to_concept_id)
    desc = desc.drop(['Category'], axis=1)
    desc = desc.set_index('Variable')
    desc = desc.drop(['datasource', 'level'])

    # rename columns
    desc = desc.rename(index={'region': 'sub_nation', 'gdlcode': 'region'})
    desc.index.name = 'concept'
    desc.columns = ['name', 'longdescr']

    desc['concept_type'] = 'measure'

    # set some porperties manually
    desc.loc[['iso_code', 'iso2'], 'concept_type'] = 'string'
    desc.loc[['country', 'sub_nation'], 'concept_type'] = 'entity_set'
    desc.loc['region', 'concept_type'] = 'entity_domain'
    desc.loc['year', 'concept_type'] = 'time'

    desc = desc.reset_index()

    desc = desc.append(pd.DataFrame([['domain', 'Domain', '', 'string'],
                                     ['drillups', 'Drill up', '', 'string'],
                                     ['longdescr', 'longer description', '', 'string'],
                                     ['urb_rur', 'Urban/Rural Regions', '', 'entity_set'],
                                     ['name', 'Name', '', 'string']
                                     ], columns=desc.columns))

    # only keep the measure type concepts which are in data file.
    desc = desc.set_index('concept')
    dps = data.copy()
    dps.columns = list(map(to_concept_id, dps.columns))
    measures = desc[desc['concept_type'] == 'measure'].index

    idx1 = desc.ix[desc['concept_type'] != 'measure'].index
    idx2 = dps.columns[8:]  # measures are after column 8
    idx = np.r_[idx1, idx2]

    desc = desc.ix[idx]

    for i in list(set(dps.columns[8:]).difference(set(measures))):
        desc.loc[i, 'concept_type'] = 'measure'

    # fill other columns
    desc['drillups'] = np.nan

    desc.loc[['sub_nation', 'urb_rur'], 'drillups'] = 'country'
    desc.loc['country', 'drillups'] = 'region'

    desc['domain'] = np.nan

    desc.loc[['sub_nation', 'urb_rur', 'country'], 'domain'] = 'region'

    return desc.reset_index().sort_values(by='concept_type')


def extract_datapoints(data):
    dps = data.copy()
    dps.columns = list(map(to_concept_id, dps.columns))
    dps = dps.rename(columns={ 'region': 'sub_nation', 'gdlcode': 'region'})

    dps = dps[['year', 'region', *dps.columns[8:]]]
    dps['region'] = dps['region'].map(to_concept_id)
    dps = dps.set_index(['year', 'region'])

    for k, df in dps.items():
        df.columns = [k]
        df = df.dropna()
        df = df.reset_index()

        yield k, df


if __name__ == '__main__':
    print('reading source files...')
    data = pd.read_csv(data_file, encoding='iso-8859-1', skipinitialspace=True)
    desc = pd.read_csv(desc_file, encoding='iso-8859-1')

    print('creating entities files...')
    region = extract_entities_region(data)
    path = os.path.join(out_dir, 'ddf--entities--region.csv')
    region.to_csv(path, index=False)

    print('creating concept files...')
    concepts = extract_concepts(data, desc)
    path = os.path.join(out_dir, 'ddf--concepts.csv')
    concepts.to_csv(path, index=False)

    print('creating datapoints files...')
    for k, df in extract_datapoints(data):
        path = os.path.join(out_dir, 'ddf--datapoints--{}--by--region--year.csv'.format(k))
        df.to_csv(path, index=False)

    print('creating index file...')
    create_index_file(out_dir)

    print('Done.')


