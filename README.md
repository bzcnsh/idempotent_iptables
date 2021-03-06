Role Name
=========

Apply iptables rules idempotently

Requirements
------------

python 2 or python 3, iptables, iptables-save

Role Variables
--------------
  
**idempotent_iptables_quiet**:  
>  false(default): display commands issued  
>  true:  display nothing  

**idempotent_iptables_rules_file**:  
>  file contains rules to be added  
>  format should match output from iptables-save utility  
>  default: iptables.rules  

**idempotent_iptables_duplicate**:  
>  true(default): allow duplicate rules  
>  false: raise exception when duplicate rules are detected  

**idempotent_iptables_success_nochange**:  
>  true(default): nothing to change, because all rules are already in place, is considered success  
>  false: nothing to change is considered faulure  

Dependencies
------------

None

Example Playbook
----------------

    - hosts: public_servers
      roles:
         - { role: idempotent_iptables, idempotent_iptables_rules_file: iptables.rules}

License
-------

MIT

Author Information
------------------

Yimin Zheng. bzcnsh at yahoo.com 
