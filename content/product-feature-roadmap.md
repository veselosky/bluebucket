# Blue Bucket Product Roadmap

Here you will find a list of features that are candidates to be added to the
system in the future. Most of these features are not scheduled or elaborated in
any way. Over time, we will be fleshing out this roadmap to include milestones
and prioritization of features. At the moment it is just a laundry list.

## Version 0.1

* Build & deploy capability; a bucket for software distribution.
* Manual account setup and bucket setup. Automation to follow in future
  releases.
* Core Indexers: item class only, no pagination support, no subset support
* Scribe for Article to page using basic template.
* Only Article item class supported. Others to come.
* Integrate contentful.com as publishing UI.
* Very basic theme with bare templates and minimal CSS, mostly for proof of
  concept and testing.

## Version 0.2

* Indexer pagination support
* Indexer subset support
* Image asset support

## Future Versions: Someday, Maybe

* "Authentication" via AWS API keys only.
* BB Updater function to install BB software suite in AWS account.
* BB Bucket Setup function to bootstrap a website, configure AWS services.
* UI Site Organizer: Inspect and navigate the site.
* UI Article Composer: Basic entry form for creating an article.
* Draft preview support for Article.
* Private drafts and publication workflow.
* Notification to Social Media on Publish
* Scheduled Future Publishing
* Feed Reader / Importer
* Dashboard
    - publishing activity
    - site traffic
    - social media engagement
    - AdSense revenue
    - Amazon associates revenue
    - AWS spend
    - Page load performance
* Calendar: Editorial calendar and task list. JIRA integration?
* Reader & Saver: Feed reader to keep up with news from wherever. Saver to squirrel away saved links for inspiration and ideas for posts. Evernote integration?
* Image suggester: suggests free images from Wikimedia Commons that may be related to your post. PITA to grab free use images from Wikimedia while preserving copyright info and attribution. Automate this. Add with one click.
* Amazon suggester: suggests Amazon items related to the post you are composing. Add affiliate links with one click.
* Collections: Group items into a series or package.
* Wraps API

Docs:

- Website integration patterns
- Solutions to common dynamic vs static issues

