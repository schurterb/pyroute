# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 19:59:42 2016

@author: schurterb

This provides a manager for keeping track of and assigning IP addresses.
Currently the Address manager is quite simple and cannot handle overlapping
 networks
"""

from .networkexceptions import IPException
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from sh import ifconfig

class IPv4Manager(object):
    
    def __init__(self, **kwargs):
        # subnets = { network_address : [ [ used IPs ], [ freed IPs ] ] }
        self.subnets = {}
        self.default_network = IPv4Network('1.0.0.0/24')        
        self.subnets[self.default_network] = [[], []]
        
        self.macAddr = {}
            
    
    def newAddress(self, network=None, netmask="24"):        
        if network is None:
            network = self.default_network
        else:
            network = IPv4Network(network+"/"+netmask)
        
        try:
            table = self.subnets[network]
        except:
            raise IPException("Subnet not loaded.")
            
        if (len(table[0]) == 0):
            address = network[0]
        elif (len(table[1]) == 0):
            address = max(table[0])
        else:
            address = min(table[1])
        
        try:
            address = IPv4Address(address +1)
        except:
            raise IPException("Invalid Address.")
        
        if address < network[-1] and address > network[0]:
            table[0].append(int(address))
            return str(address)
        else:
            return None
            
        
    def freeAddress(self, address):
       address = IPv4Address(address)     
       
       for network in list(self.subnets.keys()):
           if address < network[-1] and address > network[0]:
               table = self.subnets[network]
               address = int(address)
               
               try:
                   table[0].remove(address)
               except:
                   raise IPException("IP freed but never used.")
               table[1].append(address)
               return True
       return False
       
       
    def addSubnet(self, network, netmask="24"):        
        network = IPv4Network(network+"/"+netmask)
        self.subnets[network] = [[], []]
        
        
    def delSubnet(self, network, netmask="24"):        
        network = IPv4Network(network+"/"+netmask)
        try:
            del self.subnets[network]
        except:
            raise IPException("Network deleted but never added.")
         
    #This method must always and only be used for defining the MAC addresses
    # of nodes
    def genarateMAC(self, ip):
        ip = ip.split('.')
        mac = ['42', '42']
        for x in ip:
            x = hex(int(x)).split('x')[1]
            if len(x) == 1:
                mac += ['0'+x]
            elif len(x) == 2:
                mac += [x]
            else:
                raise ValueError
        
        return ":".join(x for x in mac)
        
    def getIP(self, device='eth0'):
        return ifconfig(device).split(' ')[13]
        
    def getMAC(self, device='eth0'):
        return ifconfig(device).split(' ')[43]
        
class IPv6Manager(object):
    
    def __init__(self, **kwargs):
        
        # subnets = { network_address : [ [ used IPs ], [ freed IPs ] ] }
        self.subnets = {}
        self.default_network = IPv4Network('1.0.0.0/24')        
        self.subnets[self.default_network] = [[], []]
    
    
    def __del__(self):
        pass
    
    
    def newAddress(self, network=None, netmask="24"):        
        if network is None:
            network = self.default_network
        else:
            network = IPv6Network(network+"/"+netmask)
        
        try:
            table = self.subnets[network]
        except:
            raise IPException("Subnet not loaded.")
            
        if (len(table[0]) == 0):
            address = network[0]
        elif (len(table[1]) == 0):
            address = max(table[0])
        else:
            address = min(table[1])
        
        try:
            address = IPv6Address(address +1)
        except:
            raise IPException("Invalid Address.")
        
        if address < network[-1] and address > network[0]:
            table[0].append(int(address))
            return str(address)
        else:
            return None
            
        
    def freeAddress(self, address):
       address = IPv6Address(address)     
       
       for network in list(self.subnets.keys()):
           if address < network[-1] and address > network[0]:
               table = self.subnets[network]
               address = int(address)
               
               try:
                   table[0].remove(address)
               except:
                   raise IPException("IP freed but never used.")
               table[1].append(address)
               return True
       return False
       
       
    def addSubnet(self, network, netmask="24"):        
        network = IPv6Network(network+"/"+netmask)
        self.subnets[network] = [[], []]
        
        
    def delSubnet(self, network, netmask="24"):        
        network = IPv6Network(network+"/"+netmask)
        try:
            del self.subnets[network]
        except:
            raise IPException("Network deleted but never added.")       

    def generateMAC(self, ip):
        raise NotImplementedError
            
    def getIP(self, device='eth0'):
        return ifconfig(device).split(' ')[28]
        
    def getMAC(self, device='eth0'):
        return ifconfig(device).split(' ')[43]