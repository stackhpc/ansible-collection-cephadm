# crush_rules

This role creates/deletes Ceph crush rules.

## Prerequisites

### Host prerequisites

* The role assumes target hosts connection over SSH with user that has passwordless sudo configured.
* Either direct Internet access or private registry with desired Ceph image accessible to all hosts is required.

### Inventory

This role assumes the existence of the following groups:

* `mons`

All Ceph hosts must be in the `ceph` group.

## Role variables

* `cephadm_crush_rules`: A list of pools to define
   Example:
   ```
          cephadm_crush_rules:
            - name: replicated_hdd
              bucket_root: default
              bucket_type: host
              device_class: hdd
              rule_type: replicated
              state: present
            - name: replicated_ssd
              bucket_root: default
              bucket_type: host
              device_class: ssd
              rule_type: replicated
              state: present
            - name: ec_ssd
              rule_type: erasure
              profile: ec_4_2_ssd
              state: present 
   ```

Check the `cephadm_crush_rule` module docs for supported key options.

