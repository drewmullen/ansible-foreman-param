#!/usr/bin/python

DOCUMENTATION = '''
---
module: foreman_param
author:  Drew Mullen
short_description: Update a foreman parameter
description:
    - Can CRUD foreman parameters
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
'''

EXAMPLES = '''
    - name: create a parameter
      foreman_param
          fqdn: example.domain.com
          param: i_like
          value: ansible
          foreman_user: foreman_admin
          foreman_pass: <blergh>
'''

from ansible.module_utils.basic import AnsibleModule
import requests
import urllib3

############
# TODO #####
# - use vars from outside play
# - verify_ssl
############

requests = requests.Session()

def main():
    module = AnsibleModule(
        argument_spec=dict(
            fqdn=dict(type='str'),
            state=dict(type='str', choices=['present','absent'], default='present'),
            param=dict(type='str'),
            value=dict(type='str'),
            foreman_user=dict(type='str'),
            foreman_pass=dict(type='str', no_log='true'),
            verify_ssl=dict(type='bool', default='false'),
            foreman_url=dict(type='str')
        ),
        required_if=( [ ('state', 'present', ['param', 'value']) ] ),
        supports_check_mode=True
    )
    # Play parameters
    fqdn = module.params['fqdn']
    state = module.params['state']
    param = module.params['param']
    value = module.params['value']
    verify_ssl = module.params['verify_ssl']
    foreman_user = module.params['foreman_user']
    foreman_pass = module.params['foreman_pass']
    foreman_url = module.params['foreman_url']
    changed = False
    exists = True

    # Set common vars
    ok_codes = [200, 201, 204]
    url = "https://" + foreman_url + "/api/v2/hosts/" + fqdn + "/parameters/"
    headers = {'Content-Type':'application/json', 'Accept':'application/json,version=2'}
    auth = (foreman_user, foreman_pass)

    if not verify_ssl:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        requests.verify = False

    # Verify host exists
    host_check = requests.get("https://" + foreman_url + "/api/v2/hosts/" + fqdn, auth=auth)
    if host_check.status_code == '404':
        module.fail_json(changed=False, msg="Host does not exist in Foreman")
    elif host_check.status_code == '401':
        module.fail_json(changed=False, msg="Foreman login failed")

    # Get current parameter value
    json_response = requests.get(url + param, auth=auth)
    json_response = json_response.json()

    # Perform idempotency checks
    # vars changed, exists are used later to signal if state must be configured
    try:
        current_value = str(json_response['value'])
        parid = str(json_response['id'])
    except KeyError:
        if state == 'present':
            current_value = None
            exists = False
            changed = True
        elif state == 'absent':
            module.exit_json(changed=False)

    # Check if current foreman value matches desired value
    if current_value != value:
        changed = True

    #### PERFORM changes
    # update param
    if changed and exists and state == 'present' and not module.check_mode:
        payload = {'parameter': {'value': value}}
        r = requests.put(url + parid, json=payload, headers=headers)

    # create param
    elif changed and not exists and state == 'present' and not module.check_mode:
        payload = {'parameter': {'name': param, 'value': value}}
        r = requests.post(url, json=payload, headers=headers)

    # delete param
    elif changed and exists and state == 'absent' and not module.check_mode:
        r = requests.delete(url + param, headers=headers)

    # no changes
    else:
        module.exit_json(changed=changed)

    if r.status_code not in ok_codes:
        module.fail_json(changed=False, msg=str(r.status_code) + str(r.text))

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
