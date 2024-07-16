import json
import requests as rq

def get_obs_history(specieslist):
    for sp in specieslist:
        # Get observations for a species
        obs = rq.get('https://api.inaturalist.org/v1/observations',
                        params = {
                            'taxon_name': sp,
                            'per-page': 200
                        }).json()['results']
        
        # Filter for research-grade observations
        rg_obs = filter(lambda ob : ob['quality_grade'] == 'research', obs)

        print(obs)

get_obs_history(['Sanguisorba officinalis'])
