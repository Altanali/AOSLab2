import sys
import os
import shutil
from fuse import FUSE, Operations
from paramiko import (SSHClient, AutoAddPolicy)
from scp import SCPClient
from pathlib import Path


username = "altannag"
host = "c220g5-111024.wisc.cloudlab.us"

class PyFuse(Operations):
	def __init__(self, rootdir, mountpoint):
		self.ssh_client = SSHClient()
		self.rootdir = rootdir
		self.mountpoint = mountpoint
		self.tempdir = os.path.join("/tmp/", self.mountpoint)
		'''
			maps remote file path -> {
				local_tmp_path, 
				open_pointers, 
				is_dirty (not race condition friendly)
			}
		'''
		self.openfiles = {}
		if not os.path.isdir(self.tempdir):
			os.mkdir(self.tempdir)
		try: 
			self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
			self.ssh_client.connect(host, username=username)
			self.scp_client = SCPClient(self.ssh_client.get_transport())
			self.sftp_client = self.ssh_client.open_sftp()
		except Exception as e :
			print("Failed to establish connection: ", str(e))
			sys.exit(0)
	
	def path_from_root(self, path: str):
		return os.path.join(self.rootdir, 
					  path if not path.startswith("/") else path[1:])
	

	def path_from_temp(self, path: str):
		return os.path.join(self.tempdir, 
					   path if not path.startswith("/") else path[1:])

	def getattr(self, path, fh=None):
		#execute lstat on remote
		# print("getattr")
		stat_args_to_bases = {
			"st_dev": 10, 
			"st_mode": 16, 
			"st_size": 10, 
			"st_atime": 10,
			"st_mtime": 10, 
			"st_ctime": 10
		}
		remote_path = self.path_from_root(path)
		if remote_path in self.openfiles:
			temp_path = self.path_from_temp(path)
			stat_obj = os.lstat(temp_path)
			return dict((key, getattr(stat_obj, key)) for key in stat_args_to_bases.keys())
		
		(stdin, stdout, stderr) = self.ssh_client.exec_command(
			"stat --printf='%D %f %s %X %Y %Z' " + remote_path
		)
		stat_vals  = stdout.read().decode('utf-8')
		# print(f"stats for {remote_path}: {stat_vals}")
		if len(stat_vals) == 0:
			return None
		stat_vals = stat_vals.split(" ")

		return dict((key, int(stat_vals[i], base=stat_args_to_bases[key])) for i, key in enumerate(stat_args_to_bases.keys()))


	
	def readdir(self, path, fh=None):
		# print("readdir")
		dirs = [".", ".."]
		dirs += self.sftp_client.listdir(self.path_from_root(path))
		return dirs
	
	def open(self, path, flags):
		# print("opening: ", path)
		#download the file from the remote
		remote_path = self.path_from_root(path)
		local_path = self.path_from_temp(path)
		if remote_path not in self.openfiles:
			# print(f"Downloading {remote_path} from remote.")
			Path(os.path.dirname(local_path)).mkdir(parents=True, exist_ok=True)
			self.scp_client.get(remote_path, local_path, recursive=True, preserve_times=True)
			self.openfiles[remote_path] = {
				"path_from_temp": local_path, 
				"is_dirty": False
			}
			
		fd = os.open(local_path, flags)
		self.openfiles[remote_path]["num_open"] = self.openfiles[remote_path].get("num_open", 0) + 1
		return fd

	def read(self, path, size, offset, fh=None):
		# print("read")
		os.lseek(fh, offset, os.SEEK_SET)
		return os.read(fh, size)
	

	def truncate(self, path, length, fh=None):
		# print("truncate: ", fh, path)
		if(fh is None):
			fd = os.open(path, os.O_RDWR)
			os.truncate(fd, length)
			return
		os.truncate(fh, length)


	def write(self, path, buffer, offset, fh):
		# print("write")
		os.lseek(fh, offset, os.SEEK_SET)
		remote_path = self.path_from_root(path)
		result = os.write(fh, buffer)
		self.openfiles[remote_path]["is_dirty"] = True
		return result

	def release(self, path, fh):
		# print("release")
		remote_path = self.path_from_root(path)
		if remote_path not in self.openfiles:
			# print(f'remote_path {remote_path} open but missing from openfiles set')
			raise Exception("failed to release: " + remote_path)
		local_path = self.openfiles[remote_path]["path_from_temp"]
		if self.openfiles[remote_path]["is_dirty"] is True:
			# print("Writing updated file to remote")
			self.scp_client.put(local_path, remote_path=remote_path, recursive=True, preserve_times=True)
		if self.openfiles[remote_path]["num_open"] == 1:
			# print(f'Removing {remote_path} from local system')
			del self.openfiles[remote_path]
			os.remove(local_path)
		else:
			self.openfiles[remote_path]["num_open"] -= 1
	
	def __del__(self):
		# print("__del__")
		shutil.rmtree(self.tempdir)
		self.ssh_client.close()

def main():
	if len(sys.argv) != 3:
		print("Require <roodir> <mountpoint>")
		sys.exit(1)
	rootdir, mountpoint = (sys.argv[1], sys.argv[2])
	FUSE(PyFuse(rootdir, mountpoint), mountpoint, nothreads=True, foreground=True)



if __name__ == '__main__':
	main()


	
	
