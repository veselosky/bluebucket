itemtype: Item/Page/Article
guid: 50c5cda2-f9d1-43a0-b773-7047ffb7b641
ID: 16  
atom_id: tag:www.webquills.org,2007:/scroll//1.6  
Created: 2007-12-15 16:43:20
Published: 2007-05-30 21:15:51  
updated: 2007-12-15 16:43:20
category: web-development/perl
slug: beyond-perl
title: Beyond Perl?

# Beyond Perl?

That's right, I give up. Despite having devoted the last five years exclusively
to Perl development, my next project will be written in another language.

I am not happy about this, quite the contrary. I love Perl. I've learned so much
of the ins and outs of Perl syntax vagaries that I feel like I've been married
to it. But for at least a year I have been looking at the web development tools
and frameworks in other languages and drooling. Where are the Perl tools that
will double my productivity in web development? No, for two years I have spent
most of my time <em>building</em> those tools for myself, because those
available do not suit my needs and do not measure up to the tools available in
several other languages. But of course, I'm not as smart as those other guys, so
my home-grown tools are not as good, and not really useful outside my personal
bubble.

Now, the Perl fanatics out there are going to start yelling about things like <a
href="http://www.catalystframework.org/">Catalyst</a> and maybe <a
href="http://jifty.org/view/HomePage">Jifty</a>. Hey, I know, because I am (was)
a Perl fanatic myself. But Catalyst is unnecessarily complicated. In trying to
be all things to all programmers, it creates more slow-downs in overhead than it
does speed-ups in infrastructure. Jifty is pretty cool, and it even comes with a
pony, but it just isn't there yet, and the community behind it is comparatively
small. None of the Perl frameworks I've examined make it particularly easy to
implement REST-based web services (it's certainly possible, but the frameworks
don't make it any easier than doing it "by hand").

Now, if I had my druthers, based purely on language syntax and tools, I probably
would go with Python, and a framework like <a
href="http://www.djangoproject.com/">Django</a>. Django is a beautiful piece of
work, in my mind the Python alternative to <a
href="http://www.rubyonrails.org/">Ruby on Rails</a>, and far superior in
productivity to <a href="http://zope.org/">Zope</a> or anything based on it.
Also, Python's <a href="http://www.feedparser.org/">Universal Feed Parser</a> is
by far the best library for manipulating RSS and Atom feeds that I have found in
any language.

But there are also disadvantages to choosing Django over PHP. PHP has the
simplest deployment path, and is still the most broadly deployed of the
open-source technologies on my radar. Django requires mod_python or FastCGI, and
Rails similarly relies on FastCGI. These technologies are not widely deployed
and not nearly as simple as just dropping a bundle of files into your document
root.

But really there are some big reasons for me to run PHP: <a
href="http://www.wordpress.org" title="Wordpress">Wordpress</a>, <a
href="http://www.mediawiki.org/wiki/MediaWiki">MediaWiki</a> and <a
href="http://www.phpbb.com/">phpBB</a>. These are excellent applications at what
they do, and I need to run them on my new web server for compatibility with
previous deployments. And all are built with PHP. Since I have to have PHP
installed anyway...

So in addition to Django, I will also give <a
href="http://www.symfony-project.com/">symfony</a> a test-drive. This is a PHP
web framework. I have no experience with it yet, but it looks more mature than
the <a href="http://framework.zend.com">Zend Framework</a>, seems fully capable
of doing what I want, and happens to be the first hit on Google for "PHP
framework", so there must be plenty of people who think it's good.

My relationship with Perl has not ended. I'm still building large-scale
applications with it at my day job, and I have no doubt I will turn to it when
the going gets tough in my sysadmin role at home. But it's time for me to
stretch my legs, to look at some other languages in the hope of finding tools
that will increase my productivity the way Perl did when I first started using
it. Python and Django will be my first try, followed closely by PHP and symfony.
And if neither works out, well, there's always Rails.



