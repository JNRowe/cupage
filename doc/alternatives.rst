Alternatives
============

Before diving in and spitting out this package I looked at the alternatives
below.  If I have missed something please drop me a mail_.

It isn’t meant to be unbiased, and you should try the packages out for yourself.
I keep it here mostly as a reference for myself, and maybe to help out people
who are already familiar with one of the entries below so they can see where I'm
coming from.

.. _mail: jnrowe@gmail.com

``ck4up``
---------

ck4up_ is a small tool written in Ruby which scans webpages for updates by
storing the hash of checked pages.  It provides pretty much the same
functionality as ``cupage``, but in a slightly different manner.

The major differences are a lack of HTTP cache support, a more manual
configuration method and no built in support for various hosting sites.

.. _ck4up: http://jue.li/crux/ck4up/

``urlwatch``
------------

urlwatch_ is a great little tool, which sends you emails containing the
differences in web pages.  To some extent ``cupage`` is mostly a narrow subset
of the functionality provided by ``urlwatch``, and the functionality could have
been implemented on top with a bunch of hooks.

In my opinion the disadvantages are a lack of HTTP cache support, the
configuration requires users to write Python and no built in support for various
hosting sites.  The massive advantage is how configurable and hackable the tool
can be thanks to the "config is a python script" design.

.. _urlwatch: http://thp.io/2008/urlwatch/
