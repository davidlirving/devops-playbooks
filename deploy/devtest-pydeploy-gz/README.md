# devtest-pydeploy-gz
This playbook is for quickly checking Python code for errors using Flake8 and mypy, deploying it and then running it on a remote host. This particular version creates a gzip artefact and pushes it to the remote host. It will use the venv Python module to manage the Python virtual environment using your project's `requirements.txt`.

This is playbook is better suited for dev/testing environments and is not recommended for production environments.

## Why gzip?
Sometimes I prefer not to have to commit every single change that I want to explore or test which is usually due to the CICD environment creating too much overhead (or is just simply broken at the time).

## Why remote host?
I often do not have all the infrastructure needed on my local machine, nor access to it, and need it to run on a remote host that does.

## How to use
Download the playbook and put it somewhere. You should be able to call the playbook with your own hosts file such as:
```yaml
nonprod:
  hosts:
    deploy_target:
      ansible_host: mynonprodserver
      ansible_user: ec2-user
      ansible_become: true
      ansible_become_method: sudo
      ansible_become_user: yourusername
```
Go to the project directory that want to deploy and create `pbconfig.yml`. See the provided one for more information.

Once configured, run `ansible-playbook -i /path/to/hosts.yml /path/to/devtest-pydeploy-gz.yml`.

It is intentional that you can have one playbook globally available and work with a project specific `pbconfig.yml`.
