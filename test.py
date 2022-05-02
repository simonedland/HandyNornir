from nornir.core.task import Task, Result
from nornir import InitNornir
from Subbnetter import subbnetter
from AddDHCPools import AddDHCPPools
from CopRunStart import SaveRunningToStart
from microsegmenter import MicroSegmenter
import portSecurer
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
import time


#todo:
#auto apply to routers
#auto config ranges to dhcp server
#adding the ability to spesify what leaf gets what range

#future ideas for projekts
#python bor
#CDP based LAG constructor
#auto secuing based on standards (dhcp snooping, dynamic arp inspection, port security, disabeling ports that is not needed)


startTime=time.time() #this is the start time of the program

nr = InitNornir(config_file="config.yaml") #this is the nornir object


def main():

    #portSecurer.ARPMarker()
    reeee=nr.run(task=portSecurer.PortMarker)
    print_result(reeee)

main() #run the main function
print(f"\n\n\n\n\nthe script took {time.time()-startTime} seconds") #prints how long the script took to run