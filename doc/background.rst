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

The database is just a serialisation of the necessary persistent data from
:class:`Site` objects, namely header data and current matches.

.. [#] Initially Pickle_ was used in versions prior to 0.3.0.  The switch was
   made as Pickle_ provided no benefits over :abbr:`JSON (JavaScript Object
   Notation)`, and some significant drawbacks including the lack of support from
   other languages.

.. _atom: http://www.atomenabled.org/
.. _freshmeat: http://freshmeat.net/
.. _Pickle: http://docs.python.org/library/pickle.html
.. _Python: http://www.python.org/
.. _json: http://docs.python.org/library/json.html


