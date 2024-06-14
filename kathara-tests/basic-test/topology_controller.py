from setup import remove_link, add_route, del_route, configure_link
import json 
from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara
from Kathara.model.Machine import Machine
import argparse 

def get_lab():
    with open("./tmp/lab_detail.json", "r") as f:
        lab_detail = json.load(f)
    lab_hash = lab_detail["lab_hash"]
    lab_name = lab_detail["lab_name"]
    lab = Kathara.get_instance().get_lab_from_api(lab_hash=lab_hash, lab_name=lab_name)
    return lab

def get_links_stats(lab, link_name = None):
    return Kathara.get_instance().get_links_stats(lab_hash=lab.hash, link_name = link_name)

def connect_machine_to_link(lab, node_name, link_name):
    machine = lab.get_machine(node_name)
    link = lab.get_link(link_name)

    Kathara.get_instance().connect_machine_to_link(machine=machine, link=link)

def disconnect_machine_from_link(lab, node_name, link_name):
    machine = lab.get_machine(node_name)
    link = lab.get_link(link_name)

    Kathara.get_instance().disconnect_machine_from_link(machine=machine, link=link)

def connect_machine_to_link(lab, node_name, link):
    machine = lab.get_machine(node_name)
    Kathara.get_instance().connect_machine_to_link(machine=machine, link=link)

def link_nodes(link_name):
    return link_name.split("-")

def main(args):
    try:
        lab = get_lab() 
        node1, node2 = link_nodes(args.link)[0], link_nodes(args.link)[1]
        
        if args.action == "add":
            link = lab.new_link(args.link)
            connect_machine_to_link(lab=lab, node_name=node1, link = link)
            connect_machine_to_link(lab=lab, node_name=node2, link = link)
            Kathara.get_instance().deploy_link(link)
            print("successfully added the link")
            
        elif args.action == "remove":
            #check status of the link 
            for stat in get_links_stats(lab, args.link):
                print(stat)
                break 
            #to undeploy a link, you must undeploy all the devices attached to it 
        #https://github.com/KatharaFramework/Kathara/issues/284
            disconnect_machine_from_link(lab=lab, node_name=node1, link_name=args.link)
            disconnect_machine_from_link(lab=lab, node_name=node2, link_name=args.link)
            remove_link(lab, args.link)
            print("successfully removed the link")
        
        #check status of the link after the action
        for stat in get_links_stats(lab, args.link):
            print("link status:", stat)
            break 

        
    except Exception as e: 
        print(e)
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", type=str, default=None)
    parser.add_argument("--link", type=str, default=None)
    args = parser.parse_args()
    print(args)
    main(args)