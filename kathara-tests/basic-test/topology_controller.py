from setup import remove_link, add_route, del_route, configure_link
import json 
from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara
from Kathara.model.Machine import Machine

def get_lab():
    with open("./tmp/lab_detail.json", "r") as f:
        lab_detail = json.load(f)
    lab_hash = lab_detail["lab_hash"]
    lab_name = lab_detail["lab_name"]
    lab = Kathara.get_instance().get_lab_from_api(lab_hash=lab_hash, lab_name=lab_name)
    return lab

def get_links_stats(lab, link_name = None):
    return Kathara.get_instance().get_links_stats(lab_hash=lab.hash, link_name = link_name)

def disconnect_machine_from_link(node_name, link_name):
    return Kathara.get_instance().disconnect_machine_from_link(machine=node_name, link=link_name)

def main():
    try:
        lab = get_lab() 
        for stat in get_links_stats(lab, "r6-s1"):
            print(stat)
            print("\n\n\n\n\n\n\n")
            break 
        print("link=",lab.get_link("r6-s1"))
        #to undeploy a link, you must undeploy all the devices attached to it 
        #https://github.com/KatharaFramework/Kathara/issues/284
        print('h')
        print(Kathara.get_instance(), type(Kathara.get_instance()))
        Kathara.get_instance().disconnect_machine_from_link(machine="r6", link="r6-s1")
        # disconnect_machine_from_link("r6", "r6-s1")
        # disconnect_machine_from_link("s1", "r6-s1")
        remove_link(lab, "r6-s1")
        # print(get_links_stats(lab, "r6-s1"))

        
    except Exception as e: 
        print(e)
        return


if __name__ == "__main__":
    main()