"""
This script contains functions that retrieve various processed data from the iNaturalist API.
"""

from typing import List, Optional, Tuple
import requests as rq
import time

"""
CONFIGS
"""

# Default time delay between iNat API requests in seconds
# Sleeping is required to fit iNaturalist's API Terms of Use (https://api.inaturalist.org/v1/docs)
INAT_DELAY = 1

"""
FUNCTIONS
"""

def get_taxon_id(taxon:str) -> int:
    """
    Get the internal taxon ID of a taxon in the iNaturalist API.

    Parameters:
        taxon (str): The scientific name of the taxon of interest.
    
    Returns:
        taxon_id (int): The corresponding taxon ID.
    """

    # Make request to find the taxon
    obs = rq.get('https://api.inaturalist.org/v1/taxa',
                        params = {
                            'q': taxon # Name of taxon
                        }).json()['results']
    
    # Get first taxon's ID and return it
    taxon_id:int = obs[0]['id']
    return taxon_id

def get_taxon_ids(taxa:List[str]) -> List[int]:
    """
    Batch version of get_taxon_id; convert a list of taxa name to API IDs.

    Parameters:
        taxa (List[str]): A list of the scientific names of the taxa of interest.
    
    Returns:
        taxon_ids (List[int]): A list of the corresponding API IDs.
    """

    # Apply get_taxon_id on the entries and return result
    return [get_taxon_id(taxon) for taxon in taxa]

def get_taxon_name(taxon_id:int) -> str:
    """
    Get the name of the taxon, given the API taxon ID.

    Parameters:
        taxon_id (int): The taxon ID

    Returns:
        taxon (str): The taxon name. This will be the binomial/trinomial for species-level or subspecies-level taxa and simply the taxon name for higher taxa.
    """

    # Make request to find the taxon
    obs = rq.get('https://api.inaturalist.org/v1/taxa/{}'.format(taxon_id)).json()['results']
    
    # Get first taxon's name and return it
    taxon:str = obs[0]['name']
    return taxon

def get_taxon_names(taxon_ids:List[int]) -> List[str]:
    """
    Get the name of multiple taxa, given a list of taxon IDs.

    Parameters:
        taxon_ids (List[int]): List of taxon IDs
    
    Returns:
        taxa (str): The taxon names
    """

def get_obs_n(taxon_id:int) -> int:
    """
    Get the number of observations for the given taxon.

    Parameters:
        taxon_id (int): The iNat API taxon ID for the taxon.

    Returns:
        n_obs (int): The number of observations of the given taxon.
    """

    # Make API request to retrieve taxon data
    taxa = rq.get('https://api.inaturalist.org/v1/taxa/{}'.format(taxon_id)).json()['results']
    
    # Get first taxon's observation count and return it
    n_obs:int = taxa[0]['observations_count']
    return n_obs


def get_id_histories(taxon_id:int, n_obs:Optional[int] = None, obs_per_page:int = 200, delay:float = INAT_DELAY) -> List[dict]:
    """
    Retrieve the identification histories of the observations of a given taxon.
    The output list is structured as follows:
    [
        {
            'history': ['Scientific name', 'Scientific name', ...]
        }, ...
    ]

    Parameters:
        taxon_id (int): The iNat API taxon ID for the taxon of interest.
        n_obs (int): The number of observations to look up using the iNat API. Default is None, which gets ID histories from all observations.
        obs_per_page (int): The number of observations per page to use for the API call. Deafult is 200.
        delay (float): Delay between batch API calls in seconds. Default is 1.

    Returns:
        id_histories (List[dict]): A list of identification histories.
    """

    # If n_obs is not specified, set it as the number of observations present for the taxon
    if n_obs == None:
        n_obs = get_obs_n(taxon_id)
    
    # ===== Get identification histories for a taxon =====
    id_histories = []

    for page_id in range(0, n_obs // obs_per_page + 1): # Iterate through page ids
        # Make request to retrieve observations of the taxon
        obs = rq.get('https://api.inaturalist.org/v1/observations',
                        params = {
                            'taxon_id': taxon_id,
                            'per_page': min(obs_per_page, n_obs - page_id * obs_per_page),
                            'page': page_id + 1,
                            'identified': 'true', # Observations with community identifications
                            'quality_grade': 'research' # Filter for research-grade observations, so that we are reasonably confident of the 'true' identity of the species
                        }).json()['results']

        # Convert to a list of identification histories
        id_histories_part = [
            {
                'history': [ident['taxon']['name'] for ident in obs_one['identifications']]
            }
            for obs_one in obs
        ]

        # Push to id_histories
        id_histories.extend(id_histories_part)

        # Delay for specified amount of time
        time.sleep(delay) 
    
    return id_histories

def get_sim_spp(taxon_id:int) -> List[Tuple[int, int]]:
    """
    For a given taxon, retrieve the list of species who have been attached to observations of the focal species,
    and the corresponding frequencies.
    This uses the /identification/similar_species API.

    Parameters:
        taxon_id (int): The taxon ID of the taxon of interest
    
    Returns:
        sim_spp (List[(int, int)]): A list of tuples where the first item in the tuple is the taxon ID and the second item is the corresponding frequency.
    """

    # Make request to retrieve similar species
    sim_spp_json = rq.get('https://api.inaturalist.org/v1/identifications/similar_species',
                    params = {
                        'taxon_id': taxon_id
                    }).json()['results']
    
    # Convert the json into a list of tuples
    sim_spp = [(sp['taxon']['id'], sp['count']) for sp in sim_spp_json]

    # Return sim_spp
    return sim_spp