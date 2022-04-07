
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config

def getIntInfo(node):
    return node.run(task=netmiko_send_command, command_string=("sh ip int br"), enable=True, use_textfsm=True)


def MicroSegmenter(node):
    intInfo = getIntInfo(node)
    node.host["facts"] = intInfo.result
    for x in node.host["facts"]:
        print(x)