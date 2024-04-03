import subprocess
import sys
from utils.experiment_helpers import iperf3_server, iperf3_client, pathneck, parse_pathneck_result, parse_iperf3_bandwidth
from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara
from Kathara.model.Machine import Machine
from setup import setup_topology
import docker
import time

def main():

    try:
        lab, links, nodes = setup_topology()

        print(nodes)
        for node in nodes:
            (stdout, stderr, retcode) = iperf3_server(lab, node)
            print(stdout, stderr, retcode)

        # run iperf between every pair of nodes
        results = {}
        for dest, (ip, _) in nodes.items():
            for source in nodes:
                if(source != dest):
                    (stdout, stderr, retcode) = iperf3_client(lab, dest, ip)
                    if(retcode == 0):
                        results[(source,dest)] = parse_iperf3_bandwidth(stdout)
                        print()
                    else:
                        results[(source, dest)] = stderr
        print(results)
        Kathara.get_instance().undeploy_lab(lab_name=lab.name)
    except Exception as e:
        print(e)
        Kathara.get_instance().undeploy_lab(lab_name=lab.name)
    except KeyboardInterrupt:
        Kathara.get_instance().undeploy_lab(lab_name=lab.name)

main()
