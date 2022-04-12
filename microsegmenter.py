#how to solve
#i think i need to alocate one nettwork to eatch spine and then make then microsegment the networks to the leafs.
#the leafs then knowing what nic goes to what spine can configgure to use the right ip based on it knowing what spine it self is
#would like to know a beter way to do this

#inputs wil probably be (where the spines at, what subbnet to segment, and how manny segments, where the spines at)
#could probably just auto detect all that

#i realy want to base this on CDP or LLDP

from Subbnetter import subbnetter
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
#gets the nesesairy information from cdp and running config
def getIntInfo(node):
    return node.run(task=netmiko_send_command, command_string=("sh cdp nei de"), enable=True, use_textfsm=True), node.run(task=netmiko_send_command, command_string=("sh run"), enable=True, use_textfsm=True)


def MicroSegmenter(node):


    #this is loopable to make it possible to have enorm amount of spines but that might require more prosessing power
    #constructs the micro segment information using my subbnetter script
    #if you want more spines you have to add more subbnets to microsegment
    subbnetspine1 = subbnetter(nettwork="10.0.0.0", 
        nettworkReq=[
        {"numberOfSubbnets":16, "requiredHosts":2},
        ])

    subbnetspine2 = subbnetter(nettwork="10.0.1.0", 
        nettworkReq=[
        {"numberOfSubbnets":16, "requiredHosts":2},
        ])

    listOfSubbnets=[subbnetspine1, subbnetspine2]

    #constructs the interface information and running config information
    #theese are stored in node.host[intf] and [self]
    intInfo = getIntInfo(node)[0]
    runInfo = getIntInfo(node)[1]
    node.host["intf"] = intInfo.result
    node.host["self"] = runInfo.result
    
    #finds all the locations of the keywords device id and interface
    #this information is on the cdp neigbour and is information about the neigbor bechause we are making a connection to the neigbour
    hostnames = [i for i in range(len(node.host["intf"])) if node.host["intf"].startswith("Device ID:", i)]
    interfaces = [i for i in range(len(node.host["intf"])) if node.host["intf"].startswith("Interface:", i)]


    #constructs a list of dictionaries with the values of hostname and what interface it is connected to
    cdpNeigbourDirections=[]
    for x in range(len(hostnames)):
        hostname = (node.host["intf"][hostnames[x]+11:hostnames[x]+24].split("\n")[0].split(".")[0])
        interface = (node.host["intf"][interfaces[x]+11:interfaces[x]+30].split("\n")[0].split(",")[0])
        cdpNeigbourDirections.append({"name":hostname, "interface":interface})
    #print(cdpNeigbourDirections)

    #finds out if the relevant switch is a spine or leaf
    if "hostname leaf" in node.host["self"]: #checks if it self is a leaf
        for neigbor in cdpNeigbourDirections: # if it is a leaf it loops trough al the cdp neigbor information
            #print(neigbor)
            if "spine" in neigbor["name"]: # if it finds spine 1 it wil do the following
                try:
                    spineNr=int(neigbor["name"][5:7])
                except:
                    spineNr=int(neigbor["name"][5:6])
                locationOfQuote=node.host["self"].find("hostname leaf") # finds out where it self says what leaf it is in the running config by looking for the hostname
                LeafNr=int(node.host["self"][locationOfQuote+13:locationOfQuote+15].replace(" ","")) # converts the last part of the hostname in to a int example: leaf7 = 7
                relevantSubbnet=listOfSubbnets[spineNr-1][LeafNr-1]
                MyIp=(f"{relevantSubbnet['broadcast'].split('.')[0]}.{relevantSubbnet['broadcast'].split('.')[1]}.{relevantSubbnet['broadcast'].split('.')[2]}.{int(relevantSubbnet['broadcast'].split('.')[3])-1}")
                print(f"this leaf interface wil choose the ip adress {MyIp}") #print for controll


    elif "hostname spine" in node.host["self"]:
        for neigbor in cdpNeigbourDirections:
            if neigbor["name"]=="Switch":
                print("error in cdp neigbor name")
                pass
            try:
                leafNr = int(neigbor["name"][4:6])
            except:
                leafNr = int(neigbor["name"][4:5])
            locationOfQuote=node.host["self"].find("hostname spine")
            SpineNr=int(node.host["self"][locationOfQuote+14:locationOfQuote+16].replace(" ",""))
            relevantSubbnet=listOfSubbnets[SpineNr-1][leafNr-1]
            MyIp=(f"{relevantSubbnet['subbnetID'].split('.')[0]}.{relevantSubbnet['subbnetID'].split('.')[1]}.{relevantSubbnet['subbnetID'].split('.')[2]}.{int(relevantSubbnet['subbnetID'].split('.')[3])+1}")
            print(f"this spine interface wil choose the ip adress {MyIp}")
    
    
    print("_____")