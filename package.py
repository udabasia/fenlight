import xml.etree.ElementTree as ET
import shutil
import os

tree = ET.parse('src/addon.xml')
root = tree.getroot()
addon_id = root.attrib.get("id")
ver = root.attrib.get("version")
output_filename = f"./packages/{addon_id}-{ver}"

os.makedirs(f"./__temp__/{addon_id}")
shutil.copytree(f"src", f"./__temp__/{addon_id}", dirs_exist_ok=True)



shutil.make_archive(output_filename, 'zip', "./__temp__")

shutil.rmtree('./__temp__')