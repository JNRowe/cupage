Background
----------

I had been looking for a better way to help me keep on top of software releases
for projects I'm interested in, be that either personally or for things we use
at work.

Many projects have Atom_ feeds, some have mailing lists just for release updates
and some post updates on sites like freshmeat_. Tracking all these resources is
annoying and a simple unified solution would be much more workable.

:mod:`cupage` is that solution, at least for my purposes and maybe it could be
for you.

.. _database-label:

Database
''''''''

With a local, unified tool we would instantly gain easy access to the updates
database for use from other tools and applications.

:abbr:`JSON (JavaScript Object Notation)` was chosen as it is simple to read and
write, especially so from Python_ using json_ [#]_.

The database is just a serialisation of the :class:`Sites` object.  The
:class:`Sites` object is a simple container for :class:`Site` objects.  Only
necessary persistent data from :class:`Site` objects that can not be
regenerated from the configuration file are stored in the database, namely
header data and current matches.

.. aafig::
   :textual:

   +=======+    +==========+       +--------+
   | Sites +<---+   Site   |     --| string |
   +=======+    +==========+    /  +--------+
                | etag     |<---
                |          |        +--------+
                | checked  |<-------| number |
                |          |        +--------+
                | matches  |<----
                |          |     \ +-------+   +--------+
                | modified |<-    -| array |<--| string |
                +----------+  \    +-------+   +--------+
                               \
                                +--------+
                                | number |
                                +--------+

``etag`` is the server provided :abbr:`HTTP (HyperText Transfer Protocol)`
:abbr:`ETag (Entity Tag)` header, it can be any arbitrary string.

``matches`` is an array, and contains the string matches of previous
:program:`cupage` runs.

``checked`` and ``modified`` are offsets in seconds from the Unix epoch and are
normally floats.  ``checked`` is the time of the last run.  ``modified`` is the
time of the server provided ``Last-Modified`` header.

.. note::
   ``etag``, ``checked`` and ``modified`` may be ``null``.

An example database file could be:

.. code-block:: js

    {
        "geany-plugins": {
            "matches": [
                "geany-plugins-0.17.1.tar.bz2",
                "geany-plugins-0.17.1.tar.gz",
                "geany-plugins-0.17.tar.bz2",
                "geany-plugins-0.17.tar.gz",
                "geany-plugins-0.18.tar.bz2",
                "geany-plugins-0.18.tar.gz"
            ],
            "etag": "\"18e8-476f10d77e604\"",
            "modified": 1256677592.0
        },
        "interlude": {
            "matches": [
                "interlude-1.0.tar.gz"
            ],
            "etag": null,
            "modified": null
        },
        "subtle": {
            "matches": [
                "subtle-0.8.1041-beta.tbz2",
                "subtle-0.8.1056-beta.tbz2",
                "subtle-0.8.1112-gamma.tbz2",
                "subtle-0.8.1192-delta.tbz2",
                "subtle-0.8.1383-epsilon.tbz2",
                "subtle-0.8.1602-zeta.tbz2",
                "subtle-0.8.997-alpha.tbz2"
            ],
            "etag": "\"acc120cb3a4363bc9f9942d7615d9da7\"",
            "modified": null
        },
    }

.. [#] Initially Pickle_ was used in versions prior to 0.3.0.  The switch was
   made as Pickle_ provided no benefits over :abbr:`JSON (JavaScript Object
   Notation)`, and some significant drawbacks including the lack of support from
   other languages.

.. _atom: http://www.atomenabled.org/
.. _freshmeat: http://freshmeat.net/
.. _Pickle: http://docs.python.org/library/pickle.html
.. _Python: http://www.python.org/
.. _json: http://docs.python.org/library/json.html


