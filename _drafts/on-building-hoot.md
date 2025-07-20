---
layout: article
title: "On Building Hoot"
---

<p class="first-paragraph">
  Hoot is an <a href="https://apps.apple.com/ca/app/hoot-of-the-day/id6743980346" >iOS app</a> that I created for the benefit of my partner, Alana. She gave me the idea for an app that prompts users once per day with a question. Everyone answers that question at the same time, then sees each others' answers. The purpose is to stimulate conversation among friends. As Alana said "my friends are moving to different cities. Our regular chats will become more infrequent if we don't have something to prompt conversation." She used to use Twitter with her friends for this purpose, but none of them use it anymore.
</p>

I built this app as a one-man team, while working another full time job. As a result, I had these goals in mind when making technical decisions about this app:

1. Developer simplicity. I wanted to use technologies that would result in less code to maintain, easy deployments, good built in observability, etc. I tried to make product decisions that would allow for straightforward code.
2. Cost. I wanted to keep the cost of this project relatively low.

This blog post is an overview of how I built the app, and some of the design decisions that I made along the way.

## Tech Stack

### React Native vs. Swift

I set out to create an iOS app. I have a background in web development, so React Native was an immediate consideration for the app client. It could have been fun to write a native iOS app, but I knew it would be much faster for me to learn React Native than Swift. There were two other considerations that enticed me to go the React Native approach. First, I like the idea of eventually publishing this app for Android, and starting with React Native obviously makes that quite a bit easier. Second, I knew this app would be mostly about scrolling through text and images, so I wasn't too worried about the performance hit incurred by using React Native. In addition to React Native, Hoot also uses [Expo](https://docs.expo.dev/), which provides awesome utility libraries, a router, a build tool, and automated app store submissions. It is analogous to Next.JS for mobile development.

### Server

I used Ruby on Rails to build the server for this app. It is the web framework I am most familiar with, though I have used [NestJS](https://docs.nestjs.com/) in the past. I wanted to use Rails because I really like it. It's opinionated, mature, and Just Works. Plus, I had not used it in a few years and was excited to try out some of its newer features, such as the Solid Trifecta. Rails is an excellent web framework that makes things easy, and doesn't require a ton of overhead. As of today, production server uses <1GB of memory.

## Authentication

Ruby on Rails is a full stack web framework, which means it is designed for cookie authentication. When using it as an API with a mobile app client, another solution is needed. I decided to go with token auth. There are gems which can make this work for rails, such as devise. But in order to minimize dependencies and learn a bit about authentication, I decided to roll my own. Token authentication is actually pretty simple in theory:

1. Client provides server with some credentials (a username & password combo, an [Apple ID token](https://developer.apple.com/documentation/authenticationservices/asauthorizationappleidcredential/identitytoken), etc.)
2. Server responds with a token
3. Client uses that token in subsequent requests to access protected resources

Here is a diagram of the authentication system used by Hoot:
<br />
![](/assets/images/on-building-hoot/authentication.png "Diagram of Hoot's authentication architecture")

The session object has the following schema:

| Name                     | Type     |
| ------------------------ | -------- |
| token                    | string   |
| refresh_token            | string   |
| token_expires_at         | datetime |
| refresh_token_expires_at | datetime |

When the app starts up, it looks for a session object in the device's secure storage (accessed through [expo-secure-store](https://docs.expo.dev/versions/latest/sdk/securestore/)). If found:

1. If refresh_token expired, prompt user to authenticate
2. If token expired, initiate refresh call to get a new one
3. Proceed with other server requests

Session tokens are short lived, with an expiry time of 1 hour, while refresh tokens live 90 days.

### Why roll my own authentication?

The alternative to building my own authentication would be to use something like [Devise](https://github.com/heartcombo/devise). But using Devise would have meant
another dependency, and adding some complexity to my app architecture. Again, Rails and Rails gems are designed for websites.
Comparatively, implementing my own authentication required little code (<500 lines across client/server), and is infinitely extendible/customizable. Since I fully own and understand the
code, it would be easy for me to add a new authentication method. I've already done so: initially Hoot only supported sign-in with Apple, but I implemented email auth before launching to the App Store.

## Architecture

### Groups vs. Follows

Every action taken in Hoot, aside from editing the user profile, creating a group, or logging out, happens in the context of a group. Think of a group like a groupchat in a messaging app: they are invite only and private, but all members of a group see all posts in the group.
Originally, Hoot used a follower/following network (similar to Instagram and other true social media apps) but I moved to a "group" model. It has a few benefits:

- prompts and responses are particular to the culture of a given group. You wouldn't write the same way in a family groupchat as in one with your friends.
- Groups are simpler: when using a follower-following model, you need to make some hard decisions like: do you see replies to posts by people you're following, even if you don't follow the reply author? In a group, everyone sees every post. Everyone knows who can see the posts they make.
- Hoot is not a true social media app. Hoot is for people who are already connected IRL to spark conversations. The asymmetrical following/follower is useful for apps where influential users broadcast content to large audiences. The group model is better for intimate conversations.

### Schema

![](/assets/images/on-building-hoot/schema.png "Diagram of Hoot's important db tables")
