from common_scripts import inat_api
import json

# id_histories = inat_api.get_id_histories('Syntrichia laevipila', 1000)

# with open('data/test_data.json', 'w') as fp:
#     fp.write(json.dumps(id_histories))

print(inat_api.get_sim_spp(55821))