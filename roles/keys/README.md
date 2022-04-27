# keys

This role creates/deletes Ceph keys (cephx).

## Prerequisites

### Host prerequisites

* The role assumes target hosts connection over SSH with user that has passwordless sudo configured.
* Either direct Internet access or private registry with desired Ceph image accessible to all hosts is required.

### Inventory

This role assumes the existence of the following groups:

* `mons`

## Role variables

* `cephadm_keys`: A list of keys to define
   Example:
   ```
          cephadm_keys:
            - name: client.glance
              caps:
                mon: "profile rbd"
                osd: "profile rbd pool=images"
                mgr: "profile rbd pool=images"
            - name: client.user2
              caps:
                mon: "allow r"
                mgr: "allow rw"
              state: absent 
   ```

Check the `cephadm_key` module docs for supported key options.

