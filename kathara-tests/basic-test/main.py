import subprocess
import sys
from utils.experiment_helpers import setup_device, iperf3_server, iperf3_client, pathneck, parse_pathneck_result, parse_iperf3_bandwidth
from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara
from Kathara.model.Machine import Machine
import docker
import time

def main():
    try:
        lab = Lab("basic-test")
        pc1 = setup_device(lab, "pc1", "katharatestimage", ["A"], ["ip address add 100.0.0.2/24 dev eth0", "ip route add default via 100.0.0.1 dev eth0",])
        pc2 = setup_device(lab, "pc2", "katharatestimage", ["B"], ["ip address add 200.0.0.2/24 dev eth0", "ip route add default via 200.0.0.1 dev eth0",])
        r1 = setup_device(lab, "r1", "katharatestimage", ["A", "B"], ["ip address add 100.0.0.1/24 dev eth0", "ip address add 200.0.0.1/24 dev eth1", "tc qdisc add dev eth0 root netem delay 10ms",])

        Kathara.get_instance().deploy_lab(lab)

        print("executing commands")

        stdout = iperf3_server(lab, pc1, 7575)
        std_pc2_c_out, _, retcode = iperf3_client(lab, pc2, "100.0.0.2", 7575)

        print("execution complete")
        print(list(x for x in std_pc2_c_out))
        print("Bandwidth", parse_iperf3_bandwidth(std_pc2_c_out), "Mbps,", "Retcode", retcode)
        print(next(Kathara.get_instance().get_machines_stats(lab_name=lab.name)))

        Kathara.get_instance().undeploy_lab(lab_name=lab.name)
    except Exception as e:
        print(e)
        Kathara.get_instance().undeploy_lab(lab_name=lab.name)
    except KeyboardInterrupt:
        Kathara.get_instance().undeploy_lab(lab_name=lab.name)

main()
