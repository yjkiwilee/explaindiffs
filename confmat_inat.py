from typing import List
import json
import requests as rq
import time

def get_id_histories(taxon:str, n_obs:int, obs_per_page:int = 200) -> List[List[str]]:
    """
    Retrieve the identification histories of the observations of a given taxon.

    Parameters:
        taxon (str): The acientfic of the taxon of interest.
        n_obs (int): The number of observations to look up using the iNat API.
        obs_per_page (int): The number of observations per page to use for the API call. Deafult is 200.

    Returns:

    """

    # Get identification histories for a taxon
    id_histories = []
    for page_id in range(0, n_obs // obs_per_page + 1): # Iterate through page ids
        # Make request to retrieve observations of the taxon
        obs = rq.get('https://api.inaturalist.org/v1/observations',
                        params = {
                            'taxon_name': taxon,
                            'per_page': min(obs_per_page, n_obs - page_id * obs_per_page),
                            'page': page_id + 1,
                            'identified': 'true', # Observations with community identifications
                            'quality_grade': 'research' # Filter for research-grade observations, so that we are reasonably confident of the 'true' identity of the species
                        }).json()['results']

        # Convert to a list of identification histories
        id_histories_part = [
            [ident['taxon']['name'] for ident in obs_one['identifications']]
            for obs_one in obs
        ]

        # Push to id_histories
        id_histories.extend(id_histories_part)

        # Log
        print('Done batch {}'.format(page_id))

        time.sleep(1) # Sleep to fit iNaturalist's API Terms of Use ()
    
    return id_histories

id_histories = get_id_histories('Rumex', 1000)

with open('data/test_data.json', 'w') as fp:
    fp.write(json.dumps(id_histories))