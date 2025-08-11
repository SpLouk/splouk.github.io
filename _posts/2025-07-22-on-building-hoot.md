---
layout: article
title: "On Building Hoot"
tags: web
---

<p class="first-paragraph">
  Hoot is an <a href="https://apps.apple.com/ca/app/hoot-of-the-day/id6743980346" >iOS app</a> that I created for the benefit of my partner, Alana. She gave me the idea for an app that prompts users once per day with a question. Everyone answers that question at the same time, then sees each others' answers. The purpose is to stimulate conversation among friends. As Alana said "my friends are moving to different cities. Our regular chats will become more infrequent if we don't have something to prompt conversation." She used to use Twitter with her friends for this purpose, but none of them use it anymore.
</p>

I built this app as a one-man team, while working another full time job. As a result, I had these goals in mind when making technical decisions about this app:

1. Developer simplicity. I wanted to use technologies that would result in less code to maintain, easy deployments, good built in observability, etc. I tried to make product decisions that would allow for straightforward code.
2. Cost. I wanted to keep the cost of this project relatively low.

This blog post is an overview of how I built the app, and some of the design decisions that I made along the way.

<!--more-->

<div class="hoot-image-container" >
  <img
    width="250"
    src="/assets/images/on-building-hoot/hoot-screen-1.png" />
  <video controls width="250">

    <source src="/assets/images/on-building-hoot/screen-recording.MP4" type="video/mp4" />

  </video>
</div>

## Tech Stack

### React Native vs. Swift

I set out to create an iOS app. I have a background in web development, so React Native was an immediate consideration for the app client. It could have been fun to write a native iOS app, but I knew it would be much faster for me to learn React Native than Swift. There were two other considerations that enticed me to go the React Native approach. First, I like the idea of eventually publishing this app for Android, and starting with React Native obviously makes that quite a bit easier. Second, I knew this app would be mostly about scrolling through text and images, so I wasn't too worried about the performance hit incurred by using React Native. In addition to React Native, Hoot also uses [Expo](https://docs.expo.dev/), which provides awesome utility libraries, a router, a build tool, and automated app store submissions. It is analogous to Next.JS for mobile development.

### Server

I used Ruby on Rails to build the server for this app. It is the web framework I am most familiar with, though I have used [NestJS](https://docs.nestjs.com/) in the past. I wanted to use Rails because I really like it. It's opinionated, mature, and Just Works. Plus, I had not used it in a few years and was excited to try out some of its newer features, such as the [Solid Trifecta](https://www.youtube.com/watch?v=FpfAu20I00A). Rails is an excellent web framework that makes things easy, and doesn't require a ton of overhead. As of today, my production server uses <1GB of memory.

Some other miscellaneous things I like about Rails:

- ActiveJob backed by Solid Queue
- ActiveStorage (make associating remote files with db tables easy)
- Simple deployments with [Kamal](https://kamal-deploy.org/) and Docker
- Multithreaded / multi-process HTTP server with Puma

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

### Schema design

Here is a simplified schema showing the most important tables in Hoot's database and their relations:

![](/assets/images/on-building-hoot/schema.png "Diagram of Hoot's important db tables")

All posts and prompts happen in the context of a group. Users may belong to many groups at once. The UX of the app allows a user to switch between groups easily.

### Client Architecture

The client architecture is designed to be as simple as possible. In order to minimize complexity and stale data, the client does not duplicate any backend state. All data changes are persisted to the db as soon as they happen and fresh data is refetched in the background. This is accomplished using [Tanstack Query](https://tanstack.com/query/latest). Tanstack query eliminates the need for complex frontend state management by allowing each component to fetch the data it needs directly from the backend. Caching, cache invalidation and refetching are handled by the library. It is a powerful tool for simplification of clients. Ephemeral local state is accomplished with the useState React hook. The only global state required is the session and the current group ID. These are kept in [React context](https://react.dev/reference/react/useContext).

![](/assets/images/on-building-hoot/client-architecture.png "Diagram of Hoot's client architecture")

A popular alternative to this sort of architecture would be to use a client-side state management tool, like [Redux](https://redux.js.org/), [Mobx](https://mobx.js.org/README.html), or something homespun (likely with React Context). I prefer the Tanstack Query approach for a few reasons. The first is simplicity. Managing global state on the client side introduces inherent complexity around keeping the client and server in-sync. The benefit of keeping a copy of some state on the client is that you can make updates, persist those updates to the database, but avoid refetching the data since it has already been updated in the client. However, you now need to manage the complexity of having two copies of that state. What if the DB update fails? How often do you refresh your client state from the DB in case it has been changed by another user?

The other supposed advantage of client state management is that you can manage state "derivatives" -- i.e. values that are computed from some persistent state. This allows you to avoid storing more state than is necessary. Redux and Mobx call these "reducers" and "computeds" respectively. I prefer a "barbell" approach to computed derivatives: if the derviative is only used locally in one component, I prefer it to be computed locally there. This results in simpler, cleaner code. If a derivative is widely used, the server should compute it and return it in the JSON payload for that object. If the derivative is computationally intensive, maybe it should be persisted to the database--this isn't the end of the world!

Keeping the client "dumb" results in less complexity to manage as a developer. Tanstack Query manages the hard problem of caching while being relatively simple to reason about.

### Prompt Scheduling

The group table has a column called `prompt_schedule` which contains a string of weekdays on which a new prompt will become active for that group. The string represents weekdays by their order in the week, 0-indexed. For example "135" would represent Monday, Wednesday and Friday. This makes it easy to compare these strings to the current weekday in SQL, so checking whether a given group has a prompt activation today is as simple as:

```ruby
Group.where("prompt_schedule LIKE ?", "%#{Date.today.wday}%")
```

This allows each group to have it's own prompt schedule. Prompts are activated at a random time each day. When the prompt activation job runs, it picks the most voted for prompt from the eligible prompts and activates it. It then sends a notification to all users in the group letting them know.

## Deployment

Hoot uses a cloud-hosted virtual machine as it's main server. The main database and job queue also live on this virtual machine. This is a simple setup, but could be changed in the future to meet scaling needs. Image assets are stored remotely on S3 and managed using [Active Storage](https://guides.rubyonrails.org/active_storage_overview.html). Client builds are created using [Expo Application Services](https://expo.dev/eas) and submitted to the Apple app store. Notifications are sent from the server to Apple's notification service for delivery to the client device. Emails are sent via Sendgrid.

![](/assets/images/on-building-hoot/deployment.png "Hoot in production")

## Conclusion

Building Hoot has been an exercise in building a fully-featured app as a one-man team. In any coding project, managing complexity is the most important goal. This is especially true when there is only one dev!
I'm happy with the way this app has turned out. It's been a lot of fun to build and use with my friends.

Try Hoot out for yourself:
[https://apps.apple.com/ca/app/hoot-of-the-day/id6743980346](https://apps.apple.com/ca/app/hoot-of-the-day/id6743980346)

<div style="display: flex; justify-content: center; padding: 32px 16px;">
  <img
    width="250"
    src="/assets/images/on-building-hoot/logo.png" />
</div>
