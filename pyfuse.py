import sys
import os
from fuse import FUSE, Operations
from paramiko import (SSHClient, AutoAddPolicy)
from scp import SCPClient

username = "altannag"
host = "c220g5-111024.wisc.cloudlab.us"

class PyFuse(Operations):
	def __init__(self, rootdir, mountpoint):
		self.ssh_client = SSHClient()
		self.rootdir = rootdir
		self.mountpoint = mountpoint
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
	
	def path_from_mount(self, path: str):
		return os.path.join(self.mountpoint, 
					   path if not path.startswith("/") else path[1:])
	def getattr(self, remote_path, fh=None):
		#execute lstat on remote
		(stdin, stdout, stderr) = self.ssh_client.exec_command(
			"stat --format='%D %f %s %X %Y %Z' " + self.path_from_root(remote_path)
		)
		stat_vals  = stdout.read().decode('utf-8')
		print("stat: ", stat_vals)
		stat_vals = stat_vals.split(" ")
		stat_args_to_bases = {
			"st_dev": 10, 
			"st_mode": 16, 
			"st_size": 10, 
			"st_atime": 10,
			"st_mtime": 10, 
			"st_ctime": 10
		}
		return dict((key, int(stat_vals[i], base=stat_args_to_bases[key])) for i, key in enumerate(stat_args_to_bases.keys()))

	def readdir(self, remote_path, fh=None):
		dirs = [".", ".."]
		dirs += self.sftp_client.listdir(self.path_from_root(remote_path))
		return dirs
	
	def open(self, path, flags):
		#download the file from the remote
		remote_path = self.path_from_root(path)
		local_path = self.path_from_mount(path)
		self.scp_client.get(remote_path, local_path, recursive=True, preserve_times=True)
		return open(local_path, flags)

	def read(self, path, size, offset, fh=None):
		print(fh)
		return "None"
		os.lseek(fh, offset, os.SEEK_SET)
		return os.read(fh, size)


	def __del__(self):
		self.ssh_client.close()

def main():
	if len(sys.argv) != 3:
		print("Require <roodir> <mountpoint>")
		sys.exit(1)
	rootdir, mountpoint = (sys.argv[1], sys.argv[2])
	FUSE(PyFuse(rootdir, mountpoint), mountpoint, nothreads=True, foreground=True)



if __name__ == '__main__':
	main()


	
	
