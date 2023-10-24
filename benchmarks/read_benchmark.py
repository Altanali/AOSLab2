import os
import sys
import time
from pathlib import Path
import time

def read_through_file(fd, read_size, indices):
	ofs = 0
	for i in indices:
		ofs = read_size*i
		os.pread(fd, read_size, ofs)


if __name__ == "__main__":
	print(sys.argv)
	path = sys.argv[1]

	start_time: float
	end_time: float

	read_size = 2048


	fd = os.open(path, os.O_RDONLY)
	file_size = os.stat(path).st_size
	num_blocks = file_size // read_size

	for i in range(10):
		indices = list(range(num_blocks))
		start = time.perf_counter()
		read_through_file(fd, read_size, indices)
		end = time.perf_counter()
		print(f"{end - start}")
		os.lseek(fd, 0, os.SEEK_SET)
	os.close(fd)