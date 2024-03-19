import os
import sys
from utils.experiment_helpers import iperf3_server, iperf3_client, pathneck, parse_pathneck_result
from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara

lab = Lab("basic-test")

pc1 = lab.new_machine("pc1")

pc2 = lab.new_machine("pc2")

# Create router1 with image "kathara/frr"
# router1 = lab.new_machine("router1", **{"image": "katharatestimage"})

# ip_port = [{"ip" : "100.0.0.2", "port": "7575"}, {"ip" : "200.0.0.2", "port": "7576"}]

lab.connect_machine_to_link(pc1.name, "A")
lab.connect_machine_to_link(pc2.name, "A")

Kathara.get_instance().deploy_lab(lab)



