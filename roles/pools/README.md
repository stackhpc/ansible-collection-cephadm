# pools

This role creates/deletes Ceph pools.

## Prerequisites

### Host prerequisites

* The role assumes target hosts connection over SSH with user that has passwordless sudo configured.
* Either direct Internet access or private registry with desired Ceph image accessible to all hosts is required.

### Inventory

This role assumes the existence of the following groups:

* `mons`

All Ceph hosts must be in the `ceph` group.

## Role variables

* `cephadm_pools`: A list of pools to define
   Example:
   ```
          cephadm_pools:
            - name: pool1
              size: 3
              application: rbd
            - name: pool2
              size: 2
              application: rbd
              state: absent 
   ```

Check the `cephadm_pool` module docs for supported pool options.

