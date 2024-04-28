# ansible-fabric-pyrun
This is a Fabric script that leverages Ansible config and hosts inventory files (to prevent duplication of configs) and can be used in tandem with Ansible.

The main reason I wrote this is that I wanted to see stdout without having to manually ssh into a host. Alternatively you could tail a log file from an execution parse of Ansible, or feed logs into something like Splunk or OpenSearch.

## How to use
TODO
Currently you need to copy the fabfile to your project directory. I have a little bit more work to do on improving it so it can be invoked globally instead.
