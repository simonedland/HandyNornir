#how to solve
#i think i need to alocate one nettwork to eatch spine and then make then microsegment the networks to the leafs.
#the leafs then knowing what nic goes to what spine can configgure to use the right ip based on it knowing what spine it self is
#would like to know a beter way to do this

#inputs wil probably be (where the spines at, what subbnet to segment, and how manny segments, where the spines at)
#could probably just auto detect all that

#i realy want to base this on CDP or LLDP



from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config

def getIntInfo(node):
    return node.run(task=netmiko_send_command, command_string=("sh cdp nei de"), enable=True, use_textfsm=True)


def MicroSegmenter(node):
    intInfo = getIntInfo(node)
    node.host["facts"] = intInfo.result
    
    print(node.host["facts"])
    print(node.host["facts"][node.host["facts"].find("Device ID:"):node.host["facts"].find("Device ID:")+10])
    #for x in node.host["facts"]:
    #    print(x)