#!/usr/bin/env python3

from html.parser import HTMLParser
from html.entities import name2codepoint
import shutil
import os
import json
import chevron
from datetime import datetime
import re

def do_fun():
    with open("src/on-montreal/content.html", "r") as f:
        new_file = f.read()

    match = re.compile("(?<=resources\/).*\.JPG")
    matches = match.findall(new_file)
    print(len(matches))
    for (index, name) in enumerate(matches):
        print(name)
        shutil.move(f"src/on-montreal/resources/{name}", f"src/on-montreal/resources/img_{index}.jpg")
        new_file = new_file.replace(name, f"img_{index}.jpg")
        new_file = new_file.replace(name.upper(), f"img_{index}.jpg")


    with open("src/on-montreal/content.html", "w+") as f:
        f.write(new_file)
    

if __name__ == "__main__":
    do_fun()