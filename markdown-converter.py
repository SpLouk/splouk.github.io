#!/usr/bin/env python3
"""
Simple script to create html from markdown using marko
"""

import argparse
import marko


def main(args):
    with open(args.file, "r") as f:
        html_text = marko.convert(f.read())
    
    new_filename = args.file.split("/")[-1].replace(".md", ".html")
    with open(new_filename, "w") as f:
        f.write(html_text)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Required positional argument")
    args = parser.parse_args()
    main(args)

