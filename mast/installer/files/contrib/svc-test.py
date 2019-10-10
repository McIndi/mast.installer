from mast.logging import make_logger
from mast.datapower import datapower
from mast.cli import Cli
from lxml import etree
import io

log = make_logger("svc-test")

remove_namespaces_xslt = '''<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" indent="no"/>

<xsl:template match="/|comment()|processing-instruction()">
    <xsl:copy>
      <xsl:apply-templates/>
    </xsl:copy>
</xsl:template>

<xsl:template match="*">
    <xsl:element name="{local-name()}">
      <xsl:apply-templates select="@*|node()"/>
    </xsl:element>
</xsl:template>

<xsl:template match="@*">
    <xsl:attribute name="{local-name()}">
      <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:template>
</xsl:stylesheet>
'''
remove_namespaces_xslt = etree.parse(io.BytesIO(str.encode(remove_namespaces_xslt)))
REMOVE_NAMESPACES = etree.XSLT(remove_namespaces_xslt)

def main(
        appliances=[],
        credentials=[],
        domains=[],
        timeout=120,
        no_check_hostname=False,
        test_files=[],
    ):
    """svc-test a utility for testing DataPower configuration and
    status. Tests are determined
    """
    check_hostname = not no_check_hostname
    env = datapower.Environment(appliances,
                                credentials,
                                timeout,
                                check_hostname=check_hostname)
    error_count = 0
    namespace = {}
    for filename in test_files:
        tree = etree.parse(filename)
        for node in tree.xpath("/TestSuite/Import"):
            module = node.get("module")
            name = module.get("as") if node.get("as") else module
            namespace[name] = __import__(module)
        for node in tree.xpath("/TestSuite/*"):
            for appliance in env.appliances:
                _domains = domains
                if "all-domains" in _domains:
                    _domains = appliance.domains
                for domain in _domains:
                    result = None
                    if node.tag == "ConfigTest":
                        config = etree.fromstring(str(appliance.get_config(domain=domain)))
                        config = REMOVE_NAMESPACES(config).getroot()
                        test_name = node.attrib.get("name")
                        for constraint in node.xpath("./Constraint"):
                            xpath = constraint.attrib.get("xpath")
                            trigger = constraint.attrib.get("trigger")
                            matches = config.xpath(xpath)
                            constraint_name = constraint.attrib.get("name")
                            namespace["matches"] = matches
                            # print(namespace)
                            result = eval(trigger, namespace)
                    elif node.tag == "StatusTest":
                        provider = node.attrib.get("provider")
                        status = etree.fromstring(str(appliance.get_status(provider, domain=domain)))
                        status = REMOVE_NAMESPACES(status).getroot()
                        test_name = node.attrib.get("name")
                        for constraint in node.xpath("./Constraint"):
                            xpath = constraint.attrib.get("xpath")
                            trigger = constraint.attrib.get("trigger")
                            matches = status.xpath(xpath)
                            constraint_name = constraint.attrib.get("name")
                            namespace["matches"] = matches
                            result = eval(trigger, namespace)
                    if result:
                        error_count += 1
                        print("FAILURE ")
                        print(("\tTestSuite: '{}'".format(test_name)))
                        print(("\tconstraint: '{}'".format(constraint_name)))
                        print(("\tXpath: '{}'".format(xpath)))
                        print(("\tTrigger: '{}'".format(trigger)))
                        print(("\tAppliance: '{}'".format(appliance.hostname)))
                        print(("\tDomain: '{}'".format(domain)))
                        try:
                            print(("\tMatches:\n\t\t'{}'".format("\n\t\t".join([etree.tostring(match, pretty_print=True).strip() for match in matches]))))
                        except:
                            print(("\tMatches:\n\t'{}'".format("\n\t\t".join([str(match).strip() for match in matches]))))
                        print(("\tresult: '{}'".format(result)))
    print(("Total Number of Failures: '{}'".format(error_count)))


if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        log.exception("Sorry, an unhandled exception occurred.")
        raise
