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
import winreg
# datetime.timezone, datetime, datetime.timedelta

def set_wallpaper(path):
	ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)

def get_all_values_in_key(key):
	res = {}
	i = 0
	while True:
		try:
			subvalue = winreg.EnumValue(key, i)
		except Exception as e:
			# print(e)
			break
		res[subvalue[0]] = subvalue[1:]
		i+=1
	return res

def get_all_colors():
	colors_key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, "Control Panel\\Colors\\", 0, winreg.KEY_ALL_ACCESS | (winreg.KEY_WOW64_64KEY if sys.maxsize > 2**32 else winreg.KEY_WOW64_32KEY))
	res = {k: list(map(int, v[0].split())) for k, v in get_all_values_in_key(colors_key).items()}
	if colors_key:
		winreg.CloseKey(colors_key)
	return res

def set_color(name, value):
	colors_key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, "Control Panel\\Colors\\", 0, winreg.KEY_ALL_ACCESS | (winreg.KEY_WOW64_64KEY if sys.maxsize > 2**32 else winreg.KEY_WOW64_32KEY))
	winreg.SetValueEx(colors_key, name, 0, winreg.REG_SZ, " ".join(map(str, value)))
	if colors_key:
		winreg.CloseKey(colors_key)

def restart_explorer():
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

def get_newest_version():
	url = "https://raw.githubusercontent.com/grinheckerdev/pcmanip/main/src/code/main.py"
	try:
		req = requests.get(url)
		code = req.text
		newest_version = re.findall(r"__version__\s+=\s+(\"|\')(.*)(\"|\')", code)
		# print(1234, newest_version)
		if newest_version: newest_version = newest_version[0]
		if len(newest_version) != 3: return
		newest_version = newest_version[1]
		# print(12345, newest_version)
		newest_version = [int(v) for v in newest_version[1:].split(".")]
		return newest_version
	except ConnectionError:
		return

def get_current_version():
	with open(os.path.join(os.path.dirname(__file__), "main.py"), "r") as f:
		cur_code = f.read()
	current_version = re.findall(r"__version__\s+=\s+(\"|\')(.*)(\"|\')", cur_code)
	if current_version: current_version = current_version[0]
	if len(current_version) != 3: return
	current_version = current_version[1]
	current_version = [int(v) for v in current_version[1:].split(".")]
	return current_version

def version_is_outdated():
	newest_version = get_newest_version()
	# print(111, newest_version)
	if not newest_version: return False
	current_version = get_current_version()
	# print(111, current_version)
	if not current_version: return False
	return newest_version > current_version

class VerticalScrolledFrame(ttk.Frame):
	"""A pure Tkinter scrollable frame that actually works!
	* Use the 'interior' attribute to place widgets inside the scrollable frame.
	* Construct and pack/place/grid normally.
	* This frame only allows vertical scrolling.
	"""
	def __init__(self, parent, *args, **kw):
		ttk.Frame.__init__(self, parent, *args, **kw)

		# Create a canvas object and a vertical scrollbar for scrolling it.
		vscrollbar = ttk.Scrollbar(self, orient=tkinter.VERTICAL)
		vscrollbar.pack(fill=tkinter.Y, side=tkinter.RIGHT, expand=tkinter.FALSE)
		canvas = tkinter.Canvas(self, bd=0, highlightthickness=0,
						   yscrollcommand=vscrollbar.set)
		canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE)
		vscrollbar.config(command=canvas.yview)

		# Reset the view
		canvas.xview_moveto(0)
		canvas.yview_moveto(0)

		# Create a frame inside the canvas which will be scrolled with it.
		self.interior = interior = ttk.Frame(canvas)
		interior.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
		interior_id = canvas.create_window(0, 0, window=interior,
										   anchor=tkinter.NW)

		# Track changes to the canvas and frame width and sync them,
		# also updating the scrollbar.
		def _configure_interior(event):
			# Update the scrollbars to match the size of the inner frame.
			size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
			canvas.config(scrollregion="0 0 %s %s" % size)
			if interior.winfo_reqwidth() != canvas.winfo_width():
				# Update the canvas's width to fit the inner frame.
				canvas.config(width=interior.winfo_reqwidth())
		interior.bind('<Configure>', _configure_interior)

		def _configure_canvas(event):
			canvas.configure(scrollregion=canvas.bbox("all"))
			if interior.winfo_reqwidth() != canvas.winfo_width():
				# Update the inner frame's width to fill the canvas.
				canvas.itemconfigure(interior_id, width=canvas.winfo_width())
			canvas.update()
		canvas.bind('<Configure>', _configure_canvas)

if __name__ == "__main__":
	# check_version()
	print(get_all_colors())
	set_color("Hilight", [255, 0, 0])
	# set_color("Hilight", [0, 120, 215])