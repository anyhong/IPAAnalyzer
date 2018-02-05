#!/usr/bin/env python
#coding: utf-8
# -*- coding: utf-8 -*-
# @Date    : 2017/11/17 11:06
# @Author  : honghanjun
# @Project : IPAAnalyzer
# @File    : IPAAnalyzer.py
# @Software: PyCharm

from LinkMapAnalyzer import *
from IPABundleAnalyzer import *
import os
import xlsxwriter
import time

def entry():

    ########################## 0.配置分析工程参数 ##########################
    """
    版本文件目录 放在 工作根目录 中，
    版本文件目录中放 ipa包 和 linkmap文件
    :return:
    """
    workspace = "/Users/xxx/Desktop/历史版本分析/"        # 分析资源文件目录
    arm64LinkMapFileName = "LinkMap-normal-arm64.txt"
    armv7LinkMapFileName = "LinkMap-normal-armv7.txt"
    ipaName = "test.ipa"

    version = ["V6.0.0",
               "V6.1.0",
               "V6.2.0",
               "V6.3.0", "V6.3.1", "V6.3.2",
               "V6.4.0", "V6.4.1",
               "V6.5.0",
               "V6.6.0"] # 版本文件目录

    title = ["index", "name"]
    title.extend(version)

    ########################## 1.初始化excel相关参数  ##########################
    currentTime = time.localtime(time.time())
    strTime = time.strftime('%Y_%m_%d_%H_%M_%S', currentTime)
    workbook = xlsxwriter.Workbook("iOS包分析%s.xlsx" %(strTime))

    # 定义标题栏格式对象：边框加粗1像素，背景色为灰色，单元格内容居中、加粗
    title_formatter = workbook.add_format()
    title_formatter.set_border(1)
    title_formatter.set_border_color('#b7b7b7')
    title_formatter.set_bg_color('#cccccc')
    title_formatter.set_bold()
    title_formatter.set_font_size(15)
    title_formatter.set_align('center')
    title_formatter.set_valign('vcenter')

    # 数据栏格式
    formatter = workbook.add_format()
    formatter.set_border(1)
    formatter.set_font_size(13)
    formatter.set_border_color('#b7b7b7')
    formatter.set_valign('vcenter')

    # 数字格式
    size_formatter = workbook.add_format()
    size_formatter.set_border(1)
    size_formatter.set_align('right')
    size_formatter.set_font_size(13)
    size_formatter.set_border_color('#b7b7b7')
    size_formatter.set_valign('vcenter')

    ########################## 2.开始解析源文件  ##########################
    linkmapArm64List = {}
    linkmapArmv7List = {}
    ipabundleList = {}
    mainObjArm64 = {}
    mainObjArmv7 = {}
    sizeSource = {}
    for sub in version:
        fullName = os.path.join(workspace, sub)
        print '开始解析-%s' % (fullName)

        sizeTemp = {}
        binarySize = 0
        mainObjSize = 0
        ipaSize = 0
        ipaUnzipSize = 0

        arm64LinkMapPath = os.path.join(fullName, arm64LinkMapFileName)
        if os.path.isfile(arm64LinkMapPath):
            outputFile = os.path.join(fullName, "arm64_output.txt")
            analyzer = LinkMapAnalyzer(arm64LinkMapPath, outputFile)
            print '解析-%s' % (arm64LinkMapPath)
            analyzer.analyze()
            linkmapArm64List[sub] = analyzer
            binarySize += analyzer.totalSize
            if not analyzer.mainProject is None:
                mainObjArm64[sub] = analyzer.mainProject.objMap
                mainObjSize += analyzer.mainProject.totalSize
            print format(round(analyzer.totalSize / 1024.0, 2), ',')

        armv7LinkMapPath = os.path.join(fullName, armv7LinkMapFileName)
        if os.path.isfile(armv7LinkMapPath):
            outputFile = os.path.join(fullName, "armv7_output.txt")
            analyzer = LinkMapAnalyzer(armv7LinkMapPath, outputFile)
            print '解析-%s' % (armv7LinkMapPath)
            analyzer.analyze()
            binarySize += analyzer.totalSize
            linkmapArmv7List[sub] = analyzer
            if not analyzer.mainProject is None:
                mainObjArmv7[sub] = analyzer.mainProject.objMap
                mainObjSize += analyzer.mainProject.totalSize
            print format(round(analyzer.totalSize / 1024.0, 2), ',')

        ipaPath = os.path.join(fullName, ipaName)
        ipaSize = os.path.getsize(ipaPath)
        if os.path.exists(ipaPath):
            ipaAnalyzer = IPABundleAnalyzer(ipaPath)
            print '解析-%s' % (ipaPath)
            ipaAnalyzer.analyze()
            ipabundleList[sub] = ipaAnalyzer
            ipaUnzipSize = ipaAnalyzer.totalSize
            print format(round(ipaAnalyzer.totalSize, 1), ',')
        unit = 1024.0 * 1024.0 # 单位mb
        sizeTemp["ipaUnzip"] = round(ipaUnzipSize / unit, 1)
        sizeTemp["ipa"] = round(ipaSize / unit, 1)
        sizeTemp["binary"] = round(binarySize / unit, 1)
        sizeTemp["sourceSize"] = round((ipaUnzipSize - binarySize) / unit, 1)
        sizeTemp["mainObj"] = round(mainObjSize / unit, 1)
        sizeTemp["libSize"] = round((binarySize - mainObjSize) / unit, 1)
        sizeSource[sub] = sizeTemp

    ########################## 3.输出数据到excel  ##########################



    # 趋势分析
    chatTitle = list(version)
    chatTitle.insert(0, u"类型")
    chatTitle.append(u"说明")
    type = [u'IPA包大小', u'解压包大小', u'三方动态库及资源大小', u'二进制文件大小', u'工程二进制大小', u'三方静态库大小']
    desc = [u'打包成IPA包后的大小',
            u'解压安装后整个包大小（包含三方动态库、资源文件、二进制文件）',
            u'三方动态库、图片资源、car等等所有',
            u'二进制文件的大小（包含主工程二进制、三方静态库）',
            u'主工程的二进制文件',
            u'三方静态库二进制']

    worksheet3_name = u"增长趋势"
    worksheet3 = workbook.add_worksheet(worksheet3_name)
    worksheet3.set_column(0, 0, 20)
    worksheet3.set_column(1, len(version)+1, 15)
    worksheet3.set_column(len(version)+1, len(version) + 1, 75)
    worksheet3.set_default_row(20)

    chart = workbook.add_chart({'type': 'line'})
    chart.set_size({'width': 1000, 'height': 500})  # 设置图表大小
    chart.set_title({'name': u'增长趋势'})  # 设置图表（上方）大标题
    chart.set_y_axis({
        'name':  u'体积大小（单位：Mb）',
        'name_font': {'size': 14, 'bold': True},
        'num_font': {'size': 12, 'bold': True},
    })

    chart.set_x_axis({
        'name_font': {'size': 16, 'bold': True},
        'num_font': {'size': 12, 'bold': True},
    })

    resultTime = time.strftime('%Y-%m-%d %H:%M:%S', currentTime)
    resultDesc = u"结果生成时间：%s" % (resultTime)
    worksheet3.merge_range(10, 0, 11, len(chatTitle)-1, resultDesc, formatter)
    worksheet3.insert_chart('A13', chart)  # 在A8单元格插入图表


    data = []
    for sub in version:
        temp = []
        binarySize = 0
        mainObjSize = 0
        ipaSize = 0
        ipaUnzipSize = 0
        libSize = 0
        sourceSize = 0
        if sub in sizeSource:
            sizeTemp = sizeSource[sub]
            binarySize = sizeTemp["binary"]
            mainObjSize = sizeTemp["mainObj"]
            ipaSize = sizeTemp["ipa"]
            ipaUnzipSize = sizeTemp["ipaUnzip"]
            libSize = sizeTemp["libSize"]
            sourceSize = sizeTemp["sourceSize"]
        temp.append(ipaSize)
        temp.append(ipaUnzipSize)
        temp.append(sourceSize)
        temp.append(binarySize)
        temp.append(mainObjSize)
        temp.append(libSize)

        data.append(temp)


    worksheet3.write_row('A1', chatTitle, title_formatter)
    worksheet3.write_column('A2', type, formatter)
    worksheet3.write_column(1, len(version)+1, desc, size_formatter)
    for index, sub in enumerate(data):
        worksheet3.write_column(1, index+1, sub, size_formatter)

    def chart_series(row):
        chart.add_series({
            'name': [worksheet3_name, row+1, 0],
            'categories': [worksheet3_name, 0, 1, 0, len(version)],
            'values': [worksheet3_name, row+1, 1, row+1, len(version)],
        })

    for index, item in enumerate(type):
        chart_series(index)






    # ipa包解析
    worksheet = workbook.add_worksheet(u"ipa包分析")
    worksheet.set_column(0, 1, 40)
    worksheet.set_column(2, 11, 15)
    worksheet.set_default_row(20)
    worksheet.write_row('A1', title, title_formatter)

    unionMeta = {}
    for sub in version:
        if sub in ipabundleList:
            analyzer = ipabundleList[sub]
            unionMeta = dict(unionMeta, **analyzer.metaFileMap)
    unionMetaDesc = sorted(unionMeta.items(), key=lambda item:item[1].totalSize, reverse=True)

    unionMetaData = {}
    unionMetaIndex = [None] * len(unionMetaDesc)
    unionMetaName = [None] * len(unionMetaDesc)

    for index, item in enumerate(unionMetaDesc):
        unionMetaIndex[index] = item[1].nameMD5
        unionMetaName[index] = item[1].name
    unionMetaData["index"] = unionMetaIndex
    unionMetaData["name"] = unionMetaName

    for titleIndex, sub in enumerate(title):
        if sub in ipabundleList:
            metaFileMap = ipabundleList[sub].metaFileMap
            temp = [None] * len(unionMetaDesc)
            for index, item in enumerate(unionMetaIndex):
                if item in metaFileMap:
                    size = format(round(metaFileMap[item].totalSize / 1024.0, 2), ',')
                    temp[index] = "%skb" % (size)
            unionMetaData[sub] = temp
            worksheet.write_column(1, titleIndex, unionMetaData[sub], size_formatter)
        else:
            worksheet.write_column(1, titleIndex, unionMetaData[sub], formatter)







    # 二进制分析
    worksheet1 = workbook.add_worksheet(u"二级制分析")
    worksheet1.set_column(0, 1, 40)
    worksheet1.set_column(2, 11, 15)
    worksheet1.set_default_row(20)
    worksheet1.write_row('A1', title, title_formatter)

    unionLib = {}
    for sub in version:
        if sub in linkmapArm64List:
            analyzer = linkmapArm64List[sub]
            unionLib = dict(unionLib, **analyzer.libMap)
    unionLibDesc = sorted(unionLib.items(), key=lambda item:item[1].totalSize, reverse=True)

    unionLibData = {}
    unionLibIndex = [None] * len(unionLibDesc)
    unionLibName = [None] * len(unionLibDesc)

    for index, item in enumerate(unionLibDesc):
        unionLibIndex[index] = item[1].nameMD5
        unionLibName[index] = item[1].name
    unionLibData["index"] = unionLibIndex
    unionLibData["name"] = unionLibName

    for titleIndex, sub in enumerate(title):
        if sub in linkmapArm64List:
            libMap64 = linkmapArm64List[sub].libMap
            libMapv7 = linkmapArmv7List[sub].libMap
            temp = [None] * len(unionLibDesc)
            for index, item in enumerate(unionLibIndex):
                if item in libMap64:
                    totalSize = libMap64[item].totalSize
                    if item in libMapv7:
                        totalSize += libMapv7[item].totalSize
                    size = format(round(totalSize / 1024.0, 2), ',')
                    temp[index] = "%skb" % (size)
            unionLibData[sub] = temp
            worksheet1.write_column(1, titleIndex, unionLibData[sub], size_formatter)
        else:
            worksheet1.write_column(1, titleIndex, unionLibData[sub], formatter)






    # 主工程二进制分析
    worksheet2 = workbook.add_worksheet(u"主工程二进制分析")
    worksheet2.set_column(0, 1, 40)
    worksheet2.set_column(2, 11, 15)
    worksheet2.set_default_row(20)
    worksheet2.write_row('A1', title, title_formatter)

    unionObj = {}
    for sub in version:
        if sub in mainObjArm64:
            objMap = mainObjArm64[sub]
            unionObj = dict(unionObj, **objMap)
    unionObjDesc = sorted(unionObj.items(), key=lambda item:item[1].fileSize, reverse=True)

    unionObjData = {}
    unionObjIndex = [None] * len(unionObjDesc)
    unionObjName = [None] * len(unionObjDesc)

    for index, item in enumerate(unionObjDesc):
        unionObjIndex[index] = item[1].nameMD5
        unionObjName[index] = item[1].fileName
    unionObjData["index"] = unionObjIndex
    unionObjData["name"] = unionObjName

    for titleIndex, sub in enumerate(title):
        if sub in mainObjArm64:
            objMap64 = mainObjArm64[sub]
            objMapv7 = mainObjArmv7[sub]
            temp = [None] * len(unionObjDesc)
            for index, item in enumerate(unionObjIndex):
                if item in objMap64:
                    totalSize = objMap64[item].fileSize
                    if item in objMapv7:
                        totalSize += objMapv7[item].fileSize
                    size = format(round(totalSize / 1024.0, 2), ',')
                    temp[index] = "%skb" % (size)
            unionObjData[sub] = temp
            worksheet2.write_column(1, titleIndex, unionObjData[sub], size_formatter)
        else:
            worksheet2.write_column(1, titleIndex, unionObjData[sub], formatter)

    workbook.close()



entry()