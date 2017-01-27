# !/usr/bin/env python

"""
Mini Smart Controller Exception
------------------------------------------------------------
Exception class
"""

__author__ = 'Kenneth A Jones II'
__email__ = 'kenneth@nvnctechnology.com'


class MSCException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)