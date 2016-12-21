Role Name
=========

Apply iptables rules idempotently

Requirements
------------

python 2 or python 3, iptables-save

Role Variables
--------------

idempotent_iptables_rules_file: File contains rules to be added. Rules must be saved in file format matching output from iptables-save utility.
idempotent_iptables_quiet:  
   false(default): display commands issued  
   true:  display nothing  
idempotent_iptables_duplicate:  
   true: allow duplicate rules  
   false(default): raise exception when duplicate rules are detected  
idempotent_iptables_success_nochange:  
   true(default): no need to change is considered success  
   false: no need to change is considered faulure  

Dependencies
------------

None

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: idempotent_iptables, idempotent_iptables_rules_file: iptables.rules}

License
-------

MIT

Author Information
------------------

Yimin Zheng. bzcnsh at yahoo.com
