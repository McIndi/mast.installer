import os
import openpyxl
from lxml import etree
from mast.cli import Cli
from mast.datapower import datapower
from mast.logging import make_logger
from mast.datapower.datapower import MGMT_NAMESPACE

def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False,
         domains=[],
         out_file="tmp/conformance-validation.xlsx"):
    check_hostname = not no_check_hostname
    env = datapower.Environment(appliances,
                                credentials,
                                timeout=timeout,
                                check_hostname=check_hostname)
    profiles = [
        "dp-wsi-bp.xsl",
        "dp-cfg-bp.xsl",
        "dp-wsi-bsp-1.0.xsl",
    ]
    fields = [
        "domain",
        "profile",
        "severity",
        "type",
        "specification",
        "object-type",
        "object-name",
        "parameter-name",
        "permitted-setting",
        "actual-setting",
        "details"
    ]
    wb = openpyxl.Workbook()
    ws = wb.active
    wb.remove_sheet(ws)
    for appliance in env.appliances:
        ws = wb.create_sheet()
        ws.title = appliance.hostname
        ws.append(fields)
        print((appliance.hostname))
        _domains = domains
        if "all-domains" in domains:
            _domains = appliance.domains
        for domain in _domains:
            print(("\t", domain))
            for profile in profiles:
                print(("\t\t", profile))
                appliance.request.clear()
                req = appliance.request.request
                req.set('domain', domain)
                gcr = etree.SubElement(req, f'{{{MGMT_NAMESPACE}}}get-conformance-report')
                gcr.set('profile', profile)
                resp = appliance.send_request()
                reports = resp.xml.findall(".//Report")
                for report in reports:
                    ws.append([
                        domain,
                        profile,
                        report.get("severity", ""),
                        report.get("type", ""),
                        report.get("specification", ""),
                        report.find('Location').get("object-type", ""),
                        report.find('Location').get("object-name", ""),
                        getattr(report.find('ParameterName'), "text", ""),
                        getattr(report.find('PermittedSetting'), "text", ""),
                        getattr(report.find('ActualSetting'), "text", ""),
                        getattr(report.find('Details'), "text", ""),
                    ])
    wb.save(out_file)

    print("Done")



if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("conformance").exception("An unhandled exception occurred")
        raise
