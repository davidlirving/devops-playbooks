# This fabfile is to remote run a Python script in a venv by using
#  existing Ansible config and inventory files.
# Copyright (C) 2024 David L. Irving
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from contextlib import contextmanager as _contextmanager
import ansible.parsing.dataloader
import ansible.inventory.manager
import ansible.vars.manager
import ansible.template
from ansible.errors import AnsibleError
from fabric import Connection


def load_ansible_inventory(inventory_path, variable_files):
    # Initialize data loader
    loader = ansible.parsing.dataloader.DataLoader()

    # Load inventory
    inventory = ansible.inventory.manager.InventoryManager(
            loader=loader, sources=inventory_path)
    variable_manager = ansible.vars.manager.VariableManager(
            loader=loader, inventory=inventory)

    # Load variables from additional variable files if they exist
    for vfile in variable_files:
        variable_data = loader.load_from_file(vfile)
        variable_manager.extra_vars.update(variable_data)

    # Gather all variables in scope
    all_vars = variable_manager.get_vars()
    all_vars['cwd'] = all_vars['playbook_dir'] # TODO - global invoke

    # Load the configuration file as a template
    try:
        config_template = loader.load_from_file('pbconfig.yml')
        templar = ansible.template.Templar(loader=loader, variables=all_vars)
        config_content = templar.template(config_template)
    except AnsibleError as e:
        raise SystemExit(f"Error processing configuration template: {e}")

    # Retrieve hosts
    if 'nonprod' in inventory.groups:
        hosts = inventory.groups['nonprod'].get_hosts()
    else:
        raise ValueError(
                "The specified group 'nonprod'"
                + " does not exist in the inventory.")

    return hosts, config_content


@_contextmanager
def enter_venv(conn, activate_path):
    with conn.prefix('. '+activate_path):
        yield


def run_script_on_hosts(hosts, config):
    for host in hosts:
        logging.debug(f"Config for {host.name}: {config}")
        ansible_hostname = host.vars.get('ansible_host')
        ansible_user = host.vars.get('ansible_user')
        if ansible_hostname is None:
            raise ValueError(f'ansible_host is None for {host}.')
        if ansible_user is None:
            raise ValueError(f'ansible_user is None for {host}.')
        try:
            logging.debug(f"Connecting to {host.name}")
            with Connection(host=ansible_hostname) as conn:
                # this assumes I have sudo access on this machine. TODO
                #   Currently I do not.
                # conn.sudo(command, user=username)
                with conn.cd(config['deployment']['remote']['project_path']):
                    with enter_venv(conn, 'venv/bin/activate'):
                        conn.run(f"python {config['project']['entry_point']}")
        except Exception as e:
            logging.error(f"Failed to connect or execute on {host.name}: {e}")


def main():
    inventory_path = '$HOME/persdoc/hosts.yml'  # TODO - don't hardcode
    config_path = ['pbconfig.yml']  # TODO - don't hardcode
    hosts, config_content = load_ansible_inventory(inventory_path, config_path)
    run_script_on_hosts(hosts, config_content)


if __name__ == "__main__":
    main()
