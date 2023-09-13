import json
from pathlib import Path

def default_path():
	cwd = Path(__file__).parents[1]
	cwd = str(cwd)
	return cwd

def open_file(filename, cwd = default_path()):
	with open(f"{cwd}/{filename}.json", "r") as file:
		data = json.load(file)
	return data

def write_file(data, filename, cwd = default_path()):
	with open(f"{cwd}/{filename}.json", "w") as file:
		json.dump(data, file, indent = 4)
