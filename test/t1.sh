#!/bin/bash
echo "l3fwrules test"
select l3fwrules-org org-Firewall_Testing_Org
select l3fwrules-store-list store-list-TST_1234
select l3fwrules-version l3fwrules_template_MAY_MX_Org_050418-v6a
get settings l3fwrules
deploy l3fwrules
echo "--------------------------------------------------"

