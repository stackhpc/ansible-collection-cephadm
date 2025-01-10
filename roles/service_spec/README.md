# service_spec

This role creates and updates arbitrary service specifications.
It is recommended to be used only where a more specific role does not yet
exist.

## Prerequisites

### Host prerequisites

* The role assumes target hosts connection over SSH with user that has passwordless sudo configured.
* Either direct Internet access or private registry with desired Ceph image accessible to all hosts is required.

### Inventory

This role assumes the existence of the following groups:

* `mons`

All Ceph hosts must be in the `ceph` group.

This role is executed on `cephadm_bootstrap_host`. This defaults to the
first member of the mon group.

## Role variables

* `cephadm_service_spec`: Service spec to apply in YAML (recommended) or dict
  format.
  Example:
  ```
      cephadm_service_spec: |
        service_type: nfs
        service_id: cephnfs
        placement:
          count: 1
          hosts:
            - host1
            - host2
            - host3
        spec:
          port: 2049
          enable_haproxy_protocol: true
        ---
        service_type: container
        service_id: foo
        placement:
          hosts:
            - host1
            - host2
            - host3
        spec:
          image: docker.io/library/foo:latest
          entrypoint: /usr/bin/foo
          uid: 1000
          gid: 1000
          args:
            - "--net=host"
            - "--cpus=2"
          ports:
            - 8080
            - 8443
          envs:
            - PORT=8080
            - PUID=1000
            - PGID=1000
          volume_mounts:
            CONFIG_DIR: /etc/foo
          bind_mounts:
            - ['type=bind', 'source=lib/modules', 'destination=/lib/modules', 'ro=true']
          dirs:
            - CONFIG_DIR
          files:
            CONFIG_DIR/foo.conf:
              - refresh=true
              - username=xyz
              - "port: 1234"
