from nornir.core.task import Task, Result
from nornir import InitNornir
from Subbnetter import subbnetter
from AddDHCPools import AddDHCPPools
from CopRunStart import SaveRunningToStart
from microsegmenter import MicroSegmenter
from nornir_utils.plugins.functions import print_result
#from nornir.plugins.tasks.networking import netmiko_send_config
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
import time


#todo
#auto apply to routers
#auto config ranges to dhcp server
#adding the ability to spesify what leaf gets what range

#future ideas for projekts
#python bor
#CDP or IP based LAG constructor
#micro segmenter on subb interfaces for ip coonfiguration when connectivity is needed while configing ips not concluded if i want this to be based on CDP or IP adresses
#leaf stuff
#auto secuing based on standards (dhcp snooping, dynamic arp inspection, port security, disabeling ports that is not needed)

startTime=time.time()

nr = InitNornir(
    config_file="E:/NornirAutoSubbnetter/config.yaml"
    )


#testing new function before mooving it o a seperat file
nr.run(task=MicroSegmenter)



def main():
    subbnets = subbnetter(nettwork="10.0.0.0", 
    nettworkReq=[
    {"numberOfSubbnets":16, "requiredHosts":200},
    {"numberOfSubbnets":20, "requiredHosts":20}
    ])
    
    #addingPools = nr.run(task=AddDHCPPools, ipconfigs=subbnets)
    #print_result(addingPools)

    #save = nr.run(task=SaveRunningToStart)
    #print_result(save)

main()
print(f"the script took {time.time()-startTime} seconds")