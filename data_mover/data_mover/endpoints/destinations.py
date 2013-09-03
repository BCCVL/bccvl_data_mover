from collections import defaultdict

nectar_hpc = defaultdict(dict)
nectar_hpc = {'name': 'NECTAR_BCCVL1',
              'ip_address': '115.146.85.28',
              'protocol': 'scp',
              'authentication':
                  {'basic_authentication':
                       {'username': 'researcher', 'password': 'pa$$w0rd'},
                   'ssh_key':
                       {'key': '123h4wj12kj23141234kj134jkh123jk4h12k3h8wusa8xc7x98h3kjr'}
                  }
}

# Example calls:
# nectar_hpc['name']
# nectar_hpc[authentication']['basic_authentication']