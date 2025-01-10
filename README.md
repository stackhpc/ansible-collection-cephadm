# StackHPC cephadm collection

[![Tests](https://github.com/stackhpc/ansible-collection-cephadm/actions/workflows/test.yml/badge.svg)](https://github.com/stackhpc/ansible-collection-cephadm/actions/workflows/test.yml) [![Publish Ansible Collection](https://github.com/stackhpc/ansible-collection-cephadm/actions/workflows/publish-collection.yml/badge.svg)](https://github.com/stackhpc/ansible-collection-cephadm/actions/workflows/publish-collection.yml)

This repo contains `stackhpc.cephadm` Ansible Collection. The collection includes modules and plugins supported by StackHPC for cephadm based deployments.

## Tested with Ansible

Tested with the current Ansible 2.9 and 2.10 releases.

## Included content

Roles:
* [cephadm](roles/cephadm/README.md) for deployment/bootstrapping
* [commands](roles/commands/README.md) for running arbitrary commands
* [crush_rules](roles/crush_rules/README.md) for defining CRUSH rules
* [ec_profiles](roles/ec_profiles/README.md) for defining EC profiles
* [enter_maintenance](roles/enter_maintenance/README.md) for placing hosts into maintenance
* [exit_maintenance](roles/exit_maintenance/README.md) for removing hosts from maintenance
* [keys](roles/keys/README.md) for defining auth keys
* [pools](roles/pools/README.md) for defining pools
* [service_spec](roles/service_spec/README.md) for arbitrary service definition

## Using this collection

Before using the collection, you need to install the collection with the `ansible-galaxy` CLI:

    ansible-galaxy collection install stackhpc.cephadm

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml` using the format:

```yaml
collections:
- name: stackhpc.cephadm
```

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Release notes handling

See [antsibull-changelog docs](https://github.com/ansible-community/antsibull-changelog/blob/main/docs/changelogs.rst) for instructions how to deal with release notes.

## More information

- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## Licensing

Apache License Version 2.0
