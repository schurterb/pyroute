# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 12:18:25 2016

@author: schurterb

This class handles routing rules, IPtable, ebtables, etc.
"""

from sh import iptables, ebtables, route
from .networkexceptions import RouteException, RouteWarning


class Manager(object):
    
    def closeIPTables(self):
        iptables('-F')
        iptables('-t', 'nat', '-F')
        iptables('-t', 'mangle', '-F')
        iptables('-P','INPUT','DROP')
        iptables('-P','FORWARD','DROP')
        iptables('-P','OUTPUT','DROP')
        
    def setDefaultGW(self, defaultGW='nodebridge'):
        try:
            route('del', 'default', 'gw', '0.0.0.0')
        except:
            print("Warning: no default gateway")
        finally:
            route('add', 'default', 'gw', defaultGW)
    
    def __init__(self, interface='eth0', **kwargs):
        self.interface = interface
        self.openPorts = []
        self.forwardedPorts = {}
        self.masqedIPs = {}
        self.portForwarding = False
    
    def __del__(self):
        pass
    
    def _enact(self, rule, rule_type='ip'):
        if rule_type == 'route':
            try:
                route(rule)
            except:
                raise RouteException("Invalid route command: " + ' '.join(rule))
        elif rule_type == 'mac':
            try:
                ebtables(rule)
            except:
                raise RouteException("Invalid route command: " + ' '.join(rule))
        else:
            try:
                iptables(rule)
            except:
                raise RouteException("Invalid route command: " + ' '.join(rule))
    
    def openPort(self, port, conn_type = 'tcp', insert_point=None):
        if insert_point is not None:
            rule = ['-I', 'INPUT', str(insert_point)]
        else:
            rule = ['-A', 'INPUT']            
        rule += ['-p',conn_type,'--dport', str(port), '-i', self.interface, '-j', 'ACCEPT']
        self._enact(rule)
        return True
    
    def closePort(self, port, conn_type = 'tcp'):
        rule = ['-D', 'INPUT']
        rule += ['-p',conn_type,'--dport', str(port), '-i', self.interface, '-j', 'ACCEPT']
        self._enact(rule)
        return True
    
    def togglePortFowarding(self, state):
        try:
            f = open('/proc/sys/net/ipv4/ip_forward', 'w')
        except:
            RouteException("You must be root to set ip_forwarding")
        if state:
            self.portForwarding = state
            f.write('1')
        else:
            self.portForwarding = state
            f.write('0')
    
    def setIPMasq(self, masqIP, port, hiddenIP, device='eth0'):
        rule = ['-t', 'nat', '-A', 'PREROUTING', '-i', device, '-p', 'tcp', '-d', masqIP+'/32', '--dport', port, '-j', 'DNAT', '--to-destination', hiddenIP+':'+port]
        self._enact(rule, 'ip')
    
    def dropIPMasq(self, masqIP, port, hiddenIP, device='eth0'):
        rule = ['-t', 'nat', '-D', 'PREROUTING', '-i', device, '-p', 'tcp', '-d', masqIP+'/32', '--dport', port, '-j', 'DNAT', '--to-destination', hiddenIP+':'+port]
        self._enact(rule, 'ip')
    
    def setMACMasq(self, masqMAC, hiddenMAC, IP):
        #make all packets from the hidden mac look like they are comming from the masqueraded mac
        rule1 = ['-t', 'nat', '-A', 'POSTROUTING', '-s', hiddenMAC, '-j', 'snat', '--to-source', masqMAC, '--snat-arp']
        #make all pacekts to the hidden mac's associated IP go to the hidden mac
        rule2 = ['-t', 'nat', '-A', 'PREROUTING', '-p', 'ipv4', '--ip-dst', IP, '-j', 'dnat', '--to-destination', hiddenMAC]
        #make all arp replies for the hidden mac's IP reference the masqueraded mac
        rule3 = ['-t', 'nat', '-A', 'PREROUTING', '-p', 'arp', '--arp-opcode', 'request', '--arp-ip-dst', IP, '-j', 'arpreply', '--arpreply-mac', masqMAC, '--arpreply-target', 'ACCEPT']
        #make all replies to arp requests from the hidden mac location be directed to the hidden mac's location
        rule4 = ['-t', 'nat', '-A', 'PREROUTING', '-p', 'arp', '--arp-opcode', 'reply', '--arp-ip-dst', IP, '-j', 'dnat', '--to-destination', hiddenMAC]
        self._enact(rule1, 'mac')
        self._enact(rule2, 'mac')
        self._enact(rule3, 'mac')
        self._enact(rule4, 'mac')
        return True
    
    def dropMACMasq(self, masqMAC, hiddenMAC, IP):
        #undo making all packets from the hidden mac look like they are comming from the masqueraded mac
        rule1 = ['-t', 'nat', '-D', 'POSTROUTING', '-s', hiddenMAC, '-j', 'snat', '--to-source', masqMAC, '--snat-arp']
        #undo making all pacekts to the hidden mac's associated IP go to the hidden mac
        rule2 = ['-t', 'nat', '-D', 'PREROUTING', '-p', 'ipv4', '--ip-dst', IP, '-j', 'dnat', '--to-destination', hiddenMAC]
        #undo making all arp replies for the hidden mac's IP reference the masqueraded mac
        rule3 = ['-t', 'nat', '-D', 'PREROUTING', '-p', 'arp', '--arp-opcode', 'request', '--arp-ip-dst', IP, '-j', 'arpreply', '--arpreply-mac', masqMAC, '--arpreply-target', 'ACCEPT']
        #undo making all replies to arp requests from the hidden mac location be directed to the hidden mac's location
        rule4 = ['-t', 'nat', '-D', 'PREROUTING', '-p', 'arp', '--arp-opcode', 'reply', '--arp-ip-dst', IP, '-j', 'dnat', '--to-destination', hiddenMAC]
        self._enact(rule1, 'mac')
        self._enact(rule2, 'mac')
        self._enact(rule3, 'mac')
        self._enact(rule4, 'mac')
        return True
    
    def addRoute(self, subnet, netmask, gateway, device=None):
        rule = ['add', '-net', subnet, 'netmask', netmask, 'gw', gateway]
        if device is not None:
            rule += ['dev', device]
        self._enact(rule, 'route')
    
    def delRoute(self, subnet, netmask, device=None):
        rule = ['del', '-net', subnet, 'netmask', netmask]
        if device is not None:
            rule += ['dev', device]
        self._enact(rule, 'route')