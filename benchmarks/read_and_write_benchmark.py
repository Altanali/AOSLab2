import time
import os
import sys
import string
import random 
def read_and_write(path):
	write_size = 1024*128
	buffer = "".join(random.choice(string.ascii_letters) for i in range(write_size))

	reader = os.open(path, os.O_RDONLY)
	writer = os.open(path, os.O_WRONLY | os.O_APPEND)

	start = time.perf_counter()
	read_size = 1024
	file_size = os.stat(path).st_size
	num_blocks = file_size // read_size
	indices = range(1000)
	for i in indices:
		#1024 random chars

		os.write(writer, buffer.encode())
		os.lseek(reader, i * (write_size + 1), os.SEEK_SET)
		content = os.read(reader, write_size + 1)	
		if(len(content) == 0):
			print("Bad read")
			break
	end = time.perf_counter()
	print(end - start)
	os.close(reader)
	os.close(writer)



if __name__ == "__main__":
	read_and_write(sys.argv[1])