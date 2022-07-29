# commands

This role executes arbitrary commands against a Ceph cluster using `cephadm`.

## Prerequisites

### Host prerequisites

* The role assumes target hosts connection over SSH with user that has passwordless sudo configured.
* Either direct Internet access or private registry with desired Ceph image accessible to all hosts is required.

### Inventory

This role assumes the existence of the following groups:

* `mons`

All Ceph hosts must be in the `ceph` group.

## Role variables

* `cephadm_commands`: A list of commands to pass to `cephadm shell -- ceph`
   Example:
   ```
          cephadm_commands:
            - "fs new cephfs cephfs_metadata cephfs_data"
            - "orch apply mds cephfs --placement 3"
   ```
