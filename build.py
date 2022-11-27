#!/usr/bin/env python3

from html.parser import HTMLParser
from html.entities import name2codepoint
import shutil
import os
import json
import chevron
from datetime import datetime

def format_date(dt: datetime):
    return dt.strftime('%B %d, %Y')

def generate_articles():
    articles = []
    for root, dirs, files in os.walk("./src"):
        if "article.json" in files:
            metadata = generate_article_get_metadata(root)
            articles.append(metadata)

    # Sort articles; we expect date formatted as "%B %d, %Y"
    # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    articles.sort(key=lambda metadata: datetime.strptime(metadata['date'], "%B %d, %Y"), reverse=True)
    generate_index(articles)

def generate_index(articles):
    with open(f"./src/index.html.mustache", "r") as f:
        article_content = f.read()
    with open("./src/article-template.html.mustache", "r") as f:
        html_output = chevron.render(**{
            'template': f,
            'data': {
                "show_title": False,
                "articles": articles
            },
            'partials_dict': {
                "article_content": article_content,
            },
        })
    with open(f"./build/index.html", "w") as output_file:
        output_file.write(html_output)

# Generate an article from the given dir, return the metadata
def generate_article_get_metadata(root: str):
    with open(f"{root}/article.json", "r") as f:
        metadata = json.load(f)
    with open(f"{root}/content.html", "r") as f:
        article_content = f.read()
    with open("./src/article-template.html.mustache", "r") as f:
        html_output = chevron.render(**{
            'template': f,
            'data': {
                "title": metadata["title"],
                "show_title": ("title" in metadata),
                "date": metadata["date"],
            },
            'partials_dict': {
                "article_content": article_content,
            },
        })

    # Write the file
    metadata['url'] = root.split("/")[-1]
    with open(f"./build/{metadata['url']}.html", "w") as output_file:
        output_file.write(html_output)
    
    # copy over resources
    for _, dirs, files in os.walk(f"{root}/resources"):
        for file in files:
            shutil.copy(f"{root}/resources/{file}", "./build/resources/")

    return metadata


if __name__ == "__main__":
    os.makedirs('build/resources', exist_ok=True)
    generate_articles()
    shutil.copy("src/styles.css", "build/")
    shutil.copy("src/header-cropped.jpg", "build/resources/")


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("Start tag:", tag)
        for attr in attrs:
            print("     attr:", attr)

    def handle_endtag(self, tag):
        print("End tag  :", tag)

    def handle_data(self, data):
        print("Data     :", data)

    def handle_comment(self, data):
        print("Comment  :", data)

    def handle_entityref(self, name):
        c = chr(name2codepoint[name])
        print("Named ent:", c)

    def handle_charref(self, name):
        if name.startswith("x"):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        print("Num ent  :", c)

    def handle_decl(self, data):
        print("Decl     :", data)


parser = MyHTMLParser()
