import os
import sys
import json
import psutil
from easy_struct import *
import systemtime
import hashlib

from debug_tool import Logger, dumpBytes

class ExFAT:
    def __init__(self) -> None:
        self.BPBFirstClusterSector = 0x1000
        self.BPBSectorPerCluster = 0x09

    def ClusterNumberToSectorPos(self, clusterPos):
        return self.BPBFirstClusterSector + (clusterPos - 2) * self.BPBSectorPerCluster
