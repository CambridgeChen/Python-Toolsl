import os
import re
import time
import datetime
import zipfile
import getopt
import sys
import shutil
import math
import json

REG_EXP = r'(\S+)(\s+)(.+)'

class DiffFileCopyer:
	fileList = []
	fileCount = 0
	beginTime = 0
	serverPath = "D:\\MoneyServer"
	gameSvnPath = serverPath + "\\gameres_svn"
	targetPath = ''
	ignorePathList = [
		gameSvnPath + "\\script",	
		gameSvnPath + "\\.svn",	
		gameSvnPath + "\\gw\\rolevalue_setting\\rolevalue_log",
		gameSvnPath + "\\itemexchange_setting\\rolevalue_log",
		gameSvnPath + "\\rolevalueladder_setting\\rolevalue_log"
	]
	# generate by 'ignorePathList'
	ignorePathTree = {}
	ignoreFileType = set()
	isPack = True


	def pack(self, packDirectory, zipFilePath, zipFileName):
		zipFileName = zipFileName + ".zip"
		zipFileName = os.path.join(zipFilePath, zipFileName)

		if not os.path.exists(zipFilePath):
			os.mkdir(os.path.join('.', zipFilePath))

		if os.path.exists(zipFileName):
			print("file: " + zipFileName + " is already exists!Please check again!")
			return

		myZipFile = zipfile.ZipFile(zipFileName, "w", zipfile.ZIP_DEFLATED)
		os.chdir(zipFilePath)
        
		for dirpath, dirnames, files in os.walk(packDirectory):
			for file in files:
				relpath = os.path.relpath(os.path.join(dirpath, file), start = zipFilePath)
				print("pack", relpath)
				myZipFile.write(relpath)

		myZipFile.close()
	

	def __isIgnoreType(self, fileName):
		fileType = os.path.splitext(fileName)
		return fileType[1] in self.ignoreFileType
	

	def __copyFunction(self, src, dst, *, follow_symlinks=True):
		if os.path.isdir(dst):
			dst = os.path.join(dst, os.path.basename(src))
		if not self.__isIgnoreType(src):
			shutil.copy2(src, dst)
		return dst


	def writeResult(self):
		if not os.path.exists(self.targetPath):
			os.makedirs(self.targetPath)
		for file in self.fileList:
			targetFile = file
			targetFile = file.replace(self.gameSvnPath, self.targetPath)
			if os.path.isfile(file):	
				targetFilePath = os.path.dirname(targetFile)
				if not os.path.exists(targetFilePath):
					os.makedirs(targetFilePath)
				shutil.copyfile(file, targetFile)
			elif os.path.isdir(file):
				shutil.copytree(file, targetFile, False, None, self.__copyFunction)


	def prosessFile(self, path):
		szRtn = os.popen("svn status " + path + "").read()
		infoList = szRtn.split("\n")
		parseRegExp = re.compile(REG_EXP)
		for line in infoList:
			if line == '':
				continue
			match = parseRegExp.findall(line)
			if match:
				status = match[0][0]
				fileName = match[0][2]
				if status == 'M' or status == '?':
					# if match[0][2] in self.ignorePathList:
					if self.__isInIgnorePath(fileName) == True or self.__isIgnoreType(fileName):
						continue
					print("add", fileName)
					self.fileList.append(fileName)
				else:
					if 'ignore-on-commit' in fileName:
						return


	def go(self):
		todayStr = "gameres_svn_" + time.strftime('%Y_%m_%d_%H_%M_%S')
		self.targetPath = self.serverPath + "\\patch\\" + todayStr
		self.prosessFile(self.gameSvnPath)
		self.writeResult()
		if self.isPack:
			self.pack(self.targetPath, self.serverPath + "\\patch\\", todayStr)
	

	def __isInIgnorePath(self, path):
		if path == None:
			return False

		segmentList = path.split(os.path.sep)
		segmentTree = self.ignorePathTree
		for segment in segmentList:
			if segmentTree.get(segment) == None:
				break
			segmentTree = segmentTree.get(segment)
		
		if len(segmentTree) == 0:
			return True
		else:
			return False


	def initFromConfig(self, jsonConfig):
		if jsonConfig == None:
			return

		serverPath = jsonConfig.get('serverPath')
		gameSvnPath = jsonConfig.get('gameSvnPath')
		ignorePathList = jsonConfig.get('ignorePathList')
		ignoreFileType = jsonConfig.get('ignoreFileType')
		isPack = jsonConfig.get('isPack')

		if serverPath != None:
			self.serverPath = serverPath
		if gameSvnPath != None:
			self.gameSvnPath = os.path.join(self.serverPath, gameSvnPath)
		if ignorePathList != None:
			self.ignorePathList = [os.path.join(self.gameSvnPath, relPath) for relPath in ignorePathList]
			for ignorePath in self.ignorePathList:
				segmentList = ignorePath.split(os.path.sep)
				segmentTree = self.ignorePathTree
				for segment in segmentList:
					if segmentTree.get(segment) == None:
						segmentTree[segment] = {}
					segmentTree = segmentTree[segment]
		if ignoreFileType != None:
			for fileType in ignoreFileType:
				self.ignoreFileType.add(fileType)
		if isPack != None:
			self.isPack = isPack


if __name__ == '__main__':
	argv = sys.argv
	argCount = len(argv)
	if argCount < 2:
		print("Please select a json config!")
		sys.exit("Please select a json config!")

	if not os.path.exists(argv[1]):
		print("File not found!")
		sys.exit("File not found!")

	with open(argv[1], 'r') as jsonConfigFile:
		jsonConfig = json.load(jsonConfigFile)

	diffFileCopyer = DiffFileCopyer()
	diffFileCopyer.initFromConfig(jsonConfig)
	diffFileCopyer.go()
