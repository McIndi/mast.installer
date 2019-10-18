from collections import defaultdict
from mast.datapower import datapower
from mast.logging import make_logger
from mast.cli import Cli
from lxml import etree
import openpyxl
import sqlite3
import pandas as pd


def recurse_config(header_row, hostname=None, domain=None, node=None, status=None, root=None, row=None, seperator="\n", obfuscate_passwords=False):
    if root is None:
        root = ""
        row = [hostname, domain, node.get("name")]
    if not root:
        try:
            object_name, object_class = node.get("name"), node.tag
            _status = status.xpath("//ObjectStatus[Name/text()='{}' and Class/text()='{}']".format(object_name, object_class))[0]
            node.append(_status.find("OpState"))
            node.append(_status.find("EventCode"))
            node.append(_status.find("ErrorCode"))
            node.append(_status.find("ConfigState"))
        except IndexError:
            print("\t\t\tNo Status Available")
    for child in list(node):
        key = root + ".{}".format(child.tag) if root else child.tag
        if not len(child):
            if child.text is None:
                child.text = ""
            if key not in header_row:
                header_row.append(key)
            index = header_row.index(key)

            # Dynamically grow rows as needed
            if index + 1 > len(row):
                _row = [None] * (index - len(row) + 1)
                row.extend(_row)
            # If value, append new value else assign new value
            if row[index]:
                if not isinstance(row[index], list):
                    row[index] = seperator.join((row[index], child.text))
            else:
                row[index] = child.text
            for attr in list(child.keys()):
                if attr.lower() == "class":
                    if isinstance(row[index], list):
                        row[index].append({
                            "name": child.text,
                            "class": child.get(attr),
                            "hostname": hostname,
                            "domain": domain,
                        })
                    else:
                        row[index] = [
                            {
                                "name": child.text,
                                "class": child.get(attr),
                                "hostname": hostname,
                                "domain": domain,
                            }
                        ]
                fieldname = "{}[@{}]".format(key, attr)
                value = child.get(attr).strip() or "N/A"
                if fieldname not in header_row:
                    header_row.append(fieldname)
                index = header_row.index(fieldname)
                if index + 1 > len(row):
                    _row = [None] * (index - len(row) + 1)
                    row.extend(_row)
                row[index] = value
        else:
            recurse_config(header_row, hostname, domain, node=child, status=status, root=key, row=row, seperator=seperator)
    return header_row, row


def append_row(table, hostname, domain, node, status, seperator="\n", obfuscate_passwords=False):
    header_row = table.pop(0)
    header_row, row = recurse_config(header_row, hostname, domain, node, status, seperator=seperator, obfuscate_passwords=obfuscate_passwords)
    table.insert(0, header_row)
    table.append(row)


def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False,
         domains=[],
         object_classes=[],
         persisted=False,
         recursive=False,
         out_file="tmp/get-config.xlsx",
         seperator="\n",
         obfuscate_passwords=False,
         ):
    check_hostname = not no_check_hostname
    env = datapower.Environment(appliances,
                                credentials,
                                timeout=timeout,
                                check_hostname=check_hostname)
    worksheets = defaultdict(lambda: [["appliance", "domain", "name"], ])
    if not object_classes:
        object_classes = [None]
    for appliance in env.appliances:
        print((appliance.hostname))
        _domains = domains
        if "all-domains" in _domains:
            _domains = appliance.domains
        for domain in _domains:
            print(("\t{}".format(domain)))
            for object_class in object_classes:
                config = etree.fromstring(
                    str(
                        appliance.get_config(
                            domain=domain,
                            _class=object_class,
                            recursive=recursive,
                            persisted=persisted
                        )
                    )
                )
                object_status = etree.fromstring(
                    str(
                        appliance.get_status(
                            "ObjectStatus",
                            domain=domain
                        )
                    )
                )
                # First sheet should be ServicesStatusPlus
                services_status = etree.fromstring(
                    str(
                        appliance.get_status(
                            "ServicesStatusPlus",
                            domain=domain
                        )
                    )
                )
                sheet = worksheets["ServicesStatusPlus"]
                sheet[0] = [
                    "appliance",
                    "domain",
                    "ServiceName",
                    "ServiceClass",
                    "LocalIP",
                    "LocalPort",
                    "FshClass",
                    "FshName",
                    "FshStatus",
                    "GatewayStatus",
                    "Summary",
                    "BackendUrl",
                    "BackendHostName",
                    "BackendPort",
                    "FshDirectory",
                    "FshGetQ",
                    "FshTopic",
                    "FshTopicSelection",
                    "FshRemoteServer",
                    "FshRemotePort",
                    "EnableHTTP",
                    "HTTPPort",
                    "EnableHTTPS",
                    "HTTPSPort",
                    "PrimaryInterface",
                    "JunctionType",
                    "JunctionTypeStandard",
                    "JunctionTypeVirtual",
                    "UnresolvedLocalAddress",
                ]
                for node in services_status.findall(datapower.STATUS_XPATH):
                    sheet.append(
                        [
                            appliance.hostname,
                            domain,
                            [
                                {
                                    "hostname": appliance.hostname,
                                    "domain": domain,
                                    "class": node.find("ServiceClass").text,
                                    "name": node.find("ServiceName").text,
                                }
                            ],
                            node.find("ServiceClass").text,
                            node.find("LocalIP").text,
                            node.find("LocalPort").text,
                            node.find("FshClass").text,
                            node.find("FshName").text,
                            node.find("FshStatus").text,
                            node.find("GatewayStatus").text,
                            node.find("Summary").text,
                            node.find("BackendUrl").text,
                            node.find("BackendHostName").text,
                            node.find("BackendPort").text,
                            node.find("FshDirectory").text,
                            node.find("FshGetQ").text,
                            node.find("FshTopic").text,
                            node.find("FshTopicSelection").text,
                            node.find("FshRemoteServer").text,
                            node.find("FshRemotePort").text,
                            node.find("EnableHTTP").text,
                            node.find("HTTPPort").text,
                            node.find("EnableHTTPS").text,
                            node.find("HTTPSPort").text,
                            node.find("PrimaryInterface").text,
                            node.find("JunctionType").text,
                            node.find("JunctionTypeStandard").text,
                            node.find("JunctionTypeVirtual").text,
                            node.find("UnresolvedLocalAddress").text,
                        ]
                    )
                for node in config.findall(datapower.CONFIG_XPATH):
                    object_class = node.tag
                    name = node.get("name")
                    print(("\t\t{} - {}".format(object_class, name)))
                    append_row(worksheets[object_class], appliance.hostname, domain, node, object_status, seperator=seperator, obfuscate_passwords=obfuscate_passwords)
    if out_file.endswith(".xlsx"):
        workbook = openpyxl.Workbook()
        workbook.remove_sheet(workbook.active)
        for title, data in list(worksheets.items()):
            if len(title) > 31:
                title = "...".join((title[:14], title[-14:]))
            worksheet = workbook.create_sheet(title=title)
            for row in data:
                for index, cell in enumerate(list(row)):
                    if isinstance(cell, list):
                        row[index] = seperator.join((item["name"] for item in cell))
                worksheet.append(row)
        workbook.save(out_file)
    elif out_file.endswith(".sqlite"):
        con = sqlite3.connect(out_file)
        for name, data in list(worksheets.items()):
            for row_index, row in enumerate(list(data)):
                for cell_index, cell in enumerate(list(row)):
                    if isinstance(cell, list):
                        data[row_index][cell_index] = seperator.join((item["name"] for item in cell))
            df = pd.DataFrame(data, columns=data.pop(0))
            df.to_sql(
                name=name,
                con=con,
                if_exists="replace",
                index=0
            )
    elif out_file.endswith(".html"):
        html = """<!DOCTYPE html>
        <html>
            <head>
                <meta charset="utf-8" />
                <meta http-equiv="X-UA-Compatible" content="IE=edge" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" />
                <link rel="stylesheet" href="https://cdn.datatables.net/1.10.19/css/jquery.dataTables.min.css" />
            </head>
            <body>
              <style>
                tfoot {
                    display: table-header-group;
                }
              </style>
<!--              <div class="container mx-auto"> -->
                <ul id="tabs" class="nav nav-tabs" role="tablist" style="display: none;">
        """
        for title in sorted(worksheets.keys()):
            html += """<li class="nav-item">
                <a class="nav-link" role="tab" data-toggle="tab" href="#{0}">{0}</a>
            </li>
            """.format(title)
        html += "</ul>"
        html += """<form><select id="tab-select">"""
        for index, title in enumerate(sorted(worksheets.keys())):
            if title == "ServicesStatusPlus":
                html += """<option value="{}" selected="selected">{}</option>""".format(index, title)
            else:
                html += """<option value="{}">{}</option>""".format(index, title)
        html += "</select></form>"
        html += """<div class="tab-content" id="nav-tabContent">"""
        for index, title in enumerate(sorted(worksheets.keys())):
            data = worksheets[title]
            if title == "ServicesStatusPlus":
                html += """<div class="tab-pane fade show active" id="{0}" role="tabpanel"><table class="display table table-striped">""".format(title)
            else:
                html += """<div class="tab-pane fade" id="{0}" role="tabpanel"><table class="display table table-striped">""".format(title)
            header = data.pop(0)
            html += "<thead><tr>"
            for cell in header:
                html += """<th>{}</th>""".format(cell)
            html += "</tr></thead>"
            html += "<tfoot><tr>"
            for cell in header:
                html += """<th></th>"""
            html += "</tr></tfoot><tbody>"
            for row in data:
                if isinstance(row[2], list):
                    html += """<tr id="{}-{}-{}-{}">""".format(
                        row[0].replace(" ", "-"),
                        row[1].replace(" ", "-"),
                        title.replace(" ", "-"),
                        row[2][0]["name"].replace(" ", "-")
                    )
                else:
                    html += """<tr id="{}-{}-{}-{}">""".format(
                        row[0].replace(" ", "-"),
                        row[1].replace(" ", "-"),
                        title.replace(" ", "-"),
                        row[2].replace(" ", "-")
                    )
                for cell in row:
                    if isinstance(cell, list):
                        html += "<td>"
                        for item in cell:
                            link = "#{}-{}-{}-{}".format(
                                item["hostname"].replace(" ", "-"),
                                item["domain"].replace(" ", "-"),
                                item["class"].replace(" ", "-"),
                                item["name"].replace(" ", "-"),
                            )
                            html += """<a href="{}" class="link" data-class="{}" >{}</a><br/>""".format(link, item["class"], item["name"])
                        html += "</td>"
                    else:
                        if cell:
                            html += "<td>{}</td>".format(cell.replace(seperator, "<br />"))
                        else:
                            html += "<td>null</td>"

                if len(row) < len(header):
                    for i in range(len(header)-len(row)):
                        html += "<td>null</td>"
                html += "</tr>"
            html += "</tbody></table></div>"
        html += """
<!--          </div> -->
        </div>
        <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
        <!-- <script src="https://cdnjs.cloudflare.com/ajax/libs/tether/1.4.0/js/tether.min.js"></script> -->
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js"></script>
        <script src="https://cdn.datatables.net/1.10.19/js/jquery.dataTables.min.js"></script>
        <script>
            $(document).ready(function() {
                $('#tab-select').on('change', function (e) {
                    $('#tabs li a').eq($(this).val()).tab('show');
                });
                $(".link").on("click", function(e){
                    e.preventDefault();
                    var objectClass = $(e.target).attr("data-class");
                    $(".nav-tabs a[href='#" + objectClass + "']").one("shown.bs.tab", function(){
                        $($(e.target).attr("href")).css("background-color", "yellow");
                        $($(e.target).attr("href")).get(0).scrollIntoView();
                        $('body, html').scrollLeft(0);
                    });
                    $("#tab-select").val($("option:contains('" + objectClass + "')").filter(function(){return $(this).text() === objectClass}).val());
                    $("#tab-select").trigger( "change" );
                });
                var tables = $('table').DataTable({
                    paging: false
                });
                $.each($('table'), function () {
                    $(this).find('tfoot th').each(function (i) {
                        var currentTable = $(this).closest('table').DataTable();
                        var select = $('<input type="text">')
                            .appendTo($(this))
                            .on('change', function () {
                                var val = $(this).val();

                                console.log(val ? $(this).val() : val)
                                currentTable.column(i)
                                    .search(val ? $(this).val() : val, false, true)
                                    .draw();
                            });

                    });
                })
            } );
        </script>
        </body>
        </html>"""
        with open(out_file, "w") as fp:
            fp.write(html)
    else:
        raise NotImplementedError("Unsopported output type, choose one of ['.xlsx', '.sqlite3', '.html']")

if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("an unhandled exception occurred")
        raise
