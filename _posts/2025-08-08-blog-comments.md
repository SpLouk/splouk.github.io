---
layout: article
title: "Adding Comments To This Blog With Bluesky"
bluesky_cid: 3lvw4zv2yos2j
tags: web
---

<p class="first-paragraph">
  I came across this <a href="https://natalie.sh/posts/bluesky-comments/">blog post</a> on Hackernews the other day and wanted to do something similar for my own blog. My reasons for doing this are similar to those outlined in the original post:
</p>

- Comments are nice to have. This site doesn't exactly have huge readership, but I like the idea that someone could leave a comment here if they wanted to.
- That said, it is not worthwhile for me to implement my own comment solution.
- Many people have Bluesky accounts already. It is convenient to not have to make a new account to comment on my website.
- Outsourcing the data hosting, account management, etc. to Bluesky is very nice.

Natalie used React to create the blog post UI, and her blog is powered by Astro. Getting this working in Jekyll with pure Javascript was pretty simple (<100 lines of code, mostly written by ChatGPT). I'm not bothering with image support, linking back to Bluesky (except at the top) or any of the other fancier stuff that natalie b. did for now. I may improve on this eventually, but I'm happy to support text responses only for now.

The only friction with this solution is that I have to go back and edit my post's [front matter](https://jekyllrb.com/docs/front-matter/) with the CID after creating the blog post and linking to it from Bluesky, but this isn't too much hassle.

You can see the code used to fetch and render Bluesky comments on this site's [github repo](https://github.com/SpLouk/splouk.github.io/blob/main/_layouts/article.html#L13).
