# commands

This role executes arbitrary commands against a Ceph cluster using `cephadm`.

## Prerequisites

### Host prerequisites

* The role assumes target hosts connection over SSH with user that has passwordless sudo configured.
* Either direct Internet access or private registry with desired Ceph image accessible to all hosts is required.

### Inventory

This role assumes the existence of the following groups:

* `mons`

with at least one host in it - see the `cephadm` role for more details.

#### Custom Inventory

You can override the previous groups with your own.

* `mons` -> `cephadm_ansible_mons_group`

## Role variables


* `cephadm_command`: The command to use with the list of commands to execute - defaults to `ceph`, but can be any command found in the `quay.io/ceph/ceph:<tag>` image.
   Example:
   ```
          cephadm_command: radosgw-admin
   ```

* `cephadm_commands`: A list of commands to pass to `cephadm shell -- {{ cephadm_command }}`
   Example:
   ```
          cephadm_commands:
            - "fs new cephfs cephfs_metadata cephfs_data"
            - "orch apply mds cephfs --placement 3"
   ```

* `cephadm_commands_until` A expression to evaluate to allow retrying commands. May reference the registered result variable, `cephadm_commands_result`. Default is `true` (do not use retries).

* `cephadm_commands_retries`: Number of retries to use with `cephadm_commands_until`. Default is 0.

* `cephadm_commands_delay`: Delay between retries with `cephadm_commands_until`. Default is 0.
