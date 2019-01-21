# module: foreman_param

author:  Drew Mullen

short_description: Update a foreman parameter

description:
    - Can CRUD foreman parameters

```
options:
    fqdn:
        description:
            - FQDN of host with param to manage.
    state:
        description:
            - Should param exist or not.
        default: present
        choices: ['present', 'absent']
    param:
        description:
            - Name of parameter.
    value:
        description:
            - Desired value of parameter.
    foreman_user:
        description:
            - login username.
    foreman_pass:
        description:
            - login password.
    foreman_url:
        description:
            - foreman domain
        default: foreman.domain.com
    verify_ssl:
        description:
            - Not working. placeholder for TODO
        default: false
        choices: ['true', 'false']
```
