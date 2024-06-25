==============================
stackhpc.cephadm Release Notes
==============================

.. contents:: Topics

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

- Deprecate `generate_keys` functionality in cephadm_keys plugin
- Deprecate `fetch_inital_keys` functionality in cephadm_keys plugin
- Fix issue with idempotency in cephadm_keys plugin, by no longer
  generating user keyring files on Ceph hosts.


v1.13.0
=======

Release Summary
---------------

Minor release adding support for choosing plugin in EC profiles


Minor Changes
-------------

- Add support for choosing plugin in EC profiles
