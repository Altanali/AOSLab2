import os
import sys
import time
from pathlib import Path
import time
import random
import string

def read_and_write_through_file(fd, fd2, block_size, read_indices, write_indices):
	ofs = 0
	for i in range(len(read_indices)):
		read_index = read_indices[i]
		write_index = write_indices[i]
		# print("Reading to index ", read_index)
		# print("Writing to index ", write_index)
		ofs = write_index*block_size
		#random write
		# letter = ("".join(random.choice(string.ascii_letters) for i in range(block_size))).encode('utf-8')
		letter = random.choice(string.ascii_letters).encode('utf-8')
		
		# if(os.pwrite(fd, letter, ofs) == -1):
		# 	raise Exception("Failed pwrite")
		
		# if(os.pwrite(fd2, letter, ofs) == -1):
		# 	raise Exception("Failed pwrite")
		
		read_index = read_index*block_size
		if(os.pread(fd, block_size, ofs) == -1):
			raise Exception("Failed pread")
		
		read_index = read_index*block_size
		if(os.pread(fd2, block_size, ofs) == -1):
			raise Exception("Failed pread")




if __name__ == "__main__":
	print(sys.argv)
	path = sys.argv[1]
	path2 = sys.argv[2]
	start_time: float
	end_time: float
	# output_path = os.path.join("benchmarks/read/", path if path[0] != "/" else path[1:])
	# output_path += ".out"
	# Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
	# output_file = open(output_path, "w+")

	block_size = 1024

	fd = os.open(path, os.O_RDWR)
	fdw = os.open(path, os.O_WRONLY)
	fd2 = os.open(path2, os.O_RDWR)
	file_size = os.stat(path).st_size
	num_blocks = max(file_size // block_size - 1, 1)

	print("starting")
	for i in range(10):
		read_indices = list(range(num_blocks - 2))
		write_indices = list(range(num_blocks - 2))
		# random.shuffle(read_indices) #uncommount for random writes
		# random.shuffle(write_indices)
		write_indices = list(reversed(read_indices))
		start = time.perf_counter()
		read_and_write_through_file(fd, fd2, block_size, read_indices, write_indices)
		end = time.perf_counter()
		print(f"{end - start:.2f}")
