# SciComp Dashboard

This is a simple [Flask](http://flask.pocoo.org/) web application
that's eventually intended to show the status of various SciComp
processes.

At present it just shows the users on the `gizmo` and `beagle`
clusters (the raw data is obtained each time the page is loaded,
by `ssh`'ing to the `rhino` machines and running `squeue` and `sinfo`).

But it's easy to add more functionality--just add a route in
[app.py](app.py) and then add a link to your route in the
`nav` section of the [layout](templates/layout.html) template.


## Deployment

This app is [deployed](https://scicomp-dashboard.fhcrc.org/) using our on-premises [CircleCI](https://circle.fhcrc.org)
and [Rancher](https://ponderosa.fhcrc.org)
installations.

This is NOT an automated DevOps pipeline; it was created manually. But it
points the way towards future automation.
