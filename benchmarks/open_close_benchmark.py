import time
import os
import random

for i in range(10):
	files = [
		"file-256b", "file-1MB", "file-256MB", "file-512MB", "file-1g"
	]

	dirname = "nfs_mountpoint/"
	fds = []

	start = time.perf_counter()
	for file in files:
		path = os.path.join(dirname, file)
		fds.append(os.open(path, os.O_RDWR))


	read_size=1024
	random.shuffle(fds)
	for fd in fds:
		ofs = 0
		while True:
			content = os.pread(fd, read_size, ofs)
			if len(content) == 0:
				break
			ofs += len(content)

	end = time.perf_counter()

	print(end - start)