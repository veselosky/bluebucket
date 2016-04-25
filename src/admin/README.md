# Blue Bucket Admin

This is the administrative interface for the blue bucket project.

## Version 0.1

See [Github Milestone](https://github.com/veselosky/bluebucket/milestones/Version%200.1)
for details.

In this first version we are going absolutely bare. We will add only enough
interface to prove out the concept by running some Lambda functions. Later we
will return to this interface and iterate to improve the site management and
content production experience.

NOTE: S3 cannot be accessed from the browser until you have configured CORS for
S3 (unless you always load the web page from an S3 DNS name, but I do not want
to enforce that constraint). Chicken-egg. Interactions with S3 will go through
Lambda, as Lambda has CORS enabled. For this version, I'll only trigger Lambda
directly from the browser, without configuring API Gateway. I don't need public
endpoints yet.

Other Notes:

* We include jQuery, Bootstrap, and the AWS SDK from CDN to save storage and
  bandwidth.
