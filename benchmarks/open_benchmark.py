import os
import sys
import time
from pathlib import Path
import time

if __name__ == "__main__":
	print(sys.argv)
	path = sys.argv[1]

	start_time: float
	end_time: float
	output_path = os.path.join("benchmarks/open/", path if path[0] != "/" else path[1:])
	output_path += ".out"
	Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
	output_file = open(output_path, "w+")

	for i in range(10):
		start = time.perf_counter_ns()
		fd = os.open(path, os.O_RDWR)
		end = time.perf_counter_ns()
		print(f"{end - start}")
		os.close(fd)


