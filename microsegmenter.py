#how to solve
#i think i need to alocate one nettwork to eatch spine and then make then microsegment the networks to the leafs.
#the leafs then knowing what nic goes to what spine can configgure to use the right ip based on it knowing what spine it self is
#would like to know a beter way to do this

#inputs wil probably be (where the spines at, what subbnet to segment, and how manny segments, where the spines at)
#could probably just auto detect all that
import time
from tqdm import tqdm
from Subbnetter import subbnetter
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config

def subbnetMicroSegmentListMaker():
    #this makes 10 subbnets with 64 microsegments (subbnets with 2 hosts) making it possible to have 10 spines and 64 leafs
    #if you need more spines you can always increase the loop amount

    subbnetList=[]
    for x in range(0,9):
        subbnetList.append(subbnetter(nettwork=f"10.0.{x}.0", 
            nettworkReq=[
            {"numberOfSubbnets":64, "requiredHosts":2},
            ]))

    return subbnetList



def MicroSegmenter(node):

    bar=tqdm(total=3, desc =str(node.host))

    listOfSubbnets=subbnetMicroSegmentListMaker()#fetches the ip adress data for tyhe spine leaf copnnection

    #constructs the interface information and running config information
    #theese are stored in node.host[intf] and [self]
    node.host["intf"] = node.run(task=netmiko_send_command, command_string=("sh cdp nei de")).result
    bar.update()
    tqdm.write(f"{node.host}: facts gathered 1 of 2")
    node.host["self"] = node.run(task=netmiko_send_command, command_string=("sh run"), enable=True).result
    bar.update()
    tqdm.write(f"{node.host}: facts gathered 2 of 2")
    
    #finds all the locations of the keywords device id and interface
    #this information is on the cdp neigbour and is information about the neigbor bechause we are making a connection to the neigbour
    hostnames = [i for i in range(len(node.host["intf"])) if node.host["intf"].startswith("Device ID:", i)]
    interfaces = [i for i in range(len(node.host["intf"])) if node.host["intf"].startswith("Interface:", i)]
    #constructs a list of dictionaries with the values of hostname and what interface it is connected to
    cdpNeigbourDirections=[]
    for x in range(len(hostnames)):
        hostname = (node.host["intf"][hostnames[x]+11:hostnames[x]+24].split("\n")[0].split(".")[0])
        interface = (node.host["intf"][interfaces[x]+11:interfaces[x]+30].split("\n")[0].split(".")[0])
        cdpNeigbourDirections.append({"name":hostname, "interface":interface})

    #finds out if the relevant switch is a spine or leaf
    if "hostname leaf" in node.host["self"]: #checks if it self is a leaf
        commandlist=[f'ip routing', f'int lo 0', f'ip ospf 1 a 0', f'exit'] # adds the commands to add the loopback interface to a 0 of ospf in the creation of the command list
        for neigbor in cdpNeigbourDirections: # if it is a leaf it loops trough al the cdp neigbor information
            if "spine" in neigbor["name"]: # if it finds spine it wil do the following
                try: # finds out what number of spine it is the reason we do it this way is bechause we dont know if it is spine 20 or 2 so we try to convert the biggest first in to a string
                    spineNr=int(neigbor["name"][5:7])
                except:
                    spineNr=int(neigbor["name"][5:6])
                locationOfQuote=node.host["self"].find("hostname leaf") # finds out where it self says what leaf it is in the running config by looking for the hostname
                LeafNr=int(node.host["self"][locationOfQuote+13:locationOfQuote+15].replace(" ","")) # converts the last part of the hostname in to a int example: leaf7 = 7
                relevantSubbnet=listOfSubbnets[spineNr-1][LeafNr-1]#naming of the spines and leafs starts at 1 but the lists start at 0
                MyIp=(f"{relevantSubbnet['broadcast'].split('.')[0]}.{relevantSubbnet['broadcast'].split('.')[1]}.{relevantSubbnet['broadcast'].split('.')[2]}.{int(relevantSubbnet['broadcast'].split('.')[3])-1}")#places it self one IP under the broadcast
                
                #prepaires the list of commands needed to add itself to OSPF and find the correct ip adress in the microsegment
                commandlist.extend([f"int {neigbor['interface']}.100",f"no sh",f"encap do 10",f"ip add {MyIp} {relevantSubbnet['mask']}",f"router ospf 1",f"network {relevantSubbnet['subbnetID']} {relevantSubbnet['mask']} a 0"])

        #runns the list of commands and prints the result
        configSubIntf = node.run(task=netmiko_send_config, config_commands=commandlist)
        #print_result(configSubIntf)



    elif "hostname spine" in node.host["self"]:
        commandlist=[f'ip routing', f'int lo 0', f'ip ospf 1 a 0', f'exit']
        for neigbor in cdpNeigbourDirections:
            if "leaf" in neigbor["name"]:
                try:
                    leafNr = int(neigbor["name"][4:6])
                except:
                    leafNr = int(neigbor["name"][4:5])
            else:
                pass
            locationOfQuote=node.host["self"].find("hostname spine")
            SpineNr=int(node.host["self"][locationOfQuote+14:locationOfQuote+16].replace(" ",""))
            relevantSubbnet=listOfSubbnets[SpineNr-1][leafNr-1]
            MyIp=(f"{relevantSubbnet['subbnetID'].split('.')[0]}.{relevantSubbnet['subbnetID'].split('.')[1]}.{relevantSubbnet['subbnetID'].split('.')[2]}.{int(relevantSubbnet['subbnetID'].split('.')[3])+1}")
            
            commandlist.extend([f"int {neigbor['interface']}.100",f"no sh",f"encap do 10",f"ip add {MyIp} {relevantSubbnet['mask']}",f"router ospf 1",f"network {relevantSubbnet['subbnetID']} {relevantSubbnet['mask']} a 0"])
        
        configSubIntf = node.run(task=netmiko_send_config, config_commands=commandlist)
    bar.update()
    time.sleep(2)
    bar.leave = False
#74 sek before increasing mem and cpu on the spines
#51 sek after