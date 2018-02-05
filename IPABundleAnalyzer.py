#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017/11/22 12:24
# @Author  : honghanjun
# @Project : IPAAnalyzer
# @File    : IPABundleAnalyzer.py
# @Software: PyCharm

from ObjFiles import *
import shutil
import zipfile


class IPABundleAnalyzer:

    def __init__(self, ipaPath):
        self.ipaPath = ipaPath
        self.__metaFileList = []
        self.metaFileMap = {}
        self.totalSize = 0

    # 开始解析
    def analyze(self):
        if os.path.isfile(self.ipaPath):
            self.readIPA(self.ipaPath)
        else:
            print "path None"
        return self.__metaFileList

    # 解析ipa文件
    def readIPA(self, ipaPath):
        basePath, ipaName = os.path.split(ipaPath)
        filename, extension = os.path.splitext(ipaName)
        newFile = '%s/%s.zip' % (basePath, filename)
        shutil.copy(ipaPath, newFile)

        filedir = '%s/%s' % (basePath, filename)
        r = zipfile.is_zipfile(newFile)
        if r:
            fz = zipfile.ZipFile(newFile, 'r')
            for file in fz.namelist():
                # print(file)  # 打印zip归档中目录
                fz.extract(file, filedir)
        else:
            print('This file is not zip file')

        ipaMetafile = MetaFile(filedir, basePath)
        self.traverseFile(ipaMetafile)

        self.listFile(ipaMetafile, self.__metaFileList)
        # cmpfun = operator.attrgetter("totalSize")
        # self.metaFileList.sort(key=cmpfun, reverse=True)

        for meta in self.__metaFileList:
            self.totalSize += meta.totalSize
            self.metaFileMap[meta.nameMD5] = meta


    # 列出文件
    def listFile(self, metafile, allMetaFiles):
        # bundle和framework就不再细分
        if not metafile.isDirectory or metafile.name.endswith(".bundle") or metafile.name.endswith(".framework"):
            allMetaFiles.append(metafile)
        else:
            for file in metafile.subFiles:
                self.listFile(file, allMetaFiles)

    # 遍历文件
    def traverseFile(self, metafile):
        basePath = metafile.fullPath
        filelist = os.listdir(basePath)

        for filename in filelist:
            if not filename.startswith("."):
                fullName = os.path.join(basePath, filename)
                ipaMetafile = MetaFile(fullName, metafile.rootPath)
                fullName = os.path.join(basePath, filename)
                if ipaMetafile.isDirectory:
                    self.traverseFile(ipaMetafile)
                else:
                    ipaMetafile.totalSize = os.path.getsize(fullName)

                metafile.addSubFile(ipaMetafile)