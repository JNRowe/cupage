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

.. blockdiag::


   diagram {
     "Site" -> "Sites";
     group A {
        "Site";
        "matches" -> "Site";
        "checked" -> "Site";
     }
     "number" -> "checked";
     "string" -> "array" -> "matches";
   }

``matches`` is an array, and contains the string matches of previous
:program:`cupage` runs.

``checked`` is the offset in seconds from the Unix epoch since the site was last
checked.  It is normally a float, but may be ``null``.

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
            "checked": 1256677592.0
        },
        "interlude": {
            "matches": [
                "interlude-1.0.tar.gz"
            ],
            "checked": null
        }
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
