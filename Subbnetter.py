def subbnetter(nettwork, nettworkReq): 
    """
    this requires a nettwork ID for the nettwork you want to subbnet
    it also requires a list of dictionaries that contain "requiredHosts" and "numberOfSubbnets"
    the required hosts key has a value of at least how manny hosts there should be, and the number of subbnets key shuld contain how manny of that subbnet you want
    the return is a list of dictswith hopfully self explaining keys "subbnetID" "broadcast" "mask" "nrOfHostsAvaidable"
    the nrOfHostsAvaidable key has a value of how manny ips axualy fits in the subbnet (keep in mind that id, broadcst, and sometimes gateway takes up some ips)
    """
    
    #sorts the list from most required hosts to least. uses lamda. i need to learn lambda
    nettworkReq = sorted(nettworkReq, key=lambda d:d["requiredHosts"], reverse = True) 
    
    #takes the nettwork, splits it to octets and converts to int
    networkOctetList=[]
    for x in nettwork.split("."):
        networkOctetList.append(int(x))

    subbnetID=networkOctetList

    #makes a list with the values of the binaries
    y=1
    octetValueList=[]
    for x in range(32):
        octetValueList.append(y)
        y=y*2



    networkList=[]

    for x in nettworkReq:
        counter=0
        for octetvale in octetValueList:
            if octetvale-1>=x["requiredHosts"]: #finds the least value the subbnets wil take
                for nrofNettworks in range(x["numberOfSubbnets"]): 
                    subbnetID=str(f"{networkOctetList[0]}.{networkOctetList[1]}.{networkOctetList[2]}.{networkOctetList[3]}")

                    #octet 4 handler
                    if counter <= 8:
                        if octetValueList[counter] + networkOctetList[3] == 256: # if it fills up the octet
                            networkOctetList[3]=0
                            networkOctetList[2]+=1
                            broadcast=f"{networkOctetList[0]}.{networkOctetList[1]}.{networkOctetList[2]-1}.255"
                            if networkOctetList[2] == 255:
                                networkOctetList[1]+=1
                                networkOctetList[3]=0
                                networkOctetList[2]=0
                                broadcast=f"{networkOctetList[0]}.{networkOctetList[1]-1}.255.255"
                        elif octetValueList[counter] + networkOctetList[3] < 256:
                            networkOctetList[3]+=octetValueList[counter]
                            broadcast=f"{networkOctetList[0]}.{networkOctetList[1]}.{networkOctetList[2]}.{networkOctetList[3]-1}"


                    # octet 3 handler
                    elif counter <= 16 and counter > 8:
                        if octetValueList[counter-8] + networkOctetList[2] == 256:
                            networkOctetList[2]=0
                            networkOctetList[1]+=1
                            broadcast=f"{networkOctetList[0]}.{networkOctetList[1]-1}.255.255"
                        elif octetValueList[counter-8] + networkOctetList[2] < 256:
                            networkOctetList[2]+=octetValueList[counter-8]
                            broadcast=f"{networkOctetList[0]}.{networkOctetList[1]}.{networkOctetList[2]-1}.255"


                    # octet 2 handler
                    elif counter <= 24 and counter > 16:
                        if octetValueList[counter-16] + networkOctetList[1] == 256:
                            networkOctetList[1]=0
                            networkOctetList[0]+=1
                            broadcast=f"{networkOctetList[0]-1}.255.255.255"
                        elif octetValueList[counter-16] + networkOctetList[1] < 256:
                            networkOctetList[1]+=octetValueList[counter-16]
                            broadcast=f"{networkOctetList[0]}.{networkOctetList[1]-1}.255.255"

                    subbnetBittList=[0,128,192,224,240,248,252,254,255]
                    octet1,octet2,octet3,octet4=0,0,0,0
                    maskList=[0,0,0,0]
                    for x in range(32-counter):
                        if maskList[0]==255:
                            if maskList[1]==255:
                                if maskList[2]==255:
                                    if maskList[3]==255:
                                        pass
                                    else:
                                        octet4+=1
                                        maskList[3]=subbnetBittList[octet4]
                                else:
                                    octet3+=1
                                    maskList[2]=subbnetBittList[octet3]
                            else:
                                octet2+=1
                                maskList[1]=subbnetBittList[octet2]
                        else:
                            octet1+=1
                            maskList[0]=subbnetBittList[octet1]
                    mask=f"{maskList[0]}.{maskList[1]}.{maskList[2]}.{maskList[3]}"

                    #construct the list that should be returned
                    networkList.append({"subbnetID":subbnetID, "broadcast":broadcast, "mask":mask, "nrOfHostsAvaidable":f"{octetvale}"})

                break
            counter+=1

    return networkList