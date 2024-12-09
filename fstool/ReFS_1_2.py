import os
import sys
import json
import psutil
from easy_struct import *
import systemtime
import hashlib

from debug_tool import Logger, dumpBytes


"""
ReFS v1.2 

see https://gist.github.com/XenoPanther/15d8fad49fbd51c6bd946f2974084ef8
ReFS 1.2
    Version of formatted by Windows 8.1, Windows 10 v1507 to v1607, Windows Server 2012 R2, 
and when specified ReFSv1 on Windows Server 2016 or later.
    Cannot use alternate data streams, when mount on 2012.

需要导入以下注册表项才能在资源管理器里面格式化：

Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\MiniNT]
"AllowRefsFormatOverNonmirrorVolume"=dword:00000001

[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem]
"RefsDisableLastAccessUpdate"=dword:00000000

"""

REFS_BPB_FSNAME = b"ReFS\x00\x00\x00\x00"
REFS_BPB_IDENTIFIER = b"FSRS"


class ReFS_BPB:
    def __init__(self, buf: bytes):
        # hex 3   "3 Jmp (Jump instructions)"
        self.Jmp = easyunpack().putString(3).get(buf[0:3])[0]
        # char[8] "8 FSName"
        self.FSName = easyunpack().putString(8).get(buf[3:11])[0]
        # hex 5   "5 MustBeZero"
        self.MustBeZero = easyunpack().putString(5).get(buf[11:16])[0]
        # uint32  "4 Identifier"
        self.Identifier = easyunpack().putString(4).get(buf[16:20])[0]
        # uint16  "2 Length (of FSRS)"
        self.LengthOfFSRS = easyunpack().putUShort().get(buf[20:22])[0]
        # uint16  "2 Checksum (of FSRS)"
        self.ChecksumOfFSRS = easyunpack().putUShort().get(buf[22:24])[0]
        # int64   "8 Sectors in volume"
        self.SectorsInVolume = easyunpack().putUInt64().get(buf[24:32])[0]
        # uint32  "4 Bytes per sector"
        self.BytesPerSector = easyunpack().putUInt().get(buf[32:36])[0]
        # uint32  "4 Sectors per cluster"
        self.SectorsPerCluster = easyunpack().putUInt().get(buf[36:40])[0]
        self.BytesPerCluster = self.BytesPerSector * self.SectorsPerCluster
        # int8    "1 File system major version"
        self.FileSystemMajorVersion = easyunpack().putUChar().get(buf[40:41])[0]
        # int8    "1 File system minor version"
        self.FileSystemMinorVersion = easyunpack().putUChar().get(buf[41:42])[0]
        # hex 14  "14 Unknown"
        self.Unknown = easyunpack().putString(14).get(buf[42:56])[0]
        # hex 8   "8 Volume Serial Number"
        self.VolumeSerialNumber = easyunpack().putString(8).get(buf[56:64])[0]
        # ReFS v1.2 contaner size is always 0x4000 sectors
        self.ContainerBytes = 0x4000
        self.ContainerCluster = self.ContainerBytes // self.BytesPerSector

    def __str__(self) -> str:
        s = f"Jmp = {self.Jmp}\n"
        s += f"FSName = {self.FSName}\n"
        s += f"MustBeZero = {self.MustBeZero}\n"
        s += f"Identifier = {self.Identifier}\n"
        s += f"LengthOfFSRS = {self.LengthOfFSRS}\n"
        s += f"ChecksumOfFSRS = {self.ChecksumOfFSRS}\n"
        s += f"SectorsInVolume = {self.SectorsInVolume}\n"
        s += f"BytesPerSector = {self.BytesPerSector}\n"
        s += f"SectorsPerCluster = {self.SectorsPerCluster}\n"
        s += f"FileSystemMajorVersion = {self.FileSystemMajorVersion}\n"
        s += f"FileSystemMinorVersion = {self.FileSystemMinorVersion}\n"
        s += f"Unknown = {self.Unknown}\n"
        s += f"VolumeSerialNumber = {self.VolumeSerialNumber}\n"
        return s

    def isValid(self):
        return (
            self.FSName == REFS_BPB_FSNAME
            and self.Identifier == REFS_BPB_IDENTIFIER
            and self.SectorsInVolume > 0
            and self.SectorsPerCluster > 0
            and self.BytesPerSector > 0
            and self.BytesPerSector % 512 == 0
            and self.FileSystemMajorVersion == 1
            and self.FileSystemMinorVersion == 2
        )

    def clusterToByte(self, cluster: int):
        return self.BytesPerCluster * cluster

    def byteToCluster(self, b: int):
        return b // self.BytesPerCluster

    def sectorToByte(self, sec: int):
        return sec * self.BytesPerSector

    def byteToSector(self, b: int):
        return b // self.BytesPerSector

    def getTotalCluster(self):
        return self.SectorsInVolume // self.SectorsPerCluster

    def blockToByte(self, blockNumber: int):
        return blockNumber * self.ContainerBytes

    def blockToSector(self, blockNumber: int):
        return blockNumber * self.ContainerBytes // self.BytesPerSector


# header of all special block in the ReFS, such as SUBP, CHKP, MSB+...
class ReFS_MetadataBlockHeader:
    def __init__(self, buf: bytes) -> None:
        self.blockNumber, self.identifier, self.unknown0, self.flags, self.unknown1 = (
            easyunpack()
            .putUInt64()
            .putString(16)
            .putUInt64()
            .putUInt64()
            .putUInt64()
            .get(buf[:48])
        )

    @staticmethod
    def size():
        return 48


class ReFS_BlockReference:
    def __init__(self, buf: bytes) -> None:
        (
            self.blockNumber,
            self.unknown0,
            self.checksumType,
            self.checksumOffset,
            self.checksumSize,
            self.unknown1,
            self.checksum,
        ) = (
            easyunpack()
            .putUInt64()
            .putUShort()
            .putUChar()
            .putUChar()
            .putUShort()
            .putUShort()
            .putString(8)
            .get(buf[:24])
        )

    def getSector(self, bpb: ReFS_BPB):
        blockSectorPos = self.blockNumber * bpb.ContainerBytes // bpb.BytesPerSector
        return blockSectorPos

    def __str__(self) -> str:
        return f"[ReFS_BlockReference] {self.blockNumber}"

    @staticmethod
    def size():
        return 24


# SUPB(super block) enterance of the ReFS file system, help to find CHKP position
# always located at container number 0x1E, which is 0x1E*0x4000//512 = 960 (sector pos)
class ReFS_SUPB:
    def __init__(self, buf: bytes) -> None:
        self.metadataBlockHeader = ReFS_MetadataBlockHeader(buf)
        offset = ReFS_MetadataBlockHeader.size()
        (
            self.uuid,
            self.unknow0,
            self.sequenceNumber,
            self.checkpointRefOffset,
            self.checkpointRefCount,
            self.selfRefDataOffset,
            self.selfRefDataSize,
        ) = (
            easyunpack()
            .putString(16)
            .putUInt64()
            .putUInt64()
            .putUInt()
            .putUInt()
            .putUInt()
            .putUInt()
            .get(buf[offset : offset + 48])
        )

        offset = self.checkpointRefOffset
        self.checkpointPos = []
        for i in range(self.checkpointRefCount):
            self.checkpointPos.append(
                easyunpack().putUInt64().get(buf[offset : offset + 8])[0]
            )
            offset += 8

        self.selfBlockRef = ReFS_BlockReference(buf[offset:])

    def isValid(self):
        return self.metadataBlockHeader.blockNumber == 0x1E


class ReFS_CheckPointHeader:
    def __init__(self, buf: bytes) -> None:
        offset = 4
        self.majorVer = easyunpack().putUShort().get(buf[offset : offset + 2])[0]
        offset += 2
        self.minorVer = easyunpack().putUShort().get(buf[offset : offset + 2])[0]
        offset += 2
        self.selfRefDataOffset = easyunpack().putUInt().get(buf[offset : offset + 4])[0]
        offset += 4
        self.selfRefDataSize = easyunpack().putUInt().get(buf[offset : offset + 4])[0]

    @staticmethod
    def size():
        return 16


class ReFS_CheckPointTrailer:
    def __init__(self, buf: bytes) -> None:
        (
            self.lastWriteSequenceNumber,
            self.chkpDataSize,
            self.unknown0,
            self.unknown1,
            self.numberOfOffsets,
        ) = (
            easyunpack()
            .putUInt64()
            .putUInt()
            .putUInt()
            .putUInt64()
            .putUInt()
            .get(buf[:28])
        )
        offset = 28
        self.offsets = []
        for i in range(self.numberOfOffsets):
            n = easyunpack().putUInt().get(buf[offset : offset + 4])[0]
            offset += 4
            self.offsets.append(n)

    def size(self):
        return 48 + 4 + 4 * len(self.offsets)


# CHKP(check point) in ReFS, which is the level 0 (root node) of the entire ReFS tree system
class ReFS_CHKP:
    """
    Metadata block header
    Checkpoint header
    Checkpoint trailer
    Self metadata block reference
    Ministore tree metadata block references
    """

    def __init__(self, blockNumber, refs) -> None:
        self.blockNumber = blockNumber
        self.sectorPos = refs.BPB.blockToSector(blockNumber)
        self.metadataBlockHeader = None
        refs.fp.seek(self.sectorPos * refs.BPB.BytesPerSector)
        buf: bytes = bytes(refs.fp.read(refs.BPB.BytesPerCluster))
        if len(buf) != refs.BPB.BytesPerCluster:
            Logger.err("[ReFS_CHKP] error read disk")
            return
        self.metadataBlockHeader = ReFS_MetadataBlockHeader(buf)
        if self.metadataBlockHeader.blockNumber != blockNumber:
            Logger.err("[ReFS_CHKP] not a CHKP block")
            return
        offset = ReFS_MetadataBlockHeader.size()
        self.chkpHeader = ReFS_CheckPointHeader(buf[offset:])
        offset += ReFS_CheckPointHeader.size()
        self.chkpTrailer = ReFS_CheckPointTrailer(buf[offset:])
        offset = self.chkpHeader.selfRefDataOffset
        self.metadataBlockRef = ReFS_BlockReference(buf[offset:])
        offset = self.chkpHeader.selfRefDataOffset + self.chkpHeader.selfRefDataSize
        """
        0 Objects tree
        1 Medium allocator tree
        2 Container allocator tree
        3 Schema tree
        4 Parent-child relationship tree
        5 Copy of object tree
        6 Block reference count tree
        Seen in format version 3
        7 Container tree
        8 Copy of container tree
        9 Copy of schema tree
        10 Container index tree
        11 Integrity state tree
        12 Small allocator tree
        """
        self.msbTreeRef = []
        for i, offset in enumerate(self.chkpTrailer.offsets):
            ref = ReFS_BlockReference(buf[offset:])
            Logger.info(f"[{i}][{offset}] MSB+ secotr pos: {ref.blockNumber}")
            self.msbTreeRef.append(ref)

    def isValid(self):
        return (
            self.metadataBlockHeader
            and self.metadataBlockHeader.blockNumber == self.blockNumber
            and self.chkpTrailer
            and self.chkpTrailer.offsets
        )


# ??not found in ReFS 3.4
class ReFS_TreeHeader:
    def __init__(self, buf: bytes) -> None:
        self.offsetToTreeData = easyunpack().putUInt().get(buf[0:4])[0]
        offset = 4
        pass

    @staticmethod
    def size():
        return 36


# header help to load NodeRecords in the MSB+
class ReFS_NodeHeader:
    # 0 == leaf
    NODE_TYPE_LEAF = 0x00
    # 1 == branch node, all file entry record data is a ReFS_MetadataBlockReference, need to load sub-MBSP
    NODE_TYPE_BRANCH = 0x01
    # 2 == root
    NODE_TYPE_ROOT = 0x02
    # 4 == is deleted?? is stream??
    NODE_TYPE_DELETED = 0x04

    def __init__(self, buf: bytes) -> None:
        self.dataStartOffset = easyunpack().putUInt().get(buf[0:4])[0]
        offset = 4
        self.dataEndOffset = easyunpack().putUInt().get(buf[offset : offset + 4])[0]
        offset += 4
        self.dataSize = easyunpack().putUInt().get(buf[offset : offset + 4])[0]
        offset += 4
        self.nodeLevel = easyunpack().putUChar().get(buf[offset : offset + 1])[0]
        offset += 1
        self.nodeType = easyunpack().putUChar().get(buf[offset : offset + 1])[0]
        offset += 1
        # skip 2
        offset += 2
        self.recordStartOffset = easyunpack().putUInt().get(buf[offset : offset + 4])[0]
        offset += 4
        self.recordCount = easyunpack().putUInt().get(buf[offset : offset + 4])[0]
        offset += 4
        self.recordEndOffset = easyunpack().putUInt().get(buf[offset : offset + 4])[0]
        offset += 4

    def isBranchNode(self):
        return self.nodeType == 0x01

    def isRootNode(self):
        return self.nodeType == 0x02

    def isStreamNode(self):
        return self.nodeType == 0x04

    @staticmethod
    def size():
        return 32


# tree index,
# block number follow contaner tree
REFS_OBJECTS_TREE = 0
#
REFS_MEDIUM_ALLOCATOR_TREE = 1
#
REFS_CONTAINER_ALLOCATOR_TREE = 2
#
REFS_SCHEMA_TREE = 3
#
REFS_PARENT_CHILD_RELATIONSHIP_TREE = 4
#
REFS_COPY_OF_OBJECT_TREE = 5
#
REFS_BLOCK_REFERENCE_COUNT_TREE = 6
# block number to container tree equals to cluster
REFS_CONTAINER_TREE = 7
#
REFS_COPY_OF_CONTAINER_TREE = 8
#
REFS_COPY_OF_SCHEMA_TREE = 9
#
REFS_CONTAINER_INDEX_TREE = 10
#
REFS_INTEGRITY_STATE_TREE = 11
#
REFS_SMALL_ALLOCATOR_TREE = 12

REFS_NODE_RECORD_KEY_ROOT_DIR = (
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00"
)
REFS_NODE_RECORD_KEY_VOLUME_INFOMATION = (
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00"
)
# the node record data is ref and the ref-msbp contains the extended-node-records of current msbp
REFS_NODE_RECORD_FLAG_IS_EXTENDED = 0x01
# the node record is deleted
REFS_NODE_RECORD_FLAG_IS_DELETED = 0x04
# [uncheck] ?? the node record contains an embedded MSB+ ??
REFS_NODE_RECORD_FLAG_EMBEDDED_MSBP = 0x08


# node record, could be a leaf/branch/root node store in the MSB+
class ReFS_NodeRecord:
    def __init__(self, buf: bytes) -> None:
        self.recordSize = easyunpack().putUInt().get(buf[0:4])[0]
        offset = 4
        self.keyDataOffset = easyunpack().putUShort().get(buf[offset : offset + 2])[0]
        offset += 2
        self.keyDataSize = easyunpack().putUShort().get(buf[offset : offset + 2])[0]
        offset += 2
        self.flags = easyunpack().putUShort().get(buf[offset : offset + 2])[0]
        offset += 2
        self.valueDataOffset = easyunpack().putUShort().get(buf[offset : offset + 2])[0]
        offset += 2
        self.valueDataSize = easyunpack().putUShort().get(buf[offset : offset + 2])[0]
        self.keyData = buf[self.keyDataOffset : self.keyDataOffset + self.keyDataSize]
        self.valData = buf[
            self.valueDataOffset : self.valueDataOffset + self.valueDataSize
        ]

    def __str__(self) -> str:
        return f"NodeRecord with key: " + dumpBytes(self.keyData)


# file name attributes
class ReFS_FNA:
    def __init__(self, buf: bytes) -> None:
        self.size = easyunpack().putUInt().get(buf[:4])[0]
        self.timeOffset = easyunpack().putUShort().get(buf[4 : 4 + 2])[0]
        (
            self.createTime,
            self.modifyTime,
            self.metadataModifyTime,
            self.accessTime,
            self.attr,
            self.parentId,
            self.fileId,
            self.unknown0,
            self.filesize,
        ) = (
            easyunpack()
            .putUInt64()
            .putUInt64()
            .putUInt64()
            .putUInt64()
            .putUInt64()
            .putUInt64()
            .putUInt64()
            .putString(0x8)
            .putUInt64()
            .get(buf[self.timeOffset : self.timeOffset + 72])
        )

# a header before datarun record, do not know what it is
class ReFS_FNANodeHeader:
    def __init__(self, buf: bytes) -> None:
        self.size = easyunpack().putUInt().get(buf[:4])[0]
        self.unknown = buf[4 : self.size]


class ReFS_FileRecord_DataDescriptor:
    def __init__(self, buf: bytes) -> None:
        self.size = easyunpack().putUInt().get(buf[:4])[0]
        self.allocSize, self.fileSize, self.fileSize1 = (
            easyunpack().putUInt64().putUInt64().putUInt64().get(buf[0x34 : 0x34 + 24])
        )


class ReFS_FileRecord_DataRunHeader:
    def __init__(self, buf: bytes) -> None:
        (
            self.size,
            self.unknown0,
            self.unknown1,
            self.unknown2,
            self.unknown3,
            self.datarunCount,
            self.unknown4,
        ) = (
            easyunpack()
            .putUInt()
            .putUInt()
            .putUInt()
            .putUInt()
            .putUInt()
            .putUInt()
            .putUInt64()
            .get(buf[:32])
        )


# file data run, require ReFS_ContainerTree to translate into cluster pos
class ReFS_FileRecord_DataRunItem:
    def __init__(self, buf: bytes) -> None:
        self.rec = ReFS_NodeRecord(buf)
        self.flag, self.clusterCount, self.datarun, self.type = (
            easyunpack()
            .putUInt64()
            .putUInt64()
            .putUInt64()
            .putUInt64()
            .get(self.rec.valData[:32])
        )

    def __str__(self) -> str:
        return (
            f"[DataRun] BlockNumber: {self.datarun}, ClusterCount: {self.clusterCount}"
        )

    def __eq__(self, value: object) -> bool:
        return self.datarun == value.datarun

    def size(self):
        return self.rec.recordSize


#
class ReFS_FileRecord_DataRunList:
    def __init__(self, buf: bytes) -> None:
        self.size = len(buf)
        self.datarun = []
        self.fnaDataRunHeader = ReFS_FileRecord_DataRunHeader(buf)
        offset = len(buf) - 4
        index = buf[offset : offset + 4]
        while offset > self.fnaDataRunHeader.size and offset < len(buf):
            if index[-2:] != b"\x00\x00":
                break
            pos = easyunpack().putUShort().get(index[:2])[0]
            if pos < self.fnaDataRunHeader.size or pos > len(buf):
                break
            datarun = ReFS_FileRecord_DataRunItem(buf[pos:])
            if datarun in self.datarun:
                Logger.warn(
                    f"[ReFS_FNADataRunList] this record repeat?? {datarun.datarun}"
                )
            else:
                self.datarun.insert(0, datarun)
            offset -= 4
            index = buf[offset : offset + 4]


# part of ReFS_FileRecord
# is a ReFS_NodeRecord
# key contains a parentId and attribute type?
# value contains a DataRun-Descriptor and DataRun-List
class ReFS_FileRecord_DataRecord:
    def __init__(self, buf: bytes) -> None:
        self.rec = ReFS_NodeRecord(buf)
        self.parentId = self.rec.keyData[:8]
        self.attrType = self.rec.keyData[8:4]
        self.dataDesc = ReFS_FileRecord_DataDescriptor(self.rec.valData)
        offset = self.dataDesc.size
        self.dataRunList = ReFS_FileRecord_DataRunList(self.rec.valData[offset:])


# leaf node of DirTree, holds infomation of a file
class ReFS_FileRecord:
    def __init__(self, base: ReFS_NodeRecord) -> None:
        self.path = ""
        # key
        self.fileName = base.keyData[4 : base.keyDataSize].decode(
            "utf-16", errors="replace"
        )
        # FNA
        buf = base.valData
        # file name attributes A8 00 ....
        self.fna = ReFS_FNA(buf)
        offset = self.fna.size
        if len(buf) < offset or offset >= len(buf) - 8:
            Logger.err("debug: empty data")
            self.dataSize = 0
            return
        # FNA node header 20 00 ....
        self.fnaNodeHeader = ReFS_FNANodeHeader(buf[offset:])
        offset += self.fnaNodeHeader.size
        # FNA Data attribute 80 01 ....
        self.dataRunRec = ReFS_FileRecord_DataRecord(buf[offset:])
        offset += self.dataRunRec.rec.recordSize


# leaf node of DirTree, holds infomation of a direcory
class ReFS_DirRecord:
    def __init__(self, base: ReFS_NodeRecord) -> None:
        self.path = ""
        self.fileName = base.keyData[4 : base.keyDataSize].decode(
            "utf-16", errors="replace"
        )
        # 这个版本的id貌似只有8字节，而ReFS_ObjectTree.findObjectRecordByKey需要16字节的key
        # 所以为了方便查找，补回16字节
        self.filesystemIdentifier = (b"\x00" * 8) + base.valData[0:8]
        self.createTime, self.modifyTime, self.entryModifyTime, self.accessTime = (
            easyunpack()
            .putUInt64()
            .putUInt64()
            .putUInt64()
            .putUInt64()
            .get(base.valData[16 : 16 + 32])
        )
        self.attrs = easyunpack().putUInt().get(base.valData[64 : 64 + 4])[0]


# branch record in a MSB+ tree node, found in ReFS_ObjectTree, ReFS_ContainerTree
class ReFS_MSBP_BranchRecord:
    def __init__(self, base: ReFS_NodeRecord) -> None:
        if not base.keyData or base.keyDataSize < 16:
            raise Exception(
                "[ReFS_ObjectTree_BranchRecord] not a ReFS_ObjectTree_BranchRecord object"
            )
        self.objectKey = easyunpack().putUInt64().putUInt64().get(base.keyData)
        self.metaDataBlockReference = ReFS_BlockReference(base.valData)

    def __lt__(self, r):
        return self.objectKey[1] < r.objectKey[1]

    def __gt__(self, r):
        return self.objectKey[1] > r.objectKey[1]

    def __eq__(self, r):
        return self.objectKey[1] == r.objectKey[1]


# leaf directory record return by ReFS_ObjectTree.findObjectRecordByKey()
class ReFS_ObjectTree_DirRecord:
    def __init__(self, base: ReFS_NodeRecord) -> None:
        self.metaDataBlockReference = ReFS_BlockReference(base.valData)
        # unknowns...


# all we concern is the object tree, which store all infomation of files and directories
class ReFS_ObjectTree:
    def __init__(self, ref: ReFS_BlockReference, refs) -> None:
        self.refs = refs
        self.rootRef = ref
        self.rootSec = refs.BPB.blockToSector(ref.blockNumber)
        self.bpb = refs.BPB
        self.fp = refs.fp
        self.blockNumbers = []
        self.blockBuffers = {}
        self.blockBufferSize = 0

    def findRootDir(self):
        return self.findObjectRecordByKey(REFS_NODE_RECORD_KEY_ROOT_DIR)

    def findObjectRecordByKey(self, objkey: bytes):
        if len(objkey) != 16:
            raise Exception("[ReFS_ObjectTree] objkey must be 16-bytes-length")
        self.keyToFind = easyunpack().putUInt64().get(objkey[8:])[0]
        return self._loadSec(self.rootRef)

    def _loadSec(self, ref: ReFS_BlockReference):
        secPos = self.bpb.blockToSector(ref.blockNumber)
        Logger.info(f"[ReFS_ObjectTree] MSBP goto sub sec: {secPos}")
        if not secPos:
            return
        if secPos == 58400:
            print("debug")
        buf = bytearray()
        if secPos in self.blockBuffers:
            buf = self.blockBuffers[secPos]
        else:
            self.fp.seek(self.bpb.sectorToByte(secPos), 0)
            buf.extend(self.fp.read(self.bpb.BytesPerCluster))
            if buf:
                self.blockBuffers[secPos] = buf
                self.blockNumbers.append(secPos)
                self.blockBufferSize += len(buf)
                while self.blockBufferSize > (32 << 20):
                    sec = self.blockNumbers.pop(0)
                    self.blockBufferSize -= len(self.blockBuffers[sec])
                    self.blockBuffers.pop(sec)
        if buf:
            # self._load(bytes(buf), bpb, fp, nodeRecords)
            return self._loadBuf(bytes(buf), ref)
        return None

    def _loadBuf(self, buf, ref: ReFS_BlockReference):
        metadataBlockHeader = ReFS_MetadataBlockHeader(buf)
        if metadataBlockHeader.blockNumber != ref.blockNumber:
            Logger.err("[ReFS_ObjectTree] error not a MSB+ ref buf")
            return None
        offset = ReFS_MetadataBlockHeader.size()
        nodeHeaderOffset = (
            easyunpack().putUInt().get(buf[offset : offset + 4])[0] + offset
        )
        # offset += 4
        # treeHeader = ReFS_TreeHeader(buf[offset:])
        nodeHeader = ReFS_NodeHeader(buf[nodeHeaderOffset:])
        offset = nodeHeaderOffset + nodeHeader.dataStartOffset
        recordCount = 0
        subMSBPRefs = []
        branch = None
        while recordCount < nodeHeader.recordCount:
            rec = ReFS_NodeRecord(buf[offset:])
            if rec.flags & 0x04:
                Logger.info(f"[ReFS_ObjectTree] this record is deleted")
            else:
                recordCount += 1
                if nodeHeader.nodeType & ReFS_NodeHeader.NODE_TYPE_BRANCH:
                    # sub MSBP
                    if rec.valueDataSize != ReFS_BlockReference.size():
                        Logger.err("[ReFS_ObjectTree] error bad logic")
                    else:
                        if rec.keyDataSize == 16:
                            branch = ReFS_MSBP_BranchRecord(rec)
                            # subMSBPRefs.append(branch.metaDataBlockReference)
                            if branch.objectKey[1] >= self.keyToFind:
                                subMSBPRefs.append(branch.metaDataBlockReference)
                            else:
                                Logger.warn(f"[ReFS_ObjectTree] skip branch {rec}")
                else:
                    if (
                        easyunpack().putUInt64().get(rec.keyData[8:])[0]
                        == self.keyToFind
                    ):
                        Logger.info(f"[ReFS_ObjectTree] MSBP got: {rec}")
                        return rec
                    # Logger.info(f"MSBP skip: {rec}")
            offset += rec.recordSize
            if offset >= len(buf):
                break
        # if branch and not subMSBPRefs:
        #    subMSBPRefs.append(branch.metaDataBlockReference)
        for ref in subMSBPRefs:
            Logger.warn(f"[ReFS_ObjectTree] MSBP goto sub msbp: {ref.blockNumber}")
            ret = self._loadSec(ref)
            if ret:
                return ret
        return None


# load MSB+ as directory tree leaf node
class ReFS_MSBP_DirTreeNode:
    def __init__(self, refs):
        self.refs = refs
        self.bpb = refs.BPB
        self.fp = refs.fp
        self.nodeRecords = []

    def load(self, ref: ReFS_BlockReference) -> None:
        self.ref = ref
        self._load(ref)

    def _loadBuf(self, buf, ref: ReFS_BlockReference):
        metadataBlockHeader = ReFS_MetadataBlockHeader(buf)
        if metadataBlockHeader.blockNumber != ref.blockNumber:
            Logger.err("[ReFS_DirTreeNode] not a MSB+ ref buf")
            return
        offset = ReFS_MetadataBlockHeader.size()
        nodeHeaderOffset = (
            easyunpack().putUInt().get(buf[offset : offset + 4])[0] + offset
        )
        # offset += 4
        # treeHeader = ReFS_TreeHeader(buf[offset:])
        nodeHeader = ReFS_NodeHeader(buf[nodeHeaderOffset:])
        offset = nodeHeaderOffset + nodeHeader.dataStartOffset
        recordCount = 0
        subMSBPRefs = []
        while recordCount < nodeHeader.recordCount:
            rec = ReFS_NodeRecord(buf[offset:])
            if rec.flags & 0x04:
                Logger.info(f"[ReFS_DirTreeNode] this record is deleted")
            else:
                recordCount += 1
                if nodeHeader.nodeType & ReFS_NodeHeader.NODE_TYPE_BRANCH:
                    # sub MSBP
                    if rec.valueDataSize != ReFS_BlockReference.size():
                        Logger.err("[ReFS_DirTreeNode] error bad logic")
                    else:
                        ref = ReFS_BlockReference(rec.valData)
                        subMSBPRefs.append(ref)
                else:
                    Logger.info(f"[ReFS_DirTreeNode] MSBP got: {rec}")
                    self.nodeRecords.append(rec)
            offset += rec.recordSize
            if offset >= len(buf):
                break

        for ref in subMSBPRefs:
            Logger.warn(f"[ReFS_DirTreeNode] MSBP goto sub msbp: {ref.blockNumber}")
            self._load(ref)

        Logger.info(f"[ReFS_DirTreeNode] MSBP load end")

    def _load(self, ref: ReFS_BlockReference):
        secPos = self.bpb.blockToSector(ref.blockNumber)
        Logger.err(f"[ReFS_DirTreeNode] MSBP goto sub sec: {secPos}")
        if secPos == 58400:
            print("debug")
        buf = bytearray()
        self.fp.seek(self.bpb.sectorToByte(secPos), 0)
        buf.extend(self.fp.read(self.bpb.BytesPerCluster))
        if buf:
            self._loadBuf(bytes(buf), ref)


class ReFS:
    def __init__(self) -> None:
        self.fp = None
        self.BPB = None
        self.SUPB = None
        self.CHKP = [0] * 2
        self.MSBP = [0] * 13
        self.fileList = []
        self.dirList = []
        # fileName -> cluster
        self.testFileDataSectors = {}
        # blockNumber[0]-> sector-pos
        self.MSBPSectors = {}

    def open(self, partitionLabel: str):
        self.partitionLabel = partitionLabel
        # self.sizeInBytes = psutil.disk_usage(f"{partitionLabel[0]}:").total
        # Logger.info(f"volumn[{partitionLabel}], size: {self.sizeInBytes}")
        # self.diskpath = f"\\\\.\\{partitionLabel[0]}:"

        self.diskpath = r"\\192.168.6.134\Debug\fstool\refs.1.2.ptt"
        self.sizeInBytes = os.stat(self.diskpath).st_size
        Logger.info(f"volumn[{partitionLabel}], size: {self.sizeInBytes}")

        self.fp = open(self.diskpath, "rb")
        self.BPB = ReFS_BPB(self.fp.read(512))
        Logger.info("BPB:")
        Logger.info(self.BPB)

        self.fp.seek(self.sizeInBytes - 512, 0)
        self.BPB2 = ReFS_BPB(self.fp.read(512))
        Logger.info("BPB-Backup:")
        Logger.info(self.BPB2)

        if not self.BPB.isValid():
            Logger.warn("BPB invalid, using BPB-Backup")
            self.BPB = self.BPB2

    def loadSUPB(self):
        if not self.BPB or not self.BPB.isValid():
            raise Exception("error bpb not valid!")
        # we always found the superblock in entry block 0x1E
        self.fp.seek(self.BPB.blockToByte(0x1E), 0)
        self.SUPB = ReFS_SUPB(self.fp.read(self.BPB.clusterToByte(1)))
        if not self.SUPB.isValid():
            Logger.warn("first SUPB is not valid, load the first backup one")
            totalCluster = self.BPB.getTotalCluster()
            self.fp.seek(self.BPB.clusterToByte(totalCluster - 3), 0)
            self.SUPB = ReFS_SUPB(self.fp.read(self.BPB.clusterToByte(1)))
            if not self.SUPB.isValid():
                Logger.warn("first SUPB is not valid, load the second backup one")
                self.SUPB = ReFS_SUPB(self.fp.read(self.BPB.clusterToByte(1)))
                if not self.SUPB.isValid():
                    raise ("no SUPB is valid, abort")

    def loadCHKP(self):
        if not self.SUPB.isValid():
            raise ("no SUPB is valid, abort")
        for i, pos in enumerate(self.SUPB.checkpointPos):
            chkp = ReFS_CHKP(pos, self)
            if not chkp.isValid():
                raise Exception("error find CHKP")
            self.CHKP[i] = chkp
        Logger.info("CHKP load ok!")

    def getCHKP(self) -> ReFS_CHKP:
        return (
            self.CHKP[0]
            if self.CHKP[0].chkpTrailer.lastWriteSequenceNumber
            > self.CHKP[1].chkpTrailer.lastWriteSequenceNumber
            else self.CHKP[1]
        )

    def _dumpObjectTree(self, msbp):
        rec: ReFS_NodeRecord = None
        for rec in msbp.nodeRecords:
            self._dumpObjectRecord(rec, self.partitionLabel + ":\\")
        for submsbp in msbp.subMSBP:
            self._dumpObjectTree(submsbp)

    def isValid(self):
        return self.BPB.isValid()

    def _dumpObjectRecord(self, rec, path: str, ref: ReFS_BlockReference = None):
        # if rec.keyData[0]==0x10:
        #    #base record
        #    Logger.info(f'base-record.key: {rec.keyData}')
        # elif rec.keyData[0]==0x20:
        #    #name record
        #    fileSystemIdentifier=rec.keyData[16:]
        #    Logger.info(f'name-record.fs.id: ' + dumpBytes(fileSystemIdentifier))
        #    nameLen=easyunpack().putUShort().get(rec.valData[10:12])[0]
        #    fileName=rec.valData[12:12+nameLen].decode('utf-16', errors='ignore')
        #    Logger.info(f'name-record.fileName: {fileName}')
        if rec.keyData and rec.keyData[0] == 0x30:
            # entry record
            type = easyunpack().putUShort().get(rec.keyData[2:4])[0]
            typeStr = ["stream", "file", "directory"]
            if type < len(typeStr):
                Logger.warn(f"entry.type: {typeStr[type]}")
            name = rec.keyData[4:].decode("utf-16", errors="replace")
            Logger.err(f"entry.name: {name}")
            Logger.err(f"entry.path: {path}{name}")
            if name == "0.12.txt":
                Logger.err("debug")
            if type == 1:
                fileRec = ReFS_FileRecord(rec)
                Logger.ok(
                    f"file.create-time: {systemtime.formatFILETIME(fileRec.fna.createTime)}\n"
                    + f"file.modify-time: {systemtime.formatFILETIME(fileRec.fna.modifyTime)}\n"
                    + f"file.entry-modify-time: {systemtime.formatFILETIME(fileRec.fna.metadataModifyTime)}\n"
                    + f"file.access-time: {systemtime.formatFILETIME(fileRec.fna.accessTime)}\n"
                    + f"file.alloc-size: {fileRec.dataRunRec.dataDesc.allocSize}\n"
                    + f"file.data-size: {fileRec.dataRunRec.dataDesc.fileSize}"
                )
                for datarunItem in fileRec.dataRunRec.dataRunList.datarun:
                    Logger.ok(f"file.datarun: {datarunItem}")
                if name in self.testFileDataSectors:
                    fileSector = self.testFileDataSectors[name]
                    Logger.warn(
                        f"file.data.sector.searched: {fileSector}/{hex(fileSector)}"
                    )
                    for datarunItem in fileRec.dataRunRec.dataRunList.datarun:
                        datarun = datarunItem.datarun
                        physicalSector = self.bpb.blockToSector(datarun)
                        Logger.ok(f"file.data.sector.calculated:  {physicalSector}")
                        if physicalSector != fileSector:
                            Logger.err(f"error translate file data run")
                        break
                    pass
                fileRec.path = path
                self.fileList.append(fileRec)
            elif type == 2:
                dirRec = ReFS_DirRecord(rec)
                Logger.ok(
                    f"dir.filesystemIdentifier: "
                    + dumpBytes(dirRec.filesystemIdentifier)
                    + "\n"
                    + f"dir.create-time: {systemtime.formatFILETIME(dirRec.createTime)}\n"
                    + f"dir.modify-time: {systemtime.formatFILETIME(dirRec.modifyTime)}\n"
                    + f"dir.entry-modify-time: {systemtime.formatFILETIME(dirRec.entryModifyTime)}\n"
                    + f"dir.access-time: {systemtime.formatFILETIME(dirRec.accessTime)}\n"
                    + "dir.attrs: 0x%08x" % (dirRec.attrs)
                )
                dirRec.path = path
                self.dirList.append(dirRec)

    def traverseRootDir(self):
        # self._searchTestFiles()
        self.fileList.clear()
        self.dirList.clear()
        chkp = self.getCHKP()
        ref: ReFS_BlockReference = chkp.msbTreeRef[REFS_OBJECTS_TREE]
        objTree = ReFS_ObjectTree(ref, self)
        rec = objTree.findObjectRecordByKey(REFS_NODE_RECORD_KEY_ROOT_DIR)
        obj = ReFS_ObjectTree_DirRecord(rec)
        Logger.warn(f"root ref: {obj.metaDataBlockReference.blockNumber}")
        msbp = ReFS_MSBP_DirTreeNode(self)
        msbp.load(obj.metaDataBlockReference)
        self._traverseDir(msbp, objTree, self.partitionLabel + ":\\")
        Logger.ok(
            f"traverseRootDir: found {len(self.fileList)} files, {len(self.dirList)} directories"
        )

    def _traverseDir(
        self, msbp: ReFS_MSBP_DirTreeNode, objTree: ReFS_ObjectTree, path: str
    ):
        self._dumpDirTree(msbp, path)
        for rec in msbp.nodeRecords:
            if rec.keyData and rec.keyData[0] == 0x30:
                type = easyunpack().putUShort().get(rec.keyData[2:4])[0]
                if type == 2:
                    subdir = ReFS_DirRecord(rec)
                    Logger.warn(f"traverse dir: {path}{subdir.fileName}")
                    Logger.warn(
                        f"traverse dir: " + dumpBytes(subdir.filesystemIdentifier)
                    )
                    subrec = objTree.findObjectRecordByKey(subdir.filesystemIdentifier)
                    if not subrec:
                        return
                    subobj = ReFS_ObjectTree_DirRecord(subrec)
                    Logger.warn(
                        f"root ref: {subobj.metaDataBlockReference.blockNumber}"
                    )
                    submsbp = ReFS_MSBP_DirTreeNode(self)
                    submsbp.load(subobj.metaDataBlockReference)
                    self._traverseDir(submsbp, objTree, f"{path}{subdir.fileName}\\")
        # for submsbp in msbp.subMSBP:
        #     self._traverseDir(submsbp, objTree)

    def _dumpDirTree(self, msbp: ReFS_MSBP_DirTreeNode, path: str):
        rec: ReFS_NodeRecord = None
        for rec in msbp.nodeRecords:
            self._dumpObjectRecord(rec, path, msbp.ref)

    def _searchTestFiles(self):
        Logger.info(f"searching test files...")
        self.testFileDataSectors = {}
        self._walkThroughAllSectors(self.__searchTestFiles)

    def __searchTestFiles(self, secdata: bytes, sectorBegin) -> bool:
        j, k = len(secdata), 0
        while k < j:
            if secdata[k : k + 8] == b"TESTDATA":
                pos = k + 8
                end = [ord("\r"), ord("\n")]
                while pos < k + 64:
                    if secdata[pos] in end:
                        break
                    pos += 1
                if pos < k + 64:
                    fileName = secdata[k + 8 : pos].decode(errors="replace")
                    self.testFileDataSectors[fileName] = (
                        k // self.BPB.BytesPerSector + sectorBegin
                    )
                    if len(self.testFileDataSectors) >= 624:
                        return False
            k += self.BPB.BytesPerSector
        return True

    # 遍历所有扇区，传递给handler处理
    # def handler(buf: bytes, sectorBegin) -> bool
    def _walkThroughAllSectors(self, handlers: callable):
        self.testFileDataSectors = {}
        i, totalSector = 0, self.BPB.SectorsInVolume
        lastPercent = -1
        while i < totalSector:
            self.fp.seek(i * self.BPB.BytesPerSector, 0)
            secdata = self.fp.read(1 << 20)
            if not secdata:
                break
            if handlers and not handlers(secdata, i):
                break
            i += len(secdata) // self.BPB.BytesPerSector
            percent = int(i / totalSector * 50)
            if lastPercent != percent:
                prog = "=" * percent + " " * (50 - percent)
                print(f"[{prog}]", end="\n" if i >= totalSector else "\r")
                lastPercent = percent

    def testObjectTreeEntry(self):
        # self._searchTestFiles()
        chkp = self.getCHKP()
        ref: ReFS_BlockReference = chkp.msbTreeRef[REFS_OBJECTS_TREE]
        objTree = ReFS_ObjectTree(ref, self.BPB, self.fp)
        rec = objTree.findObjectRecordByKey(
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x30\x05\x00\x00\x00\x00\x00\x00"
        )
        obj = ReFS_ObjectTree_DirRecord(rec)
        Logger.warn(f"volume info ref: {obj.metaDataBlockReference.blockNumber}")

    def __searchMSBP(self, secdata: bytes, sectorBegin) -> bool:
        j = len(secdata)
        k = 0
        while k < j:
            if secdata[k : k + 8] == b"MSB+\x02\x00\x00\x00":
                msbpHeader = ReFS_MetadataBlockHeader(
                    secdata[k : k + ReFS_MetadataBlockHeader.size()]
                )
                self.MSBPSectors[msbpHeader.blockNumber] = (
                    k // self.BPB.BytesPerSector + sectorBegin
                )
            k += self.BPB.BytesPerSector
        return True

    def exportFiles(self, exportRoot: str):
        fileRec: ReFS_FileRecord = None
        for fileRec in self.fileList:
            exportPath = exportRoot + fileRec.path[3:]
            exportFile = os.path.join(exportPath, fileRec.fileName)
            if not os.path.exists(exportPath):
                os.makedirs(exportPath)
            filePath = os.path.join(fileRec.path, fileRec.fileName)
            Logger.info(f"export [{filePath}] -> [{exportFile}]")
            fp = open(exportFile, "wb")
            datarunItem: ReFS_FileRecord_DataRunItem = None
            szWritten = 0
            for datarunItem in fileRec.dataRunRec.dataRunList.datarun:
                sec = self.bpb.blockToSector(datarunItem.datarun)
                self.fp.seek(self.BPB.sectorToByte(sec), 0)
                buf = self.fp.read(self.BPB.clusterToByte(datarunItem.clusterCount))

                if szWritten + len(buf) < fileRec.dataRunRec.dataDesc.fileSize:
                    fp.write(buf)
                    szWritten += len(buf)
                else:
                    sz = fileRec.dataRunRec.dataDesc.fileSize - szWritten
                    fp.write(buf[:sz])
                    szWritten += sz
            fp.close()

            if os.path.exists(filePath):
                srcmd5, dstmd5 = "", ""
                with open(filePath, "rb") as fp:
                    srcmd5 = hashlib.md5(fp.read()).hexdigest()
                with open(exportFile, "rb") as fp:
                    dstmd5 = hashlib.md5(fp.read()).hexdigest()
                if srcmd5 != dstmd5:
                    Logger.err(f"error export md5 not match!")


if __name__ == "__main__":
    fs = ReFS()
    fs.open("i")
    fs.loadSUPB()
    fs.loadCHKP()
    fs.traverseRootDir()
    # fs.testObjectTreeEntry()
    # fs.findCHKPTreeEntrySectors()

    # export file
    # fs.exportFiles("g:\\temp\\refs\\")
