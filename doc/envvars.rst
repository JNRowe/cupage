Configuration via environment variables
=======================================

:program:`cupage` defaults for many options can be configured via environment
variables.  The design purpose for supporting these environment variables is
to make it easy for users to configure per-project defaults using shell hooks.

.. envvar:: CUPAGE_PROFILE

   This controls whether to profile the execution of :program:`cupage`.  It must
   be a string value, and will be used as the profile’s output filename.
