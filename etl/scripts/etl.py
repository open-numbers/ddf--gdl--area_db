# 

# %%
import pandas as pd
import numpy as np
import os

from ddf_utils.str import to_concept_id
# %%
# configuration of file path
data_file = '../source/GDL-AreaData402 (1).csv'
desc_file = '../source/GDL-AreaData401-Variabledescription (1).csv'
out_dir = '../../'

# %%
data = pd.read_csv(data_file, encoding='iso-8859-1', skipinitialspace=True)
desc = pd.read_csv(desc_file, encoding='iso-8859-1')
# %%
data.head()
# %%
desc.head()
# %%
desc = desc.dropna(how='all', axis=1)
# %%
desc
# %%
desc['Unnamed: 14'].dropna()
# out: 145    shdix healthindx incindx edindx lifexpx lgnicx...
# %%
# Not sure what that means, drop that
desc = desc.drop(columns=['Unnamed: 14'])
# %%
desc
# %%
desc['Dtype'].unique()
# %%
desc[desc['Dtype'] == 'Pos']
# %%
data['eyem'].head()
# %%
# treat Pos as float then
# %%
# datapoints
# %%
data['level'].unique()
# %%
data[data.level == 'Wealth quartiles'].head()
# %%
data.columns.tolist()
# %%
# create entities
# %%
ents = data[['iso_code', 'ISO2', 'iso_num', 'country', 'GDLCODE', 'level', 'region']].copy()
# %%
ents
# %%
ents = ents.drop_duplicates(subset=['GDLCODE'])
# %%
ents
# %%
ents.level.unique()
# %%
# national
nat = ents[ents['level'] == 'National'].copy()
# %%
nat = nat.set_index('GDLCODE')
# %%
nat.columns = ['iso_code', 'iso2', 'iso_num', 'name', 'level', 'region']
# %%
nat = nat.drop(columns=['level', 'region'])

# %%
nat['is--national'] = 'TRUE'
# %%
nat['iso_num'] = nat['iso_num'].map(lambda x: str(int(x)) if not pd.isnull(x) else '')
# %%
nat['national'] = nat.index.map(to_concept_id)
# %%
nat.index.name = 'gdlcode'
# %%
nat = nat.reset_index().set_index('national')
# %%
nat
# %%
nat.to_csv('../../ddf--entities--level--national.csv')
# %%
# Subnat
subnat = ents[ents.level == 'Subnat']
# %%
subnat = subnat.set_index('GDLCODE')
subnat.index.name = 'gdlcode'
subnat.columns = ['iso_code', 'iso2', 'iso_num', 'country', 'level', 'region']
subnat['is--subnational'] = 'TRUE'
# %%
subnat = subnat.drop(columns=['level'])
# %%
subnat['subnat'] = subnat.index.map(to_concept_id)
# %%
subnat = subnat.reset_index().set_index('subnat')
# %%
subnat
# %%
subnat['iso_code'].hasnans
# %%
natmap = nat['iso_code'].to_dict()
# %%
natmap = dict([(v, k) for k, v in natmap.items()])
# %%
natmap
# %%
subnat['national'] = subnat['iso_code'].map(lambda x: natmap.get(x))
subnat['name'] = subnat['country'].str.strip() + ' - ' + subnat['region'].str.strip()
subnat = subnat.drop(columns=['country', 'region', 'iso_code', 'iso2', 'iso_num'])
# %%
subnat
# %%
subnat.to_csv('../../ddf--entities--level--subnat.csv')
# %%
# urb/rur
rur = ents[ents.level == 'Urb/rur']
# %%
rur
# %%
rur = rur.set_index('GDLCODE')
rur.index.name = 'gdlcode'
rur.columns = ['iso_code', 'iso2', 'iso_num', 'country', 'level', 'region']
rur['is--urb_rur'] = 'TRUE'
rur = rur.drop(columns='level')
# %%
rur
# %%
rur['national'] = rur['iso_code'].map(lambda x: natmap.get(x))
# %%
rur['urb_rur'] = rur.index.map(to_concept_id)
rur['name'] = rur['country'].str.strip() + ' - ' + rur['region'].str.strip()
rur = rur.drop(columns=['country', 'region', 'iso_code', 'iso2', 'iso_num'])

# %%
rur = rur.reset_index().set_index('urb_rur')
# %%
rur
# %%
rur.to_csv('../../ddf--entities--level--urb_rur.csv')
# %%
# Wealth quartiles
wq = ents[ents['level'] == 'Wealth quartiles']
# %%
wq
# %%
wq = wq.set_index('GDLCODE')
wq.index.name = 'gdlcode'
wq.columns = ['iso_code', 'iso2', 'iso_num', 'country', 'level', 'region']
wq['is--wealth_quartiles'] = 'TRUE'
wq = wq.drop(columns='level')
# %%
wq['national'] = wq['iso_code'].map(lambda x: natmap.get(x))
wq['wealth_quartiles'] = wq.index.map(to_concept_id)
wq['name'] = wq['country'].str.strip() + ' - ' + wq['region'].str.strip()
wq = wq.drop(columns=['country', 'region', 'iso_code', 'iso2', 'iso_num'])
# %%
wq = wq.reset_index().set_index('wealth_quartiles')
# %%
wq
# %%
wq.to_csv('../../ddf--entities--level--wealth_quartiles.csv')
# %%
# poverty
pov = ents[ents['level'] == 'Poverty']
# %%
pov
# %%
pov = pov.set_index('GDLCODE')
pov.index.name = 'gdlcode'
pov.columns = ['iso_code', 'iso2', 'iso_num', 'country', 'level', 'region']
pov['is--poverty'] = 'TRUE'
pov = pov.drop(columns='level')
pov['national'] = pov['iso_code'].map(lambda x: natmap.get(x))
pov['poverty'] = pov.index.map(to_concept_id)
pov['name'] = pov['country'].str.strip() + ' - ' + pov['region'].str.strip()
pov = pov.drop(columns=['country', 'region', 'iso_code', 'iso2', 'iso_num'])
# %%
pov
# %%
pov = pov.reset_index().set_index('poverty')
# %%
pov
# %%
pov.to_csv('../../ddf--entities--level--poverty.csv')
# %%
data.head()
# %%
gs = data.groupby('level')
# %%
gmap = {
    'National': 'national',
    'Poverty': 'poverty',
    'Subnat': 'subnat',
    'Urb/rur': 'urb_rur',
    'Wealth quartiles': 'wealth_quartiles'
}
# %%
for k, df in gs:
    gid = gmap[k]
    dfg = df.copy()
    dfg[gid] = dfg['GDLCODE'].map(to_concept_id)
    dfg = dfg.set_index([gid, 'year']).loc[:, 'N': 'empty'].drop(columns=['empty'])
    for c in dfg.columns:
        cid = to_concept_id(c)
        fname = f'../../datapoints/ddf--datapoints--{cid}--by--{gid}--year.csv'
        ser = dfg[c]
        ser.name = cid
        ser.index.names = [gid, 'year']
        ser.sort_index().dropna().to_csv(fname)
# %%
data.loc[:, 'N': 'empty'].columns
# %%
desc
# %%
desc['concept'] = desc['Variable'].map(to_concept_id)
# %%
desc = desc.set_index('concept')
# %%
desc[['Variable', 'Dtype', 'Shortdescr', 'Longdescr']]
# %%
desc.index.values
# %%
desc.loc['wrldreg']
# %%
desc = desc.drop(['country', 'datasource', 'level', 'region', 'dollarstreet', 'dollarstlink', 'continent', 'wrldreg'])
# %%
desc
# %%
desc = desc.drop(columns=['Category', 'Decimals', 'RankOrder', 'Label'])
# %%
desc
# %%
desc.columns = ['name', 'concept_type', 'shortdescr', 'longdescr']
# %%
desc['concept_type'] = 'measure'
# %%
desc.loc[['iso_code', 'iso2', 'iso_num', 'gdlcode'], 'concept_type'] = 'string'
desc.loc[['year'], 'concept_type'] = 'time'
# %%
desc
# %%
# append more
concs = [
    ['level', 'Level', 'entity_domain'],
    ['national', 'National', 'entity_set'],
    ['subnat', 'Sub National', 'entity_set'],
    ['urb_rur', 'Urb/Rur', 'entity_set'],
    ['wealth_quartiles', 'Wealth Quartiles', 'entity_set'],
    ['poverty', 'Poverty Level', 'entity_set']
]
concs = pd.DataFrame(concs, columns=['concept', 'name', 'concept_type']).set_index('concept')
# %%
concs.loc[['national', 'subnat', 'urb_rur', 'wealth_quartiles', 'poverty'], 'domain'] = 'level'
concs.loc[['national', 'subnat', 'urb_rur', 'wealth_quartiles', 'poverty'], 'drill_ups'] = 'national'
# %%
concs2 = [
    ['shortdescr', 'Short Description', 'string'],
    ['longdescr', 'Long Description', 'string'],
    ['domain', 'Domain', 'string'],
    ['drill_ups', 'Drill ups', 'string'],
    ['name', 'Name', 'string']
]
concs2 = pd.DataFrame(concs2, columns=['concept', 'name', 'concept_type']).set_index('concept')
# %%
concs
# %%
concs3 = [
    ['chnprim', '', 'measure'],
    ['nchnprim', '', 'measure']
]
concs3 = pd.DataFrame(concs3, columns=['concept', 'name', 'concept_type']).set_index('concept')
# %%
cdf = pd.concat([desc, concs, concs2, concs3])
# %%
cdf
# %%
cdf.to_csv('../../ddf--concepts.csv')
# %%
