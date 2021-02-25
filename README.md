# StackHPC cephadm collection

This repo contains `stackhpc.cephadm` Ansible Collection. The collection includes modules and plugins supported by StackHPC for cephadm based deployments.

## Tested with Ansible

Tested with the current Ansible 2.9 releases.

## Included content

cephadm_deploy role

## Using this collection

Before using the collection, you need to install the collection with the `ansible-galaxy` CLI:

    ansible-galaxy collection install stackhpc.cephadm

You can also include it in a `requirements.yml` file and install it via ansible-galax collection install -r requirements.yml` using the format:

```yaml
collections:
- name: stackhpc.cephadm
```

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## More information

- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## Licensing

Apache License Version 2.0
