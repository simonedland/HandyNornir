import time
from tqdm import tqdm
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config

def PortMarker(node):
    node.run(task=netmiko_send_command, command_string=("sh cdp nei de"))
    
    print("test")


def PortCloser():
    print("test")
def DHCPMarker():
    print("test")
def ARPMarker():
    print("test")
def MACLimiter():
    print("test")