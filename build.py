#!/usr/bin/env python3

from html.parser import HTMLParser
from html.entities import name2codepoint
import shutil
import os
import glob
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
    
    article_file = glob.glob('*.html', root_dir=root)[0]
    print(article_file)
    with open(f"{root}/{article_file}", "r") as f:
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

def build_site():
    os.makedirs('build/resources', exist_ok=True)
    generate_articles()
    shutil.copy("src/styles.css", "build/")
    shutil.copy("src/header.jpg", "build/resources/")
    shutil.copy("src/header-small.jpg", "build/resources/")

if __name__ == "__main__":
    build_site()