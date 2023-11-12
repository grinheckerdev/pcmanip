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
from tkinter import filedialog, scrolledtext, messagebox, colorchooser
import psutil
from utils import *
import platform
import requests
import keyboard
import mouse
import multiprocessing
from pprint import pprint

hosts = []
root = notebook = frame_remote_manip = computer_listbox = scan_computers_button = shutdown_labelframe = restart_checkbox = restart_var = force_var = force_checkbox = time_var = time_spinbox = shutdown_button = info_labelframe = info_label = frame_personalization = wallpaper_labelframe = open_wallpaper_button = frame_computer_info = computer_info_text = send_message_labelframe = message_text_scrolledtext = send_message_button = blocked_keys_listbox = None

global param_names, param_syntax
param_names = {
	"--sv": "--sunvalley",
	"-l": "--light",
	"-d": "--dark",
	"-c": "--console",
	"--tm": "--topmost",
	"-h": "--help",
	"--help_me_please_i_am_so_lost": "--help"
}

param_descriptions = {
	"--sunvalley": "Turns on the sunvalley ttk theme for the GUI.",
	"--light": "Turns the light mode on if the --sunvalley flag is set.",
	"--dark": "Turns the dark mode on if the --sunvalley flag is set.",
	"--console": "Console mode (currently unavailable).",
	"--topmost": "Makes window always stay on top.",
	"--help": "Displays help."
}

for v in param_names.copy().values():
	param_names[v] = v

param_syntax = {
}

flag1 = False
choice = None

for v in param_names.copy().values():
	if v not in param_syntax:
		param_syntax[v] = {"params": []}

# print(param_names, param_syntax)

__version__ = "v0.1.0.11"

previous_blocked_keys = []

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

	# print(local_ip, public_ip, mask, cidr)

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
	# print("This is help. Maybe.", file = sys.stderr)
	print("\nArguments and flags:\n")
	for param, syntax in param_syntax.items():
		alternatives = [k for k, v in param_names.items() if v == param and k != param]
		if "--help_me_please_i_am_so_lost" in alternatives:
			alternatives.remove("--help_me_please_i_am_so_lost")
		# print(param, alternatives, syntax)
		if syntax["params"]:
			print(f"  Argument {param}:")
		else:
			print(f"  Flag {param}:")
		print("    Alternatives:", " ".join(alternatives))
		descr = "\n".join(["      "+l for l in param_descriptions[param].split("\n")])
		print("    Description:\n", descr, sep="")
		print()

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
	dt = datetime.datetime.fromtimestamp(psutil.boot_time())
	dt_formatted = dt.strftime("%c")
	add_text_computer_info(f"Boot time: {dt_formatted}")

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
	# print(argv)
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

def key_pressed_set_choice(key):
	global choice
	choice = key.name

# def update_keys():
# 	global previous_blocked_keys
# 	blocked_keys = blocked_keys_listbox.get(0, END)
# 	print(blocked_keys, previous_blocked_keys)
# 	previous_blocked_keys = blocked_keys

def set_flag1(v):
	global flag1
	flag1 = v

def key_select_popup(block_keys = []):
	global flag1, choice
	flag1 = False
	choice = None
	r = tkinter.Tk()
	r.wm_attributes("-toolwindow", 1)
	r.title("Choose key")
	r.update()
	l = ttk.Label(r, text="> Press any key <")
	l.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
	b1 = ttk.Button(r, text="Ok", command = lambda: set_flag1(True))
	b1.grid(row=1, column=0)
	b2 = ttk.Button(r, text="Cancel", command = lambda: set_flag1(True))
	b2.grid(row=1, column=1)

	r.focus_force()
	r.update()

	# process = multiprocessing.Process(target=key_and_set_flag, args=(l,))
	# process.start()
	try:
		while not flag1 and r.winfo_exists():
			r.update()
			if choice:
				l["text"] = f"> {choice} <"
		r.destroy()
	except tkinter.TclError:
		pass
	# process.terminate()
	return choice

def change_color_gui(name, b):
	color = colorchooser.askcolor(b["bg"])[0]
	if color:
		set_color(name, color)
		avg = sum(color)/len(color)
		if avg > 128:
			inverse = 0
		else:
			inverse = 255
		bg = '#{:02x}{:02x}{:02x}'.format(*color)
		fg = '#{:02x}{:02x}{:02x}'.format(inverse, inverse, inverse)
		b.config(bg = bg, fg = fg, activebackground = bg, activeforeground = fg)

def restart_explorer_gui():
	x = threading.Thread(target=restart_explorer)
	x.start()

def add_block_key():
	result = key_select_popup()
	if result and result not in blocked_keys_listbox.get(0, tkinter.END):
		blocked_keys_listbox.insert(tkinter.END, result)
		keyboard.block_key(result)

def remove_block_key(failed=[]):
	failed_new = []
	for i in list(blocked_keys_listbox.curselection())+failed:
		key = blocked_keys_listbox.get(i)
		if key:
			try:
				keyboard.unblock_key(key)
				blocked_keys_listbox.delete(i)
			except KeyError:
				pass
		else:
			failed_new.append(i)
	if failed_new:
		root.after(30, remove_block_key, failed_new)
	blocked_keys_listbox.focus_force()

def check_version_gui():
	version_outdated = version_is_outdated()
	if version_outdated:
		show_version_warning()

def main_gui(argv):
	global root, notebook, frame_remote_manip, computer_listbox, scan_computers_button, shutdown_labelframe, restart_checkbox, restart_var, force_var, force_checkbox, time_var, time_spinbox, shutdown_button, info_labelframe, info_label, computer_info_textframe_personalization, wallpaper_labelframe, open_wallpaper_button, frame_computer_info, computer_info_text, send_message_labelframe, message_text_scrolledtext, send_message_button, blocked_keys_listbox

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

	info_label = ttk.Label(info_labelframe, text=f"Your public IP: {get_public_ip()}\nYour local IP: {get_local_ip()}\nIP: -\n Name: -")
	info_label.pack(fill = tkinter.BOTH)

	notebook.add(frame_remote_manip, text="Remote manipulation")

	################################################################################################################################################

	frame_personalization = ttk.Frame(notebook)
	frame_personalization.pack(fill=tkinter.BOTH, expand=True)

	wallpaper_labelframe = ttk.LabelFrame(frame_personalization, text="Wallpaper")
	wallpaper_labelframe.grid(row=0, column=0)

	open_wallpaper_button = ttk.Button(wallpaper_labelframe, text = "Set wallpaper", command = choose_and_set_wallpaper)
	open_wallpaper_button.pack()

	try:
		colors = get_all_colors()

		colors_labelframe = ttk.LabelFrame(frame_personalization, text="Colors")
		colors_labelframe.grid(row=0, column=1)

		colors_scrolling_frame = VerticalScrolledFrame(colors_labelframe)
		colors_scrolling_frame.pack()

		# print(colors)

		for k, v in colors.items():
			print(k, v)
			avg = sum(v)/len(v)
			if avg > 128:
				inverse = 0
			else:
				inverse = 255
			bg = '#{:02x}{:02x}{:02x}'.format(*v)
			fg = '#{:02x}{:02x}{:02x}'.format(inverse, inverse, inverse)
			b = tkinter.Button(colors_scrolling_frame.interior, text = k, bg = bg, fg = fg, activebackground = bg, activeforeground = fg)
			b.config(command = lambda k=k, b=b: change_color_gui(k, b))
			b.pack(fill = tkinter.X, expand = True)

		# apply_colors_button = ttk.Button(colors_labelframe, text = "Apply", command = restart_explorer_gui)
		# apply_colors_button.pack()

		apply_colors_label = ttk.Label(colors_labelframe, text="To apply settings reboot.")
		apply_colors_label.pack()
	except:
		traceback.print_exc()

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

	################################################################################################################################################

	frame_keyboard_mouse = ttk.Frame(notebook)
	frame_keyboard_mouse.pack(fill=tkinter.BOTH, expand=True)

	blocked_keys_labelframe = ttk.LabelFrame(frame_keyboard_mouse, text="Block keys")
	blocked_keys_labelframe.grid(row=0, column=0)

	blocked_keys_listbox = tkinter.Listbox(blocked_keys_labelframe, selectmode = tkinter.EXTENDED)
	# blocked_keys_listbox["command"] = blocked_keys_listbox.focus_force
	blocked_keys_listbox.grid(column = 0, row = 0, columnspan = 2, padx=5, pady=5)

	add_block_key_button = ttk.Button(blocked_keys_labelframe, text="+", command=add_block_key)
	add_block_key_button.grid(row=1, column=0)

	remove_block_key_button = ttk.Button(blocked_keys_labelframe, text="-", command=remove_block_key)
	remove_block_key_button.grid(row=1, column=1)


	# key_bindings_scrolling_frame = VerticalScrolledFrame(frame_keyboard_mouse)
	# key_bindings_scrolling_frame.grid(row=0, column=1)


	# sample_key_bindings_frame = ttk.Frame(key_bindings_scrolling_frame.interior)
	# sample_key_bindings_frame.pack(anchor = tkinter.NW, fill = tkinter.X, expand=True)
	# key_button = ttk.Button(sample_key_bindings_frame, text = "space")
	# key_button.grid(row=0, column=0)
	# action_combobox = ttk.OptionMenu(sample_key_bindings_frame, tkinter.StringVar(), "enter keys", "enter keys", "press key", "open file", "open topmost pcmanip")
	# action_combobox.grid(row=0, column=1)
	# action_parameters = ttk.Frame()


	# frame_keyboard_mouse.columnconfigure(1, minsize=80)

	notebook.add(frame_keyboard_mouse, text="Keyboard/Mouse")

	root.update()
	print(root.winfo_width(), root.winfo_height())
	# root.bind("<Configure>", lambda e: print(e.width, e.height))
	# root.resizable(0, 0)
	root.mainloop()

if __name__ == '__main__':
	keyboard.hook(key_pressed_set_choice)
	x = threading.Thread(target=check_version_gui)
	x.start()
	argv = parse_argv(sys.argv[1:])
	if argv["--help"]:
		show_help()
	elif argv["--console"]:
		main(argv)
	else:
		main_gui(argv)
