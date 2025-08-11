---
layout: article
title: "A Year of Working Contract"
tags: web
---

<p class="first-paragraph">
For the past year and a bit I've been working on a contract for a large Canadian Insurance company. I got the opportunity through a friend who runs a contracting firm. The experience of working for this large insurance company was interesting. This post is an account, mostly for my own memory and interest, of the work I did there.
</p>

<!--more-->

## Background

The large insurance company I worked for had recently (over the last 4 years) acquired a number of smaller tech companies that were intended to be rolled into a holistic health + insurance online platform. Large Insurance Co. (as I will hereafter call them) wanted to integrate all of these softwares into a unified web and mobile app. Having started as distinct companies, each product had separate apps, separate servers and separate tech stacks. In order to present them as one unified product to the end user, it was necessary to build a new web app which would talk to all of these backends. This was already more or less built when I joined. The website is a React/NextJS web app with authentication provided by [Microsoft Azure B2C](https://learn.microsoft.com/en-us/azure/active-directory-b2c/overview). This was chosen so that the problem of identity management could be outsourced. It works like this:

1. User initiates sign-in from Large Insurance Co. landing page
2. User is redirected to webpage on Azure B2C domain. User authenticates (with password, SSO or other method)
3. User is redirected back to Large Insurance Co website. Azure B2C ID token--a [JWT](https://en.wikipedia.org/wiki/JSON_Web_Token)--is included in the redirect URL
4. ID token passed to 1 or more backend services. Backend services request user profile from a central Identity Service
5. Identity service verifies JWT and issues user profile

<br />

![](/assets/images/insurance-company-contract/authentication-architecture.png "Diagram of Insurance Co's authentication architecture")
_Diagram of Insurance Co's authentication architecture_

Imagine a fairly standard client rendered React app (NextJS was used for routing only. There was no or server rendering).
However, this app talks to 8 or 9 different backends. The frontend maintains the presentation of a unified app, but behind the facade the system is a patchwork of backends from the aforementioned acquired companies. You might call this an accidental micro service architecture.

## My Work: The New Benefits Service

One of the companies acquired by Large Insurance Co. in the last few years is a benefits administration software. Let's call it MyBenefits. This software enables employees of a company to enrol in benefits packages offered to them by their employer. They might be able to pick from a few preset benefits "modules", or they might get a lot of flexibility when choosing which benefits and insurance coverages to opt for. The system also records related information like their dependants and beneficiaries, and handles annual re-enrolments and life events (such as dependants changes).

The system when it was acquired consisted of a .NET web app and an external service with a database and some business logic--I will refer to this as the Fortress service--which exposed an API that was accessed by the .NET app to read and write data. Importantly, for each client that MyBenefits took on, it would provision a new instance of this software stack (on physical servers that they managed). Each instance had its own subdomain that the client's employees would use to access it.

Our task was to integrate this system into Large Insurance Co.'s new unified web app. Again, this web app was already a "facade" connecting several different backends. When I joined the team, the project had been scoped such that the main two chunks of work were to rebuild the functionality of the .NET app in the client-side React code, and to build a "proxy service" that would accept API requests and redirect them to the correct Fortress instance. The scoping was done without direct communication with the team that had built MyBenefits, and without seeing the code of either the .NET app or the Fortress service.

Shortly after I joined, we did get access to the code for the .NET app. We also asked to see the Fortress source code, but were declined. It was originally assumed that the business logic mostly resided in the Fortress service. After exploring the .NET code, we discovered a lot of business logic was in the server backend.

This was a problem. If we wanted to continue with our plan to duplicate the .NET app in client-side react code, it would:

1. Increase the complexity of the client side code _a lot_
2. Impose security problems

On point 2: the .NET backend code was not the kind of stuff that should client-side. The Fortress Service, as it turns out, is very trusting of the users of its APIs. Meaning, if someone reverse engineered our client-side code, they might be able to take actions that were not intended to be permitted. There was nothing in the Fortress validation preventing actions that should be illegal--it was up to the web app backend to police bad actors.

So I proposed instead that we rewrite the .NET app backend in [Nest.js](https://nestjs.com/). After some discussion, the team was convinced. I think we would have ended up going down this path even if we had begun with the original "proxy service" idea. This change of scope now meant that we had to acknowledge that we were fully rebuilding a software application that had existed for decades and was still being actively developed in parallel. It was mid-May, and the plan was to launch with our first client on November 1--plenty of time right?

We had one saving grace: the November 1st deadline was for supporting a new hire enrolment; that meant that life events (divorce, new dependant, etc.) could come later. Being able to focus on this one event type helped. Still, the timeline was tight.

### Architecture

Here is a look at the system architecture. Note that changing the implentation from "proxy service" to full backend did not affect this architecture much. Our backend service still did not persist any data (besides the mapping from client to Fortress instance). The only thing that changed is that the Nest.JS backend ended up doing a lot more than redirecting requests. If we had forged ahead with the "proxy service", this would have had to go in the client code instead.

![](/assets/images/insurance-company-contract/service-architecture.png "Diagram of the enrolment service architecture")
_Diagram of the enrolment service architecture_

**Notes**

- The identity service stores the user's profile, including which organization (client) they belong to
- Again, there were many instances of the fortress service. We maintained a local database with mappings from client organization to Fortress instance

**A typical server roundtrip**

1. frontend requests backend endpoint. Request includes an event ID
2. User profile is looked up in Identity service; user's organization is included in profile
3. organization used to find correct Fortress instance in local DB
4. Fortress instance is queried one or more times to complete the client request

Given the unavoidable call to the identity service on every server request, we had an incentive to minimize API calls. This was managed with a client-side data fetching library.

### State Management

![](/assets/images/insurance-company-contract/state-management.png "Diagram of the enrolment service's state management")
_Diagram of the enrolment service's state management_

To minimize complexity while also minimizing server roundtrips, we used [RTK Query](https://redux-toolkit.js.org/rtk-query/overview) to perform client-side data fetching. This library caches API requests from the server, and automatically invalidates and refetches endpoints when a resource is mutated. Using this library meant we didn't have to do any hand written state management on the frontend, but we only ever fetched a resource as seldom as required.

The only client state not managed by RTK Query was the user session cookie and the enrolment event ID in the URL. The event ID was included in every API request to return the appropriate resource for the given event.

### We Faced a Few Problems

This project included several curve balls:

#### An unbudgeted migration of our backend service to a new monolith

This required all hands on deck for a few days (and nights).

#### Requirement changes

Large Insurance Co. is a sales-led orgnization. Requirements often changed as a result of a conversation between a sales rep and their client, without any engineer or PM present. This continued right up until the launch deadline.

##### Aside: Sales led vs. Product led organizations

In a nutshell (as I understand it):

- Product-led orgs empower product managers to determine on and prioritize product features. They have a strategic direction set by the executive team of the company, but individual teams are given flexibility in deciding how best to convert those high-level goals into a product roadmap.
- Sales-led orgs decide what should be built based on what has been sold to a customer. In other words, a salesperson promises that a product will have a certain feature set by a certain date in order to close a deal. Engineering & product are left to make it happen.

My [steelman](https://en.wikipedia.org/wiki/Straw_man#Steelmanning) for sales-led organizations is that they may be more likely to be "customer obsessed"--a celebrated virtue in the tech world. But I think strong engineering teams are more likely to thrive in product-led organizations; they are less likely to get hit with scope-creep and last minute requirement changes. Product managers tend to be more technical than salespeople, and they tend to work more closely with engineering.

#### Communication breakdowns

This happened three ways:

1. Between higher level management and my PM
2. Between our engineering team and the engineering team that had built MyBenefits (we were replacing their product. They viewed us as a nuisance at best, and competition at worst)
3. Between our engineering team and the engineering team that owned the identity service--we sometimes needed them to make changes to their service. Sometimes we needed these changes on a timeline. They weren't happy about this.

#### The Fortress service

We did not have access to the source code for the Fortress service or the underlying DB. This meant that some guess work was required. Information was pieced together from looking at the service API, looking at how the .NET backend interacted with Fortress, and squeezing information out of the MyBenefits team when we could.

The Fortress service was not designed to be used by anyone other than the team that built it and had intimate knowledge of it. If a bad request was submitted to the service, it would respond with a 200 OK and silently consider the data invalid. For example, users would add beneficiaries for their benefits which had potential payouts (life insurance, accidental death & dismemberment, etc.). If the beneficiaries were submitted in a state deemed invalid by the Fortress service, it would return a 200 but not include them in the final enrolment object. This meant that the appropriate follow-up events were not triggered. In this case, a form that should have been generated for the user to sign, swearing that their beneficiaries were correct, was not generated. It's worth noting that whether or not the submitted beneficiary object was valid depended on the particular configuration of the client. Different configurations required different information. While we were developing our new service, the configuration of our staging instance of Fortress would change without warning. This was usually because Large Insurance Co.'s sales team was using the same staging instance to run demos. Sometimes the configuration changed for reasons we could never figure out. This was a continual headache for us and a cause of inter-team friction.

### The Good Parts

I did enjoy working on this project. I feel like I got lucky because the engineers on my immediate team were also part of the contracting firm I was working through and were competent collaborators. We were able to commiserate about the dysfunction of Large Insurance Co. together. We also had a lot of freedom over the technical implementation of the requirements. I was especially autonomous when working on the client-side, because I was the only "frontend engineer" on the team. When it came to collaborating on the Nest.JS server, we were able to align on patterns early on that worked well for us and enabled smooth collaboration. Once the main technical concerns were dealt with--the routing of requests to the correct Fortress instance, the proper handling of enrolment events, the interactions with the Identity Service--the rest was a matter of grinding out the re-implementation of the .NET web app. [LLMs](https://www.anthropic.com/claude-code) proved useful for this in two ways: first, for helping to interpret .NET (C#) code, a framework and language that I was not familiar with at the beginning of the project; and second, for helping to write tests to validate correct behaviour, based on interpreting the original .NET code. I did not find LLMs as useful for directly translating the .NET code to Typescript/Nest.JS, because often the translation was not 1:1. We usually had to do things in a slightly different way, and this meant that it was just as fast writing the code by hand. Still, using LLMs significantly sped up the delivery of this project in the two ways mentioned.

## Conclusion

In the end, we were able to meet the deadline.

In some ways this project seems unique: we were working to build a new web app whose database and some (but not all) business logic was contained in a service that we did not control, had no documentation of, which was owned by a team who did not want to help us. In some ways, this might not be so different from other situations in software engineering where you build an integration with an external service. However, when integrating with a service you're paying for, there is usually someone on the other end who is eager to make sure you are successful.

Despite this, we were reasonably successful at rebuilding the part of the benefits service that we needed to, resulting in a seamless, one-login, one-portal experience for the end user to enrol in their benefits.

Working for this company was a learning experience. I had heard stories about what it is like working in large, bureaucratic organizations, but there was value in experiencing it for myself. I'm happy with the work my team managed to do during our time there.
