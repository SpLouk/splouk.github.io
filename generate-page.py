#!/usr/bin/env python3
"""
Simple script to create html from markdown using marko
"""

import argparse
import marko


def main(args):
    with open("./src/page-template.html", "r") as f:
        template_text = f.read()

    with open(args.file, "r") as markdown_file:
        html_text = marko.convert(markdown_file.read())

    splice_idx = template_text.find("</main>")
    output = template_text[:splice_idx] + html_text + template_text[splice_idx:]
    
    new_filename = args.o if args.o else args.file.split("/")[-1].replace(".md", ".html")
    with open(new_filename, "w") as f:
        f.write(output)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Required positional argument")
    parser.add_argument("-o", help="Output file")
    args = parser.parse_args()
    main(args)

