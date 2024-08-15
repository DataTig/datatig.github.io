---
layout: blog
title:  "Hub Released"
---

This summer we have started a Hub website - a web app that can host the data from many repositories with features to:

* Build the data automatically on any change (checks regularly and responds to webhooks).
* Allow people to use the data, with browse, search, exports and API.
* Provide forms for people to edit and create new data, with a markdown editor if applicable.
* Log in with GitHub and have their changes appear as commits on GitHub automatically.
* Report on the data - it's correctness and errors, stats about the data and link checking any URLs in the data.

It supports GitHub, but it can also work with any Git host that provides a public Git point to clone from. 
The code is structured so it's possible to add support for other hosts like GitLab later.

This is [now available online at hub.datatig.com](https://hub.datatig.com/).

The [source code is open source](https://github.com/DataTig/Hub) so you can host this yourself. 
For [full hosting requirements see the docs](https://datatig-hub.readthedocs.io/en/latest/).

It's written in Django and uses [our Open Source python library](https://pypi.org/project/DataTig/) heavily. 
While developing the Hub we have also developed the library this summer, releasing version 0.6 with new features. 
The Hub also provides a space to experiment with new features before they are ready to make it into the library. 
(For example link checking is currently only available in the Hub, but will make it into a library release later.)



