# gicore
import gicore.discovery
import gicore.filetransfer
import gicore.models

import config

# internal
try:
    import json
except ImportError:
    import simplejson as json

def install(desired_state):
    server = config.get("gi/DISCOVERY_SERVER")
    pub_key = config.get("gi/PUBLIC_KEY")
    timeout = config.get("gi/TIMEOUT")
    all_packages_max_size = config.get("gi/ALL_PACKAGES_MAX_SIZE")
    all_packages_raw = get_file(server, gicore.discovery.ALL_PACKAGES_PATH,
        pub_key, timeout, all_packages_max_size)
    all_packages_dict = json.loads(encoding = "ascii")
    all_packages = gicore.models.AllPackages.from_dict(all_packages_dict)
    all_packages.validate()
