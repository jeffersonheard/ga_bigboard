ga_bigboard - Teleconferencing Over Maps
##########################################

Introduction
============

The Big Board is a system for doing "Teleconferencing over maps."  It is distributed as a standalone Django app meant to
be used in conjunction with other Geoanalytics apps (github.com/JeffHeard/ga_*) to create a collaborative environment
over which to discuss georeferenced data in context with the wider world.  The Big Board is based on HTML5, Javascript,
and Django and runs in-browser over HTTP without any extensions such as Flash, Java, or other plugins.  It is mobile-
ready, developed with JQueryMobile and OpenLayers for tablet devices and standards compliant browsers.  It was
originally developed as a decision-support tool for emergency managers to collaborate before and during a widespread
emergency, such as a hurricane.

External requirements and installation
======================================

    * Django 1.3 or 1.4 with all standard apps enabled, including admin.
    * Django Tastypie 0.9.11 or better
    * Django Celery 2.5
    * OpenLayers 2.11 or better
    * JQuery 1.6 or better
    * JQueryMobile 1.1.0

The Big Board is distributed as a Django app.  You must have sufficient privileges to install Django apps on your
machine and a working Django installation.  If you have that, simply run::

    $ python setup.py install

and add the ``ga_bigboard`` application to the list of installed applications in :file:`settings.py`.  After that, add
:module:`bigboard.urls` to your Django :file:`urls.py` to setup an endpoint for the Big Board in your web heirarchy.

Quickstart guide for administrators
===================================

Currently adding users, roles, and rooms is achieved through the Django Admin tool.  This may change in the future as
people other than site administrators may be assigned the responsibility of creating these but for now, this is the
state of our art.  All rooms and overlays must have at least one role assigned to them to be visible, and a role should
have at least one user assigned to it (although it is possible to have blank roles).

Users
-----

Users are part of the main Django authentication system.  Follow your system's instructions on creating users.

Roles
-----

A role is nothing more than a name.  In the future, roles will be able to be assigned by a rule engine based on a user's
membership in other roles, but for now, they are directly assigned.  Go to the admin tool and find "roles" under
the heading "Ga_bigboard" and add at least one role, selecting at least one user to add to the role.

One note: right now, roles must be assigned by an administrator.  There is a flag for "self-assignable" roles in the
role portion of the admin tool.  This is reserved for future use and may allow user's to claim certain roles for
themselves.

Overlays
--------

Overlays are provided by standard webservices such as WMS or WFS.  Services containing layers may be setup as part of
your `Geoanalytics`_ installation, or separately by servers such as `GeoServer`_ or `MapServer`_. These

Overlays are probably the most complicated of the items you must create for a room.  This is because an overlay can
be any constructable Openlayers.Layers.Vector or OpenLayers.Layers.WMS object.  You must therefore fill in the section
for "default creation options" with a Javascript object containing the options to be passed to the OpenLayers layer
constructor.  Follow the `OpenLayers`_ API documentation for more information.

.. _Geoanalytics: http://geoanalytics.renci.org
.. _GeoServer: http://geoserver.org
.. _OpenLayers: http://openlayers.org
.. _MapServer: http://www.mapserver.org

Rooms
-----

Once you have a role, a user, and an overlay created, you can add a conference room.  Of course one user for your
conference isn't very interesting, but that's sort of beside the point.  To add a conference room, it needs:

    * A name, which must be unique.
    * A basic description (can be blank).
    * A number of roles to which this room is visible.
    * A center point and base zoom level (these can be changed later by users from within the room).
    * A base layer.  This can either be one of the Google layers, Open Streetmap, or an OGC Web Map Service (WMS)
      provided by your system administrator or a third party map provider.  The one restriction on this is that
      the provider **must** provide the map in **EPSG:3857** (Google Mercator) projection.


