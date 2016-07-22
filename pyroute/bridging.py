# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 12:18:25 2016

@author: schurterb

This package provides a manager to handle creating and destroying linux bridges.
"""

from sh import ifconfig, brctl
from .networkexceptions import BridgeException, IPException

"""
Handles creating, destroying, and connecting bridges
"""
class Manager(object):
     
    def create(self, bridge):
        if bridge not in self.bridgeList:
            try:
                brctl.addbr(bridge)
                ifconfig(bridge, 'up')
                self.bridgeList += [bridge]
            except:
                raise BridgeException("Unable to add linux bridge.")
            return True
        else:
            return False
    
    def destroy(self, bridge):
        if bridge in self.bridgeList:
            try:
                ifconfig(bridge, 'down')
                brctl.delbr(bridge)
                self.bridgeList.remove(bridge)
            except:
                raise BridgeException("Unable to delete linux bridge.")
            return True
        else:
            return False
    
    def addIP(self, bridge, ipv4, netmask='255.255.255.0'):
        if bridge in self.bridgeList:
            try:
                ifconfig(bridge, 'down')
                ifconfig(bridge, ipv4, 'netmask', netmask, 'up')
            except:
                raise IPException("Bridge IP assignment failed.")
            return True
        else:
            raise BridgeException("Bridge not found.")
            return False            
    
    def delIP(self, bridge):
        if bridge in self.bridgeList:
            try:
                ifconfig(bridge, 'down')
                ifconfig(bridge, 'up', '0.0.0.0')
            except:
                raise IPException("Bridge IP removal failed.")
            return True
        else:
            raise BridgeException("Bridge not found.") 
            return False            
    
    def addIf(self, bridge, devices):
        if bridge in self.bridgeList:
            if type(devices) is list:
                try:
                    ifconfig(bridge, 'down')
                    for device in devices:
                        ifconfig(device, 'down')
                        brctl.addif(bridge, device)
                        ifconfig(device, 'up')
                    ifconfig(bridge, 'up')
                except:
                    raise BridgeException("Interface assignment failed.")
            else:
                try:
                    ifconfig(bridge, 'down')
                    ifconfig(devices, 'down')
                    brctl.addif(bridge, devices)
                    ifconfig(devices, 'up')
                    ifconfig(bridge, 'up')
                except:
                    raise BridgeException("Interface assignment failed.")
            return True
        else:
            raise BridgeException("Bridge not found.")
            return False            
        
    def delIf(self, bridge, devices):
        if bridge in self.bridgeList:
            if type(devices) is list:
                try:
                    ifconfig(bridge, 'down')
                    for device in devices:
                        ifconfig(device, 'down')
                        brctl.delif(bridge, device)
                        ifconfig(device, 'up')
                    ifconfig(bridge, 'up')
                except:
                    raise BridgeException("Interface assignment failed.")
            else:
                try:
                    ifconfig(bridge, 'down')
                    ifconfig(devices, 'down')
                    brctl.delif(bridge, devices)
                    ifconfig(devices, 'up')
                    ifconfig(bridge, 'up')
                except:
                    raise BridgeException("Interface assignment failed.")
            return True
        else:
            raise BridgeException("Bridge not found.")
            return False             
            
    def __init__(self):
        self.bridgeList = []
        
    def __del__(self):
        for bridge in self.bridgeList:
            self.destroy(bridge)
            

