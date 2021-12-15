# keys

This role creates/deletes Ceph keys (cephx).

## Prerequisites

### Host prerequisites

* The role assumes target hosts connection over SSH with user that has passwordless sudo configured.
* Either direct Internet access or private registry with desired Ceph image accessible to all hosts is required.

### Inventory

This role assumes the existence of the following groups:

* `ceph`
* `mons`
* `mgrs`
* `osds`

Optional groups (those services will be deployed when group exists)::

* `rgws`

All Ceph hosts must be in the `ceph` group.

## Role variables

* `cephadm_keys`: A list of pools to define
   Example:
   ```
          cephadm_keys:
            - name: client.user1
            - name: client.user2
              state: absent 
   ```

Check the `cephadm_key` module docs for supported key options.

