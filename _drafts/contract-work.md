---
layout: article
title: "A Year of Working Contract"
---

<p class="first-paragraph">
For the past year and a bit I've been working on a contract for a large Canadian Insurance company. I got the opportunity through a friend who runs a contracting firm. The experience of working for a large insurance company was interesting. This post is an account, mostly for my own memory and interest, of the work I did there.
</p>

<!--more-->

## Background

The large insurance company I worked for had recently (over the last 4 years) acquired a number of smaller tech companies that were to be rolled into a holistic health + insurance online platform. Large Insurance Co. wanted to integrate all of the products into unified web and mobile apps. Having started as distinct companies, each product had separate apps, separate servers and tech stacks. In order to present them as one unified product to the end user, it was necessary to build a new web app which would talk to all of these backends. The groundwork for this was already more or less built when I joined. The website was a React/NextJS web app with authentication provided by [Microsoft Azure B2C](https://learn.microsoft.com/en-us/azure/active-directory-b2c/overview). This was chosen so that the problem of identity management could be outsourced. The architecture works like this:

1. User initiates sign-in from Insurance Co landing page
2. User is redirected to webpage on Azure B2C domain. User authenticates (with password, SSO or other method)
3. User is redirected back to Insurance Co website. Azure B2C ID token--a [JWT](https://en.wikipedia.org/wiki/JSON_Web_Token)--is included in the redirect URL
4. ID token passed to 1 or more backend services
5. Backend services verify JWT and issue user profile

**Diagram of Insurance Co's authentication architecture**

![](/assets/images/insurance-company-contract/authentication-architecture.png "Diagram of Insurance Co's authentication architecture")

Imagine a fairly standard client rendered React app (we did use NextJS but only for routing. There was no SSR or server components).
However, this app talks to 8 or 9 different backends. The frontend maintains the presentation of a unified app, but behind the facade the system is a patchwork of backends from the aforementioned acquired companies. You might call this an accidental micro service architecture.

## My Work: The New Benefits Service

One of the companies acquired by Insurance Co in the last few years is a benefits administration software. I will refer to it as MyBenefits. This company would allow users to enrol in benefits packages offered to them by their employer. They might be able to pick from a few preset benefits "modules", or they might get a lot of flexibility when choosing which benefits and insurance coverages to opt for. The system also recorded related information like their dependants and beneficiaries, and handled annual re-enrolments and life events (such as dependants changes).

The system when it was acquired consisted of a .NET fullstack web app, and a data layer with some business logic--I will refer to this as Fortress for fun--which exposed an API that was accessed by the .NET app to read and write data. Importantly, for each client that MyBenefits took on, it would provision a new physical instance of this software stack (I'm guessing on physical servers that they managed). Each instance had its own subdomain that clients' employees would use to access it.

Our task was to integrate this system into Large Insurance Co.'s unified web app. Again, this web app was already a "facade" connecting several different backends. When I joined the team, the project had been scoped such that the main two chunks of work were to rebuild the functionality of the .NET app in the client-side React code, and to build a "proxy service" that would accept API requests and redirect them to the correct instance of Fortress. The scoping was done without direct communication with the team that had built MyBenefits, and without seeing the code of either the .NET app or the Fortress service.

Shortly after I joined, we did get access to the code for the .NET app. We also asked to see the Fortress source code, but were declined. Seeing the .NET app code made it immediately clear that there was a lot more data manipulation happening on the server-side of this app than was originally assumed. It was originally assumed that the business logic mostly resided in the Fortress service, but it turns out it was spread across both.

This was a problem. If we wanted to continue with our plan to duplicate the .NET app in client-side react code, it would:

1. Increase the complexity of the client side code _a lot_
2. Impose security problems

On point 2: some of the business logic involved was not the kind of stuff that should be in client-side code. The Fortress Service, as it turns out, was very trusting of the users of its APIs. Meaning, if someone reverse engineered our client-side code, they might be able to take actions that were not intended to be permitted. There was nothing in the Fortress validation preventing actions that should be illegal--it was up to the web app backend to police bad actors.
