==============================
stackhpc.cephadm Release Notes
==============================

.. contents:: Topics

v1.22.1
=======

- Override repo for Squid on Rocky 10

v1.22.0
=======

Minor Changes
-------------

- Add Tentacle support

v1.21.1
=======

Bugfixes
--------

- prechecks - change groups existence check to run once
- prechecks - fix groups existing assertion

v1.19.1
=======

Bugfixes
--------

- pools - cephadm_pool tasks now correctly run with sudo

v1.16.0
=======

Release Summary
---------------

Fix idempotency issue in cephadm_keys plugin. `cephadm_keys` no
longer generates keyring files on Ceph hosts, and additional tasks
are required to write keyring files to disk - see the cephadm_keys
README.md for further details.

Minor Changes
-------------

- Deprecate `fetch_inital_keys` functionality in cephadm_keys plugin
- Deprecate `generate_keys` functionality in cephadm_keys plugin
- Fix issue with idempotency in cephadm_keys plugin, by no longer generating user keyring files on Ceph hosts.

v1.13.0
=======

Release Summary
---------------

Minor release adding support for choosing plugin in EC profiles

Minor Changes
-------------

- Add support for choosing plugin in EC profiles
