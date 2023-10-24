import os
import sys
import time
from pathlib import Path
import time
import random
import string

def write_through_file(fd, block_size, indices):
	ofs = 0
	for i in indices:
		ofs = i*block_size
		letter = random.choice(string.ascii_letters).encode("utf-8")
		chunk = ("".join(random.choice(string.ascii_letters) for i in range(block_size))).encode("utf-8")
		os.pwrite(fd, chunk, i*block_size)
		os.lseek(fd, block_size, os.SEEK_CUR)

if __name__ == "__main__":
	print(sys.argv)
	path = sys.argv[1]

	start_time: float
	end_time: float
	block_size = 8192

	fd = os.open(path, os.O_RDWR)
	num_blocks = 1000

	for i in range(10):
		indices = list(range(num_blocks))
		random.shuffle(indices) #uncommount for random writes
		start = time.perf_counter()
		write_through_file(fd, block_size, indices)
		end = time.perf_counter()
		print(f"{end - start:.2f}")
		os.lseek(fd, 0, os.SEEK_SET)
		os.truncate(fd, 0)