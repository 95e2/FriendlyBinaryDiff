import os
import sys

_EOF = b''
_USAGE_ERR = 1
_OPEN_ERR = 2
_SIZE_ERR = 3
_CHUNK_SIZE = 16
_FIRST_ONLY = False # or True

NONE = '\033[0m'
LIGHT_RED = '\033[31m'
LIGHT_GREEN = '\033[32;1m'
LIGHT_YELLOW = '\033[33;1m'

class DiffFile:
	def __init__(self, fp):
		self.__seek = 0
		self.__fp = fp
		self.__chunk = None

	def __nextChunk__(self, chunkSize):
		self.__seek += chunkSize
		self.__fp.seek(self.__seek)
		self.__chunk = self.__fp.read(chunkSize)

	def getChunk(self):
		self.__nextChunk__(_CHUNK_SIZE)
		if self.__chunk != _EOF:
			return self.__chunk

	def getAddress(self):
		return self.__seek

def checkSize(oldSize, newSize):
	if oldSize < newSize:
		sys.stderr.write("Error: the old file size less than the new file!\n")
		sys.exit(_SIZE_ERR)
	elif oldSize > newSize:
		sys.stderr.write("Error: the old file size more than the new file!\n")
		sys.exit(_SIZE_ERR)

def chunkToHexStr(chunk):
	if isinstance(chunk, str):
		# Python 2.x
		return ''.join(['%02X '%(ord(x)) for x in chunk])
	else:
		# Python 3.x
		return ''.join(['%02X '%(x) for x in chunk])

"""
                              ADDRESS: 016D8590
OLD <<<========================================
7F 25 92 BB 0D 42 20 C2 16 6D A4 AC CF 89 61 37 
===============^v=============^v===============
4F 25 92 BB 0D 82 20 C2 16 6D B9 AC CF 89 61 37 
========================================>>> NEW
"""

def getDiffStr(diffOffsets):
	seek = 0
	diffStr = ""
	for offset in diffOffsets:
		diffStr += (offset - seek) * "==="
		diffStr += LIGHT_GREEN + "^" + \
		    LIGHT_RED + "V" + NONE + "="
		seek = offset + 1
	diffStr += (_CHUNK_SIZE - diffOffsets[-1] - 1) * "==="
	return diffStr

def diffStart(old, new):
	while True:
		oldChunk = old.getChunk()
		newChunk = new.getChunk()
		if (not oldChunk or
		       not newChunk):
			break
		
		diffOffsets = []
		for i in range(len(zip(oldChunk, newChunk))):
			if oldChunk[i] != newChunk[i]:
				diffOffsets.append(i) # record offset.

		# FIXME: The result is not accurate.
		DISPLAY_LEN = (_CHUNK_SIZE * 2 + _CHUNK_SIZE / 2 + 1)
		if len(diffOffsets) > 0:
			print("ADDRESS: %08X, COUNT(%d)"%(old.getAddress() or
			                                new.getAddress(), len(diffOffsets) ) )
			print(LIGHT_GREEN + "OLD <<<" + "="*DISPLAY_LEN + NONE)
			print(chunkToHexStr(oldChunk))
			print(getDiffStr(diffOffsets))
			print(chunkToHexStr(newChunk))
			print(LIGHT_YELLOW + "="*DISPLAY_LEN + ">>> NEW\n" + NONE)
			if _FIRST_ONLY: break

def main(argv):
	if len(argv) < 3:
		sys.exit(_USAGE_ERR)

	oldFile = argv[1]
	newFile = argv[2]
	if not os.path.exists(oldFile) or not os.path.exists(newFile):
		sys.stderr.write("Error: can not found the old or the new file!\n")
		sys.exit(_OPEN_ERR)

	oldSzie = os.path.getsize(oldFile)	
	newSzie = os.path.getsize(newFile)
	checkSize(oldSzie, newSzie)

	with open(oldFile, "rb") as oldFp, open(newFile, "rb") as newFp:
		old = DiffFile(oldFp)
		new = DiffFile(newFp)

		diffStart(old, new)

if __name__ == "__main__":
	main(sys.argv)
