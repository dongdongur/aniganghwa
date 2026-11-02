import ctypes,sys,shutil
L=ctypes.CDLL('/home/claude/StormLib/build/libstorm.so')
src,chk,dst=sys.argv[1:4]
shutil.copy(src,dst)
h=ctypes.c_void_p()
assert L.SFileOpenArchive(dst.encode(),0,0,ctypes.byref(h))
L.SFileRemoveFile(h,b'staredit\\scenario.chk',0)
ok=L.SFileAddFileEx(h,chk.encode(),b'staredit\\scenario.chk',0x200|0x80000000,2,2)  # COMPRESS|REPLACE, zlib
print('add',ok)
L.SFileCompactArchive(h,None,0)
L.SFileCloseArchive(h)
