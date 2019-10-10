import json
import urllib3
import requests
from mast.cli import Cli
from mast.logging import make_logger
from mast.datapower import datapower

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main(
    appliances=[],
    credentials=[],
    timeout=3.0,
    no_check_hostname=False,
    domains=[],
    providers=[],
):
    logger = make_logger(__name__)
    check_hostname = not no_check_hostname
    env = datapower.Environment(
        appliances,
        credentials,
        timeout,
        check_hostname=check_hostname
    )
    for appliance in env.appliances:
        rest_url = "https://{}:{}".format(appliance._hostname, 5551)
        appliance.session = requests.Session()
        _domains = domains # Can we support glob and/or regex?
        if "all-domains" in _domains:
            _url = "{}/mgmt/domains/config/".format(rest_url)
            username, password = appliance.credentials.split(":", 1)
            try:
                domains_config = appliance.session.get(_url, verify=check_hostname, auth=(username, password), timeout=timeout).json()
            except requests.exceptions.ConnectionError:
                continue
            _domains = [d["name"] for d in domains_config["domain"]]
        if "app-domains" in _domains:
            _url = "{}/mgmt/domains/config/".format(rest_url)
            username, password = appliance.credentials.split(":", 1)
            try:
                domains_config = appliance.session.get(_url, verify=check_hostname, auth=(username, password), timeout=timeout).json()
            except requests.exceptions.ConnectionError:
                continue
            _domains = [d["name"] for d in domains_config["domain"] if d["name"] != "default"]

        for domain in _domains:
            for provider in providers:
                rest_uri = "/mgmt/status/{}/{}".format(domain, provider)
                _url = "{}{}".format(rest_url, rest_uri)
                username, password = appliance.credentials.split(":", 1)
                try:
                    status = appliance.session.get(_url, verify=check_hostname, auth=(username, password)).json()[provider]
                except KeyError:
                    print(("*** Error occured when calling {} ***".format(_url)))
                    continue
                if isinstance(status, list):
                    for _status in status:
                        _status.update(hostname=appliance.hostname, domain=domain, provider=provider, uri=rest_uri)
                        print((json.dumps(_status)))
                else:
                    status.update(hostname=appliance.hostname, domain=domain, provider=provider, uri=rest_uri)
                    print((json.dumps(status)))


if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("An unhandled exception occurred.")
        raise
