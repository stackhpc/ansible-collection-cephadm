# keys

This role creates/deletes Ceph keys (cephx).

## Prerequisites

### Host prerequisites

* The role assumes target hosts connection over SSH with user that has passwordless sudo configured.
* Either direct Internet access or private registry with desired Ceph image accessible to all hosts is required.

### Inventory

This role assumes the existence of the following groups:

* `mons`

#### Custom Inventory

You can override the previous groups with your own.

* `mons` -> `cephadm_ansible_mons_group`

## Role variables

* `cephadm_keys`: A list of keys to define
   Example:
   ```yaml
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

* Keyrings are never written to disk on Ceph hosts by tasks in this role. If a Cephadm keyring should
  be written to the filesystem the following approach can be taken:
  ```yaml
    - name: Get Ceph keys
      stackhpc.cephadm.cephadm_key:
        name: client.glance
        output_format: plain
        state: info
      register: cephadm_key_info
      become: true

    - name: Write Ceph keys to disk
      vars:
        cephadm_key: "{{ cephadm_key_info.stdout }}"
        cephadm_user: "{{ cephadm_key_info.name }}"
      copy:
        # Include a trailing newline.
        content: |
          {{ cephadm_key }}
        dest: "/etc/ceph/ceph.{{ cephadm_user }}.keyring"
      become: true
  ```