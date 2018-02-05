#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017/11/17 13:06
# @Author  : honghanjun
# @Project : IPAAnalyzer
# @File    : ObjFiles.py
# @Software: PyCharm

import operator
import os
import hashlib


class LibFile:
    """
    这个文件是解析二进制文件的数据
    """
    def __init__(self, name):
        self.name = name
        self.objFileList = []
        self.totalSize = 0
        self.nameMD5 = hashlib.md5(name).hexdigest()
        self.objMap = {}

    def addObj(self, obj):
        if obj.fatherProj == self.name:
            self.objMap[obj.nameMD5] = obj
            self.totalSize += obj.fileSize

    def sortBySize(self):
        cmpfun = operator.attrgetter("fileSize")
        self.objFileList.sort(key=cmpfun, reverse=True)



class ObjFile:
    """
    单个文件
    """
    def __init__(self, fileNum, fileName, fatherProj):
        self.fileNum = fileNum
        self.fileName = fileName
        self.nameMD5 = hashlib.md5(fileName).hexdigest()
        self.fatherProj = fatherProj
        self.fatherProjMD5 = hashlib.md5(fatherProj).hexdigest()
        self.fileSize = 0
        self.symbolFileList = []

    def appendSymbolFile(self, symbolFile):
        if symbolFile.fileNum == self.fileNum:
            self.symbolFileList.append(symbolFile)
            self.fileSize += symbolFile.fileSize



class SymbolFile:
    """
    文件内部字符
    """
    def __init__(self, fileNum, fileSize):
        self.fileNum = fileNum      # 所属的obj文件编号
        self.fileSize = fileSize    # 大小
        self.fileLine = ""          # 解析的内容
        self.objName = ""           # 所属的obj





class MetaFile:
    def __init__(self, fullPath, rootPath):
        basePath, fileName = os.path.split(fullPath)
        self.isDirectory = True if os.path.isdir(fullPath) else False
        self.totalSize = 0
        self.name = fileName
        self.nameMD5 = hashlib.md5(fileName).hexdigest()
        self.relpath = fullPath.replace(rootPath, "")
        self.fullPath = fullPath
        self.rootPath = rootPath
        self.subFiles = []


    def addSubFile(self, metaFile):
        self.subFiles.append(metaFile)
        self.totalSize += metaFile.totalSize




class LinkMapLineType:
    LinkMapBlank = 0
    LinkMapPath = 1
    LinkMapArch = 2
    LinkMapObjFiles = 3
    LinkMapSections = 4
    LinkMapSymbols = 5
    LinkMapUnKnown = 6

