# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 18:34:29 2016

@author: schurterb

A set of exceptions for the pyroute networking managers.
"""

#import Exception

#An error raised by failed bridge operations
class BridgeException(Exception):
    def __init__(self, msg, *args):
        self.message = msg
        
#An error raised by failed IP operations
class IPException(Exception):
    def __init__(self, msg, *args):
        self.message = msg
        
#An error raised by an invalid routing rule
class RouteException(Exception):
    def __init__(self, msg, *args):
        self.message = msg
        
#An error raised by an invalid routing rule
class RouteWarning(Warning):
    def __init__(self, msg, *args):
        self.message = msg