# ec_profiles

This role creates/deletes Ceph EC profiles.

## Prerequisites

### Host prerequisites

* The role assumes target host connection over SSH to the first MON server.

### Inventory

This role assumes the existence of the following groups:

* `mons`

#### Custom Inventory

You can override the previous groups with your own.

* `mons` -> `cephadm_ansible_mons_group`

## Role variables

* `cephadm_ec_profiles`: A list of pools to manage.
   Example:
   ```
          cephadm_ec_profiles:
            - name: foo
              k: 4
              m: 2
            - name: delete_me
              state: absent
            - name: foo-osd
              k: 4
              m: 2
              crush_failure_domain: osd

   ```

Check Erasure Code profiles [docs](https://docs.ceph.com/en/squid/rados/operations/erasure-code-profile/#osd-erasure-code-profile-set) for supported key options.
