import subprocess
import sys
import os
from utils.experiment_helpers import iperf3_server, iperf3_client, capture_traffic, pathneck, parse_pathneck_result, parse_iperf3_bandwidth, ptr_client, ptr_server, parse_ptr_result, ptr_clientM
from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara
from Kathara.model.Machine import Machine
from setup import setup_topology
import seaborn as sns
import matplotlib.pyplot as plt
import docker
import time
import threading 
import json 
from topology_controller import get_lab

def main():

    try:
        # setup the topology
        lab = get_lab() 
        # global variables
        n_iter = 3
        bottleneck_bandwidth = []
        data = {'00': [], '01': [], '02': [], '03': [], '04': [], '05': []}

        server = {'name': 's1', 'ip': '10.0.4.4'}
        bandwidth_server = {'name': 'r3', 'ip': '10.0.2.4'}
        contesting_client = 'c2'
        client = 'c1'
        bottleneck_link_dest = {'name': 'r6', 'ip': '10.0.8.4'}
        bottleneck_router = 'r5'
        # iperf3_server(lab, server['name'])
        # iperf3_server(lab, bandwidth_server['name'])
        # print("start the server now")
        server_t = threading.Thread(target = ptr_server, args=(lab, 's1', n_iter+1,))
        server_t.start()

        
        
        dst_addr = server['ip']
        data = [] 
        data_m = []
        for i in range(n_iter+1):
            result = ptr_clientM(lab, 'c1', dst_addr)
            print(result)
            data.append(parse_ptr_result(result))

        # result = ptr_client(lab, 'c1', dst_addr)
        # print(result)
        print("termination:",data)
        # print("without termination:", data_m)
        # result = iperf3_client(lab, "c1", server['ip']) #c2->r6
        # result = iperf3_client(lab, client, bandwidth_server['ip']) #c1->s1
        # print("iperf3 client:",result)
        # server_t.join() 

        print("end")
        
        # Kathara.get_instance().undeploy_lab(lab_name=lab.name)
    except Exception as e:
        print(e)
        # server.join() 
        # client.join() 
        Kathara.get_instance().undeploy_lab(lab_name=lab.name)
    except KeyboardInterrupt:
        # server.join() 
        # client.join() 
        Kathara.get_instance().undeploy_lab(lab_name=lab.name)

main()

