import os
import sys

_EOF = b''
_USAGE_ERR = 1
_OPEN_ERR = 2
_SIZE_ERR = 3
_CHUNK_SIZE = 16
_FIRST_ONLY = False # or True

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

def diffStart(old, new):
	while True:
		oldChunk = old.getChunk()
		newChunk = new.getChunk()
		if (not oldChunk or
		       not newChunk):
			break
		if oldChunk != newChunk:
			print(" "*30 + "ADDRESS: %08X"%(old.getAddress() or
			                                new.getAddress() ) )
			print("OLD <<<" + "="*40)
			print(chunkToHexStr(oldChunk))
			print("="*47)
			print(chunkToHexStr(newChunk))
			print("="*40 + ">>> NEW\n")
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
