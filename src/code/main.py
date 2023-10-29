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
from tkinter import filedialog, scrolledtext, messagebox
import psutil
from utils import *
import platform
import requests

hosts = []
root = notebook = frame_remote_manip = computer_listbox = scan_computers_button = shutdown_labelframe = restart_checkbox = restart_var = force_var = force_checkbox = time_var = time_spinbox = shutdown_button = info_labelframe = info_label = frame_personalization = wallpaper_labelframe = open_wallpaper_button = frame_computer_info = computer_info_text = send_message_labelframe = message_text_scrolledtext = send_message_button = None

global param_names, param_syntax
param_names = {
	"--sv": "--sunvalley",
	"-l": "--light",
	"-d": "--dark",
	"-c": "--console",
	"--tm": "--topmost",
}

for v in param_names.copy().values():
	param_names[v] = v

param_syntax = {
}

for v in param_names.copy().values():
	if v not in param_syntax:
		param_syntax[v] = {"params": []}

# print(param_names, param_syntax)

__version__ = "v0.1.0.6"

class Argv:
	def __init__(self, data):
		self.data = []
		pnames = set(param_names.values())
		for pn in pnames:
			if pn not in [i[0] for i in data if type(i) is list and i[1] == {}]:
				data.append([pn, False])
		for d in data:
			# print(type(d), type(d) is str)
			if type(d) is str:
				self.data.append([d])
			else:
				self.data.append(d)
		# print(self.data)
	def __getitem__(self, item):
		if type(item) is int:
			return self.data[item]
		elif type(item) is str:
			# print("\n")
			# print(1, item)
			for arg, *par in self.data:
				# print(2, arg, par)
				if item == arg:
					if par!=[False]:
						return par
					else:
						return (True if par == [{}] else False)
			raise KeyError(item)
		else:
			raise KeyError(f"Argv indices must be integers or strings, not {type(item).__name__}")

def main_old(argv):
	if len(argv) == 2: shutdown_computer(argv[1], force=True)

	local_ip = get_local_ip()
	public_ip = get_public_ip()

	mask = get_subnet_mask()
	cidr = get_cidr(mask)

	print(local_ip, public_ip, mask, cidr)

	interface = ipaddress.ip_interface(public_ip+"/"+str(cidr))

	threads = []
	for host in map(str, interface.network.hosts()):
		if host != public_ip:
			x = threading.Thread(target = check_ip, args=(host,))
			x.start()
			threads.append(x)

	for x in threads:
		x.join()

	for h in hosts:
		if input(f"Press 'y' to turn off computer {h[0]} with ip {h[1]} > ").lower() == 'y':
			shutdown_computer(h[1])
			print(f"Turned off computer {h[1]} with ip {h[0]}")

def main(argv):
	print("Curently unavailable!")
	sys.exit(1)

def check_ip_gui(host):
	try:
		name = socket.gethostbyaddr(host)
		hosts.append([host, *name])
		#print(socket.getsockname(host))
		# print(name)
		computer_listbox.insert(tkinter.END, name[0])
	except socket.herror:
		pass

def scan_computers_gui():
	local_ip = get_local_ip()
	public_ip = get_public_ip()

	mask = get_subnet_mask()
	cidr = get_cidr(mask)

	# print(local_ip, public_ip, mask, cidr)

	interface = ipaddress.ip_interface(public_ip+"/"+str(cidr))

	computer_listbox.delete(0, tkinter.END)

	threads = []
	for host in map(str, interface.network.hosts()):
		# if host != public_ip:
		# 	x = threading.Thread(target = check_ip_gui, args=(host,))
		# 	x.start()
		# 	threads.append(x)
		x = threading.Thread(target = check_ip_gui, args=(host,))
		x.start()
		threads.append(x)

def shutdown_computer_gui():
	for i in computer_listbox.curselection():
		h = computer_listbox.get(i)
		x = threading.Thread(target=shutdown_computer, args=(h,))
		x.start()

def update_info(event):
	if len(computer_listbox.curselection()) > 0:
		a = computer_listbox.curselection()[-1]
		h = computer_listbox.get(a)
		# print(h)
		host = []
		for i in hosts:
			if i[1] == h:
				host = i
                
		info_label.configure(text=f"Your public IP: {get_public_ip()}\nYour local IP: {get_local_ip()}\nIP: {host[0]}\n Name: {host[1]}")

def show_help():
	print("This is help. Maybe.", file = sys.stderr)

def unpack_argv(argv):
	try:
		new_argv = []
		for arg in argv.copy():
			if arg[0] == "-":
				if arg[1] == "-":
					try:
						arg = [param_names[arg]]
					except KeyError:
						print(f"ERROR: Unknown parameter name '{arg.replace('-', '')}'!")
						return
				else:
					if len(arg) == 2:
						try:
							arg = [param_names[arg]]
						except KeyError:
							print(f"ERROR: Unknown parameter name '{arg.replace('-', '')}'!")
							return
					elif len(arg) > 2:
						arg_ = []
						for a in arg[1:]:
							try:
								arg_.append(param_names["-"+a])
							except KeyError:
								print(f"ERROR: Unknown parameter name '{a.replace('-', '')}' in '-{arg[1:]}'!")
								return
						arg = arg_
			else:
				arg = [arg]
			new_argv.extend(arg)
		return new_argv
	except:
		traceback.print_exc()
		return None

def add_text_computer_info(text, end="\n"):
	computer_info_text.configure(state ='normal')
	computer_info_text.insert(tkinter.INSERT, text+end) 
	computer_info_text.configure(state ='disabled')

def update_text_about_computer():
	computer_info_text.configure(state ='normal')
	computer_info_text.delete('1.0', tkinter.END)
	computer_info_text.configure(state ='disabled')

	add_text_computer_info(f"NETWORK INFO:")
	add_text_computer_info(f"Computer name: {socket.gethostname()}")
	add_text_computer_info(f"Computer local IP: {get_local_ip()}")
	add_text_computer_info(f"Computer public IP: {get_public_ip()}")

	add_text_computer_info(f"\nSOFTWARE INFO:")
	add_text_computer_info(f"Platform name: {sys.platform}")
	add_text_computer_info(f"Full platform name: {platform.platform()}")
	add_text_computer_info(f"OS name: {os.name}")
	add_text_computer_info(f"OS version: {platform.version()}")

	add_text_computer_info(f"\nHARDWARE INFO:")
	add_text_computer_info(f"Logical CPUs: {psutil.cpu_count()}")
	add_text_computer_info(f"Physical CPUs: {psutil.cpu_count(logical=False)}")
	cpu_percentage = " ".join([str(i)+'%' for i in psutil.cpu_percent(percpu=True)])
	add_text_computer_info(f"CPUs percentage: {cpu_percentage}")
	add_text_computer_info(f"CPU architecture: {platform.machine()}")

	add_text_computer_info(f"\nOTHER INFO:")
	add_text_computer_info(f"Boot time: {round(psutil.boot_time(), 2)}")

	power_info = psutil.sensors_battery()
	add_text_computer_info(f"\nBATTERY INFO:")
	if power_info:
		plugged_in = ("Yes" if power_info.power_plugged else "No")
		add_text_computer_info(f"Plugged in: {plugged_in}")
		add_text_computer_info(f"Battery percentage: {round(power_info.percent, 2)}%")
		add_text_computer_info(f"Seconds left: {round(power_info.secsleft)}")
	else:
		add_text_computer_info(f"No battery info available!")

	# add_text_computer_info(f"")
	# add_text_computer_info(f"")
	# add_text_computer_info(f"")
	# add_text_computer_info(f"")
	# add_text_computer_info(f"")
	# add_text_computer_info(f"")
	# add_text_computer_info(f"")
	# add_text_computer_info(f"")
	# add_text_computer_info(f"")
	# add_text_computer_info(f"")

def parse_argv(argv):
	print(argv)
	if not argv: return Argv(argv)
	new_argv = unpack_argv(argv)
	if new_argv is None:
		show_help()
		sys.exit(1)

	i = 0
	argv = new_argv.copy()
	new_argv.clear()
	# print(argv)
	while i < len(argv):
		# print(i)
		arg = argv[i]
		# print(arg, i)
		new_arg = [arg, {}]
		i+=1
		# print(arg)
		if arg[0] == '-':
			# print(4, arg)
			for j, param in enumerate(param_syntax[arg]["params"]):
				try:
					par = argv[i]
					i+=1
				except IndexError:
					print(f"ERROR: Argument '{arg.replace('-', '')}' needs {len(param_syntax[arg]['params'])} arguments, but {j} were given!")
					show_help()
					sys.exit(1)
				try:
					new_arg[1][param["name"]] = param["type"](par)
				except ValueError:
					print(f"ERROR: parameter #{j} ({param['name']}) for argument '{arg.replace('-', '')}' must be {param['type'].__name__}! (Got {par!r})")
					show_help()
					sys.exit(1)
				except:
					traceback.print_exc()
					show_help()
					sys.exit(1)
		else:
			# print(5, arg)
			new_arg = arg
		# print(new_arg)
		new_argv.append(new_arg)
	argv = new_argv.copy()
	new_argv.clear()
	# print(argv)
	return Argv(argv)

def choose_and_set_wallpaper():
	fn = filedialog.askopenfilename(filetypes=[("Image", "*.png"), ("Image", "*.jpg"), ("Image", "*.jpeg")])
	if fn:
		set_wallpaper(fn)

def send_message_computer_gui():
	for i in computer_listbox.curselection():
		h = computer_listbox.get(i)
		x = threading.Thread(target = send_message, args=(h, message_text_scrolledtext.get("1.0", tkinter.END)))
		x.start()

def show_version_warning():
	cur_ver = get_current_version()
	if not cur_ver: cur_ver = "?"
	else: cur_ver = "v"+".".join(map(str, cur_ver))

	new_ver = get_newest_version()
	if not new_ver: new_ver = "?"
	else: new_ver = "v"+".".join(map(str, new_ver))

	# print(f"Current version: {cur_ver}\nNewest version: {new_ver}")

	messagebox.showwarning(title="Version outdated",
				message=f"This version of pcmanip is outdated!\nCurrent version: {cur_ver}\nNewest version: {new_ver}\nDownload new version from github.com/grinheckerdev/pcmanip")


def main_gui(argv):
	global root, notebook, frame_remote_manip, computer_listbox, scan_computers_button, shutdown_labelframe, restart_checkbox, restart_var, force_var, force_checkbox, time_var, time_spinbox, shutdown_button, info_labelframe, info_label, computer_info_textframe_personalization, wallpaper_labelframe, open_wallpaper_button, frame_computer_info, computer_info_text, send_message_labelframe, message_text_scrolledtext, send_message_button
	
	if version_outdated:
		x = threading.Thread(target = show_version_warning)
		x.start()

	root = tkinter.Tk()
	root.title("PCmanip")
	if argv["--topmost"]:
		root.wm_attributes("-topmost", 1)

	if argv["--sunvalley"]: sv_ttk.set_theme("light" if argv["--light"] else "dark")

	################################################################################################################################################

	notebook = ttk.Notebook(root)
	notebook.pack(expand=True, fill=tkinter.BOTH)

	
	frame_remote_manip = ttk.Frame(notebook)
	frame_remote_manip.pack(fill=tkinter.BOTH, expand=True)


	computer_listbox = tkinter.Listbox(frame_remote_manip, selectmode = tkinter.EXTENDED)
	computer_listbox.grid(column = 0, row = 0, columnspan = 3, padx=5, pady=5)
	computer_listbox.bind('<<ListboxSelect>>', update_info)

	scan_computers_button = ttk.Button(frame_remote_manip, text = "Scan", command=scan_computers_gui)
	scan_computers_button.grid(column = 0, row = 1, padx=5)


	shutdown_labelframe = ttk.LabelFrame(frame_remote_manip, text="Shutdown")
	shutdown_labelframe.grid(column = 0, row = 2, columnspan = 3, pady=5, rowspan = 3)

	restart_var = tkinter.BooleanVar()
	restart_checkbox = ttk.Checkbutton(shutdown_labelframe, var=restart_var, text="Restart")
	restart_checkbox.pack(anchor=tkinter.W, pady=0)

	force_var = tkinter.BooleanVar()
	force_checkbox = ttk.Checkbutton(shutdown_labelframe, var=force_var, text="Force-quit")
	force_checkbox.pack(anchor=tkinter.W, pady=0)

	time_var = tkinter.IntVar()
	time_spinbox = ttk.Spinbox(shutdown_labelframe, from_=1, to=99, textvariable=time_var)
	time_spinbox.pack(anchor=tkinter.W, pady=5)

	shutdown_button = ttk.Button(shutdown_labelframe, text="Shutdown", command=shutdown_computer_gui)
	shutdown_button.pack(anchor=tkinter.W, pady=5)

	
	send_message_labelframe = ttk.LabelFrame(frame_remote_manip, text="Message")
	send_message_labelframe.grid(column = 3, row = 2, columnspan = 3, rowspan = 3)

	message_text_scrolledtext = scrolledtext.ScrolledText(send_message_labelframe, width=30, height=8)
	message_text_scrolledtext.pack(fill = tkinter.BOTH, expand=True)

	send_message_button = ttk.Button(send_message_labelframe, text="Send", command=send_message_computer_gui)
	send_message_button.pack()


	info_labelframe = ttk.LabelFrame(frame_remote_manip, text="Info")
	info_labelframe.grid(column = 3, row = 0, pady=5)

	info_label = tkinter.Label(info_labelframe, text=f"Your public IP: {get_public_ip()}\nYour local IP: {get_local_ip()}\nIP: -\n Name: -")
	info_label.pack(fill = tkinter.BOTH)

	notebook.add(frame_remote_manip, text="Remote manipulation")

	################################################################################################################################################

	frame_personalization = ttk.Frame(notebook)
	frame_personalization.pack(fill=tkinter.BOTH, expand=True)

	wallpaper_labelframe = ttk.LabelFrame(frame_personalization, text="Wallpaper")
	wallpaper_labelframe.grid(row=0, column=0)

	open_wallpaper_button = ttk.Button(wallpaper_labelframe, text = "Set wallpaper", command = choose_and_set_wallpaper)
	open_wallpaper_button.pack()

	notebook.add(frame_personalization, text="Personalization")

	################################################################################################################################################

	frame_computer_info = ttk.Frame(notebook)
	frame_computer_info.pack(fill=tkinter.BOTH, expand=True)

	computer_info_text = scrolledtext.ScrolledText(frame_computer_info, font = ("Courier", 8), width=0, height=0)
	computer_info_text.configure(state ='disabled')
	computer_info_text.pack(fill=tkinter.BOTH, expand=True)
	update_text_about_computer()

	computer_info_update_button = ttk.Button(frame_computer_info, text="Update", command=update_text_about_computer)
	computer_info_update_button.pack()

	notebook.add(frame_computer_info, text="Computer info")

	root.update()
	print(root.winfo_width(), root.winfo_height())
	# root.bind("<Configure>", lambda e: print(e.width, e.height))
	# root.resizable(0, 0)
	root.mainloop()

if __name__ == '__main__':
	version_outdated = version_is_outdated()
	if "-c" in sys.argv[1:]:
		main_old(parse_argv(sys.argv[1:]))
	else:
		main_gui(parse_argv(sys.argv[1:]))
