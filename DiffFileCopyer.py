import os
import re
import time
import datetime
import zipfile
import getopt
import sys
import shutil
import math

REG_EXP = r'(\S+)(\s+)(.+)'

class DiffFileCopyer:
	fileList = []
	fileCount = 0
	beginTime = 0
	serverPath = "D:\\MoneyServer"
	gameSvnPath = serverPath + "\\gameres_svn"
	targetPath = ''
	ignorePathList =[
		gameSvnPath + "\\script",	
		gameSvnPath + "\\.svn",	
		gameSvnPath + "\\gw\\rolevalue_setting\\rolevalue_log",
		gameSvnPath + "\\itemexchange_setting\\rolevalue_log",
		gameSvnPath + "\\rolevalueladder_setting\\rolevalue_log"
	]

	def traverse(self, path):
		if not path:
			return False
		if not os.path.exists(path):
			print("error path " + path)
			return False
		if os.path.isfile(path):
			# currentTime = time.time() + 0.01
			# speed = math.floor(self.fileCount / (currentTime - self.beginTime) * 100) / 100
			# print("parse file " + str(self.fileCount) + " " + path + " with speed " + str(speed) + "/s.")
			self.prosessFile(path)
		if os.path.isdir(path) and not (path in self.ignorePathList):
			# print("walk path " + path)
			if not self.prosessFile(path):
				fileNameList = os.listdir(path)
				for fileName in fileNameList:
					fileName = path + '/' + fileName
					self.traverse(fileName)
			return True

	def pack(self, packDirectory, zipFilePath, zipFileName):
		zipFileName = zipFileName + ".zip"
		zipFileName = os.path.join(zipFilePath, zipFileName)

		if not os.path.exists(zipFilePath):
			os.mkdir(os.path.join('.', zipFilePath))

		if os.path.exists(zipFileName):
			print("file: " + zipFileName + " is already exists!Please check again!")
			return

		myZipFile = zipfile.ZipFile(zipFileName, "w", zipfile.ZIP_DEFLATED)
        
		for dirpath, dirnames, files in os.walk(packDirectory):
			for file in files:
				relpath = os.path.relpath(os.path.join(dirpath, file), start = zipFilePath)
				print(relpath)
				myZipFile.write(relpath)

		# logFileNameList = os.listdir(packDirectory)

		# try:
		# 	for logFileName in logFileNameList:
		# 		print("logFileName", logFileName)
		# 		info = os.path.join(packDirectory, logFileName)
		# 		if os.path.isfile(info):
		# 			myZipFile.write(info, logFileName)
		# finally:
		# 	myZipFile.close()
        
		# try:
		# 	myZipFile = zipfile.ZipFile(zipFileName, "r", zipfile.ZIP_DEFLATED)

		# 	errorFileName =  myZipFile.testzip()
		# finally:
		myZipFile.close()

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
				shutil.copytree(file, targetFile)

	def prosessFile(self, fileName):
		szRtn = os.popen("svn status " + fileName + "").read()
		infoList = szRtn.split("\n")
		parseRegExp = re.compile(REG_EXP)
		for line in infoList:
			if line == '':
				continue
			match = parseRegExp.findall(line)
			if match:
				if match[0][0] == 'M' or match[0][0] == '?':
					if match[0][2] in self.ignorePathList:
						continue
					print(match[0][2])
					self.fileList.append(match[0][2])
				else:
					if 'ignore-on-commit' in match[0][2]:
						return
	def go(self):
		todayStr = "gameres_svn_" + time.strftime('%Y_%m_%d_%H_%M_%S')
		self.targetPath = self.serverPath + "\\patch\\" + todayStr
		self.prosessFile(self.gameSvnPath)
		self.writeResult()
		self.pack(self.targetPath, self.serverPath + "\\patch\\", todayStr)


if __name__ == '__main__':
	diffFileCopyer = DiffFileCopyer()
	diffFileCopyer.go()
