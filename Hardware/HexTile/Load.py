# To run, open the KiCad scripting console and type: exec(open('F:/Git/RGBTile/Hardware/HexTile/PlaceLEDs.py').read())
# Can all make a function:
# def Run():
# 	exec(open("F:/Git/RGBTile/Hardware/HexTile/Load.py").read())
# Then use Run()

def Load(path:str):
	import importlib.util
	import sys
	spec = importlib.util.spec_from_file_location("script", path)
	if spec is not None and spec.loader is not None:
		script = importlib.util.module_from_spec(spec)
		sys.modules["script"] = script
		spec.loader.exec_module(script)
		script.PlaceComponents()
	else:
		print(f"Failed to load script '{path}'")

if __name__ == "__main__":
	Load("F:/Git/RGBTile/Hardware/HexTile/PlaceLEDs.py")