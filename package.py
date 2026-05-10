import xml.etree.ElementTree as ET
import shutil
import hashlib
import os

tree = ET.parse('src/addon.xml')
root = tree.getroot()
addon_id = root.attrib.get("id")
with open('./packages/fenlight_version') as f: 
    ver = f.read()
    
root.attrib["version"] = ver
tree.write("src/addon.xml")
output_filename = f"./packages/{addon_id}-{ver}"

os.makedirs(f"./__temp__/{addon_id}")
shutil.copytree(f"src", f"./__temp__/{addon_id}", dirs_exist_ok=True)



shutil.make_archive(output_filename, 'zip', "./__temp__")

shutil.rmtree('./__temp__')


with open("addons.xml", "rb") as f:
    data = f.read()

md5 = hashlib.md5(data).hexdigest()

with open("addons.xml.md5", "w") as f:
    f.write(md5)