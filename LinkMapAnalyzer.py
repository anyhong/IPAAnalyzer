#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017/11/22 12:23
# @Author  : honghanjun
# @Project : IPAAnalyzer
# @File    : LinkMapAnalyzer.py
# @Software: PyCharm


from ObjFiles import *
import re
import string
import operator

class LinkMapAnalyzer:

    def __init__(self, linkMapPath, outputPath = None):
        self.linkMapPath = linkMapPath
        self.outputPath = outputPath
        self.projectName = ""
        self.mainProject = None
        self.symbolMap = {}
        self.objMap = {}
        self.libMap = {}
        self.totalSize = 0
        self.__objFileList = []
        self.__symbolsList = []

    # 开始解析
    def analyze(self):
        self.analyzeLinkmap()
        self.dispatchFiles()

        if not self.outputPath is None:
            self.formatOutput()


    # 逐行解析文件
    def analyzeLinkmap(self):

        f_read = open(self.linkMapPath, "r")
        type = LinkMapLineType.LinkMapUnKnown
        line = f_read.readline()

        while (line):
            currentType = self.analyzeLineType(line)

            if currentType == LinkMapLineType.LinkMapBlank:
                type = LinkMapLineType.LinkMapBlank
            elif currentType != LinkMapLineType.LinkMapUnKnown:
                type = currentType

            if type == LinkMapLineType.LinkMapPath:
                self.projectName = self.analyzeProjectName(line)
            elif type == LinkMapLineType.LinkMapObjFiles:
                obj = self.analyzeObjFiles(line)
                if not obj is None:
                    self.__objFileList.append(obj)
            elif type == LinkMapLineType.LinkMapSymbols:
                symbol = self.analyzeSymbol(line)
                if not symbol is None:
                    self.__symbolsList.append(symbol)

            line = f_read.readline()

        f_read.close()



    # 文件分发
    def dispatchFiles(self):
        objList = [None] * (len(self.__objFileList) + 1)
        for obj in self.__objFileList:
            objList[obj.fileNum] = obj

        for symbol in self.__symbolsList:
            obj = objList[symbol.fileNum]
            if not obj is None:
                obj.appendSymbolFile(symbol)

        for obj in objList:
            if not obj is None:
                if obj.fatherProjMD5 in self.libMap:
                    lib = self.libMap[obj.fatherProjMD5]
                    lib.addObj(obj)
                else:
                    lib = LibFile(obj.fatherProj)
                    lib.addObj(obj)
                    self.libMap[obj.fatherProjMD5] = lib

        for key, value in self.libMap.items():
            self.totalSize += value.totalSize
            if value.name == self.projectName:
                self.mainProject = value


    # 解析工程名
    def analyzeProjectName(self, line):
        if line == None:
            return ""
        else:
            return line.split("/")[-1].strip()



    # 解析Symbol符号
    def analyzeSymbol(self, line):
        fileNum = 0
        fileSize = 0

        if len(line.strip()) == 0:
            return fileNum, fileSize

        # 解析文件大小
        fileSizeResult = re.findall(r"\b0x[0-9a-fA-F]+\b", line, re.M)
        if len(fileSizeResult) > 1:
            fileSize = int(fileSizeResult[1], 16)

        # 解析文件编号
        result = re.findall(r"(\[.*?\])", line, re.M)
        if len(result) > 0:
            result = result[0].replace('[', '').replace(']', '')
            fileNum = string.atoi(result)

        symbolFile = SymbolFile(fileNum, fileSize)
        return symbolFile



    # 解析obj文件
    def analyzeObjFiles(self, line):
        if len(line.strip()) == 0:
            return None

        projectName = self.projectName

        # 解析文件编号
        fileNum = 0
        result = re.findall(r"(\[.*?\])", line, re.M)
        if len(result) > 0:
            result = result[0].replace('[', '').replace(']', '')
            fileNum = string.atoi(result)

        # 解析文件名称 和 所属的文件类
        fileName = line.split("/")[-1].strip()
        if "(" in fileName:
            nameList = fileName.split("(")
            projectName = nameList[0]
            fileName = nameList[-1].replace(')', '')

        # 判断是否合法属性
        if fileName.strip() == '' or projectName.strip() == '' or fileNum == 0:
            return None

        return ObjFile(fileNum, fileName, projectName)


    # 解析LinkMap中行类型
    def analyzeLineType(self, line):

        if line.strip() == '':
            return LinkMapLineType.LinkMapBlank
        elif line.startswith("# Path"):
            return LinkMapLineType.LinkMapPath
        elif line.startswith("# Arch"):
            return LinkMapLineType.LinkMapArch
        elif line.startswith("# Object"):
            return LinkMapLineType.LinkMapObjFiles
        elif line.startswith("# Address") and "Section" in line:
            return LinkMapLineType.LinkMapSections
        elif line.startswith("# Address") and "Name" in line:
            return LinkMapLineType.LinkMapSymbols
        else:
            return LinkMapLineType.LinkMapUnKnown


    # 格式化输出
    def formatOutput(self):
        f_output = open(self.outputPath, "w+")
        for key, lib in self.libMap.items():
            totalSize = '%.3fkb' % (lib.totalSize / 1024.0)
            f_output.write("%-50s %-30s\n" % (lib.name, totalSize))
            if lib.name == self.projectName:
                f_output.write("======================\n")
                for key, obj in lib.objMap.items():
                    fileSize = '%.3fkb' % (obj.fileSize / 1024.0)
                    f_output.write("%-50s %-20d %-10s\n" % (obj.fileName, obj.fileNum, fileSize))
            f_output.write("======================\n")

        f_output.close()