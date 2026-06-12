# enter_maintenance

This role places Ceph hosts into maintenance mode using `cephadm`.

## Prerequisites

This role should be executed on one host at a time. This can be achieved by
adding `serial: 1` to a play.

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