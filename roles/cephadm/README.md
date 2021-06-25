cephadm
=======

This role bootstraps and configures Ceph using cephadm.

Inventory
---------

This role assumes the existence of the following groups:

* `ceph`
* `mons`
* `mgrs`
* `osds`

Optional groups (those services will be deployed when group exists)::

* `rgws`

All Ceph hosts must be in the `ceph` group.

Role variables
--------------

* General
  * `cephadm_ceph_release`: Ceph release to deploy (default: octopus)
  * `cephadm_fsid`: FSID to use for cluster (default: empty - cephadm will generate FSID)
  * `cephadm_recreate`: If existing cluster should be destroyed and recreated (default: False)
  * `cephadm_custom_repos`: If enabled - the role won't define yum/apt repositories (default: False)
  * `cephadm_package_update`: If enabled - cephadm package will be updated to latest version (default: False)
  * Bootstrap settings
    * `cephadm_enable_dashboard`: If enabled - dashboard service on MGR will be enabled (default: False)
    * `cephadm_enable_firewalld`: If enabled - firewalld will be installed and rules will be applied (default: False)
    * `cephadm_enable_monitoring`: If enabled - cephadm monitoring stack will be deployed i.e. prometheus/node-exporters/grafana (default: False)
    * `cephadm_install_ceph_cli`: If enabled - ceph cli will be installed on the hosts (default: False)
    * `cephadm_ssh_public_key`: Location where ssh public key used by cephadm will be saved (default: /etc/ceph/cephadm.pub)
    * `cephadm_ssh_private_key`: Location where ssh private key used by cephadm will be saved (default: /etc/ceph/cephadm.id)
  * OSDs
    * `cephadm_osd_devices`: List of /dev/device paths to use (e.g. for multipath devices that can't be used using an OSD spec)
      Example:
      ```
          cephadm_osd_devices:
            - /dev/sdb
            - /dev/sdc
      ```
    * `cephadm_osd_spec`: OSD spec to apply in yaml format
      Example:
      ```
          cephadm_osd_spec:
          service_type: osd
          service_id: osd_spec_default
          placement:
            host_pattern: '*'
          data_devices:
            model: MZ7KH960HAJR0D3
          db_devices:
            model: Dell Express Flash PM1725b 1.6TB SFF
      ```
    
* Registry
    * `cephadm_registry_url`: (default: not used)
    * `cephadm_registry_username`: (default: not used)
    * `cephadm_registry_password`: (default: not used)

* Networking
  * Mandatory
    * `cephadm_public_interface`: Public interface (mandatory)
    * `cephadm_public_network`: Public network including CIDR (mandatory)
  * Optional
    * `cephadm_cluster_interface`: Cluster interface (optional - if not defined ceph will not use dedicated cluster network)
    * `cephadm_cluster_network`: Cluster network including CIDR (optional - if not defined ceph will not use dedicated cluster network)
