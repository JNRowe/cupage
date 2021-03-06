Background
----------

I had been looking for a better way to help me keep on top of software releases
for the projects I'm interested in, be that either personally or for things we
use at work.

Some projects have Atom_ feeds, some have mailing lists for release updates,
some post updates on sites like freshmeat_ and some have no useful update
watching mechanism at all.  Tracking all these resources is annoying and
a simple unified solution would be much more workable.

|modref| is that solution, at least for my purposes.  Maybe it could be for you
too!

.. _database-label:

Database
~~~~~~~~

With a local, unified tool we would instantly gain easy access to the updates
database for use from other tools and applications.

|JSON| was chosen as it is simple to read and write, especially so from Python_
using the json_ module [#]_.

The database is a simple serialisation of the :class:`cupage.Sites` object.  The
:class:`cupage.Sites` object is a container for :class:`cupage.Site` objects.
Only persistent data from :class:`cupage.Site` objects that can not be
regenerated from the configuration file is stored in the database, namely last
check time stamp and the current matches.

.. blockdiag::

   diagram {
     "Site" -> "Sites";
     group A {
        "Site";
        "matches" -> "Site";
        "checked" -> "Site";
     }
     "string" -> "array" -> "matches";
     "number" -> "checked";
   }

``matches`` is an array, and contains the string matches of previous
:program:`cupage` runs.

``checked`` is the offset in seconds from the Unix epoch that the site was last
checked.  It is normally a float, but may be ``null`` prior to the first update.

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

.. [#] Pickle_ was used in versions prior to 0.3.0.  The switch was made as
   Pickle_ provided no benefits over |JSON|, and some significant drawbacks
   including the lack of support for reading it from other languages.

.. _atom: http://www.atomenabled.org/
.. _freshmeat: http://freshmeat.net/
.. _Pickle: https://docs.python.org/3/library/pickle.html
.. _Python: https://www.python.org/
.. _json: https://docs.python.org/3/library/json.html
