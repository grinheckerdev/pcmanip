import subprocess
import socket
import ipaddress
import threading
import time
import os
import sys
import tkinter
from tkinter import ttk
import ctypes
import sv_ttk
import traceback
import shlex
from tkinter import filedialog, scrolledtext
import psutil
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import shutil
import datetime
import requests
from requests.exceptions import ConnectionError
import re
# datetime.timezone, datetime, datetime.timedelta

def set_wallpaper(path):
	ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)

def remove_windows_not_activated():
	os.system("taskkill /F /IM explorer.exe && explorer.exe")

def get_public_ip():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80)) 
	return s.getsockname()[0]

def get_local_ip():
	return socket.gethostbyname(socket.gethostname())

def get_subnet_mask():
	local_ip = get_local_ip()
	proc = subprocess.Popen('ipconfig', stdout=subprocess.PIPE)
	while True:
		line = proc.stdout.readline()
		if local_ip.encode() in line:
			break
	mask = proc.stdout.readline().rstrip().split(b':')[-1].replace(b' ',b'').decode()
	return mask

def get_cidr(mask = None):
	if not mask: mask = get_subnet_mask()
	cidr = 0
	for i in mask.split("."): cidr += bin(int(i))[2:].count("1")
	return cidr

def shutdown_computer(name, reboot=False, time=1, force=False):
	os.system(f"shutdown {'/s' if not reboot else '/r'} /m \\\\{name} {'/t '+str(time) if time else ''}{' /f' if force else ''}")

def check_ip(host):
	try:
		name = socket.gethostbyaddr(host)
		print(socket.getsockname(host))
		#hosts.append([host, name[0]])
		print(host, "Yes.")
	except socket.herror:
		pass
		print(host, "No.")

def send_message(name, text, time_close=999999):
	os.system(f"msg /SERVER:{name} * /TIME:{time_close} \"{text}\"")

def check_version():
	url = "https://raw.githubusercontent.com/grinheckerdev/pcmanip/main/src/code/main.py"
	try:
		req = requests.get(url)
		code = req.text
		with open(os.path.join(os.path.dirname(__file__), "main.py"), "r") as f:
			cur_code = f.read()
		newest_version = re.findall(r"__version__\s+=\s+(\"|\')(.*)(\"|\')", code)
		if len(newest_version) != 3: return False
		newest_version = newest_version[1]
		current_version = re.findall(r"__version__\s+=\s+(\"|\')(.*)(\"|\')", cur_code)
		if len(current_version) != 3: return False
		current_version = current_version[1]
		newest_version = [int(v) for v in newest_version[1:].split(".")]
		current_version = [int(v) for v in current_version[1:].split(".")]
		return newest_version > current_version
	except ConnectionError:
		return False

if __name__ == "__main__":
	check_version()
