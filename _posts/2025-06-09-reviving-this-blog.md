---
layout: article
title: "Reviving this blog"
---

<p class="first-paragraph">
I haven't written on this blog in a while. This is partly because I haven't felt like doing long-form writing. It's also because of the way this blog was built and deployed in the past, which made publishing a new piece more work than necessary.
</p>

For a while I've wanted a place to leave thoughts, no matter how short or inconsequential. I used to use Twitter for this, but I don't anymore for obvious reasons. I now use Bluesky sometimes, but I wanted a place of my own to write content of any length or complexity. I have had this website for a few years, but it wasn't really set up for "microblogging". Over the past few weeks, I've migrated this blog to Jekyll & Github pages in order to make it easy to contribute to. I also changed the homepage layout to a format that will make it easy to consume small posts and previews of larger posts without clicking into the article. My old homepage only showed the article title and date, whereas now it should be easy to read an entire short post without clicking on it.

Jekyll + Github pages makes publishing content really easy. I just write my thoughts into a markdown file in my blog git repo, push it to Github, and it's published! For my own interest, I am documenting below the old way my blog was written and published. It will be obvious why this setup created a higher barrier to posting.

<!--more-->

## My Old Blog

Part of why I built this website originally was out of interest in creating a website "from scratch". As someone who has worked as a frontend engineer (also sometimes a fullstack engineer) in the 2020s, I was interested in getting back to basics by working with good ol' HTML and CSS. The web programming I was doing for my day job had many abstractions separating me from these technologies (React, CSS in JS libraries, etc.); I wanted to prove I could still make something nice without bundling hundreds of Javascript libraries.

I also did not want to have to edit tons of html each time I wanted to write a new blog post, so I ended up creating my own crude static site generator. I would write and format my posts using [Notion.so](https://notion.so) and then export my documents as markdown. I used a python library called [marko](https://pypi.org/project/marko/) to convert this to HTML. Then, I [wrote a script](https://github.com/SpLouk/splouk.github.io/blob/e854ba3b9904954f4893925cfc93ad27bbe939fa/build.py) to build the html snippet into a full document with layouts I had built. This meant that, in order to create a new post, I would:

1. Write the post in Notion and export it as markdown
2. Run a script to convert the markdown to HTML, and move the HTML and images into the source directory for the blog
3. Run a build script to regenerate the website
4. Run a publish script to copy the built site to an S3 bucket

This is a bit more involved than `git commit -am '...' && git push`. Especially because I usually had to mess around with the generated html a bit to make sure it looked good. Also, doing something like including a snippet from my articles on the homepage, or pagination--both features I've added pretty easily with Jekyll--would have been pretty involved. The complexity of my build scripts would need to increase quite a bit.

I'm glad I went through the exercise of creating my own SSG, but I came to realize that having any barrier to writing a post means that often the post does not get written. I want this to be a public place where I can think out loud; that means making capturing thoughts as frictionless as possible.
