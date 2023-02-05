#!/usr/bin/env python3
"""
Simple script to create html from markdown using marko
"""

import argparse
import marko
import glob
import os
import distutils.dir_util


def main(args):
    file = glob.glob("*.md", root_dir=args.directory)[0]
    with open(f"{args.directory}/{file}", "r") as f:
        html_text = marko.convert(f.read())

    article_name = args.article_name or file.split("/")[-1].replace(".md", "")
    article_dir = f"src/{article_name}"
    os.makedirs(f"{article_dir}/resources", exist_ok=True)
    with open(f"{article_dir}/{article_name}.html", "w") as f:
        f.write(html_text)

    resource_dir = file.replace(".md", "")
    if (os.path.exists(resource_dir)):
        distutils.dir_util.copy_tree(f"{args.directory}/{resource_dir}", f"{article_dir}/resources")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Required positional argument")
    parser.add_argument("-n", "--article-name", help="article name", required=False)
    args = parser.parse_args()
    main(args)
