
destinations = {
    'visualizer': {
        'description': 'The visualizer component of the UI',
        'ip-address': '0.0.0.0',
        'protocol': 'scp',
        'authentication': {
            'key-based': {
                'username': 'root'
            }
        }
    },
    'test_machine': {
        'description': 'Test destination for behave tests',
        'ip-address': '127.0.0.1',
        'protocol': 'scp',
        'authentication': {
            'key-based': {
                'username': None
            }
        }
    },
    'test_machine_bad': {
        'description': 'Invalid test destination for behave tests',
        'ip-address': '0.0.0.0',
        'protocol': 'scp',
        'authentication': {
            'key-based': {
                'username': 'root'
            }
        }
    }
}
