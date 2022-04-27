# ec_profiles

This role creates/deletes Ceph EC profiles.

## Prerequisites

### Host prerequisites

* The role assumes target hosts connection over SSH with user that has passwordless sudo configured.
* Either direct Internet access or private registry with desired Ceph image accessible to all hosts is required.

### Inventory

This role assumes the existence of the following groups:

* `mons`

## Role variables

* `cephadm_ec_profiles`: A list of pools to define
   Example:
   ```
          cephadm_ec_profiles:
   ```

Check the `cephadm_ec_profile` module docs for supported key options.

