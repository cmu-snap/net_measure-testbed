import os
import sys
from utils.experiment_helpers import iperf3_server, iperf3_client, pathneck, parse_pathneck_result
from Kathara.model.Lab import Lab
# import Kathara
from Kathara.manager.Kathara import Kathara
from Kathara.manager.docker.DockerMachine import DockerMachine
from Kathara.manager.docker.DockerImage import DockerImage
from Kathara.model.Machine import Machine
import docker


lab = Lab("basic-test")

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

dockerImage = DockerImage(client)

dockerMachine = DockerMachine(client, dockerImage)

pc1 = Machine(lab, "pc1", **{"image": "katharatestimage"})

pc2 = Machine(lab, "pc2", **{"image": "katharatestimage"})

# Create router1 with image "kathara/frr"
# router1 = lab.new_machine("router1", **{"image": "katharatestimage"})

ip_port = [{"ip" : "100.0.0.2", "port": "7575"}, {"ip" : "200.0.0.2", "port": "7576"}]

lab.connect_machine_to_link(pc1.name, "A")
lab.connect_machine_to_link(pc2.name, "A")

Kathara.get_instance().deploy_lab(lab)
print(type(pc1))

dockerMachine.create(machine=pc1)
dockerMachine.create(machine=pc2)

pc1_server = "iperf3 -s -p 7575 &"
pc2_server = "iperf3 -s -p 7576 &"
pc1_c = "iPerf3 -c 200.0.0.2 -p 7576"
pc2_c = "iPerf3 -c 100.0.0.2 -p 7575"

[stdout_pc1_s, stderr_pc1_s] = pc1.api_object.exec(lab_hash=lab.hash, machine_name=pc1.name, user="pc1", command=pc1_server, wait=True)
[stdout_pc2_s, stderr_pc2_s] = pc2.api_object.exec(lab_hash=lab.hash, machine_name=pc2.name, user="pc2", command=pc2_server, wait=True)
[stdout_pc1_c, stderr_pc1_c] = pc1.api_object.exec(lab_hash=lab.hash, machine_name=pc1.name, user="pc1", command=pc1_c, wait=True)
[stdout_pc2_c, stderr_pc2_c] = pc2.api_object.exec(lab_hash=lab.hash, machine_name=pc2.name, user="pc2", command=pc2_c, Wait=True)
# Kathara.get_instance().connect_tty(pc2.name, lab_name=lab.name)
print(stderr_pc1_s)
print(stderr_pc1_s)
print(stdout_pc2_s)
print(stderr_pc2_s)
print(stderr_pc1_c)
print(stderr_pc1_c)
print(stdout_pc2_c)
print(stderr_pc2_c)
print(next(Kathara.get_instance().get_machines_stats(lab_name=lab.name)))

# pc1.api_object.undeploy(lab.hash, {pc1.name, pc2.name})

Kathara.get_instance().undeploy_lab(lab_name=lab.name)
