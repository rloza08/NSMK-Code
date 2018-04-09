
from flask import Flask, jsonify, render_template, request

import backend as backend
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

global store_group
store_group = None
global fw_l3_version
fw_l3_version = None

global org_group
org_group = None
global fw_s2s_version
fw_s2s_version = None

global org_group_l3
org_group_l3 = None

# INCOMING REQUEST
# ===== L3 Firewall ========
@app.route('/deploy_l3')
def deploy_l3():
    global store_group
    global fw_l3_version
    if store_group is None or fw_l3_version is None or org_group_l3 is None:
        print ("Invalid: {} {}".format(fw_l3_version, store_group, org_group))
        return jsonify("error")
    backend.bulk_deploy_l3(org_group_l3, fw_l3_version, store_group)
    return jsonify("done")


@app.route('/fw_l3_version')
def select_fw_l3_version():
    global fw_l3_version
    version_number = request.args.get('a', 0, type=int)
    firewall_versions = backend.get_firewall_l3_versions()
    fw_l3_version = firewall_versions[version_number]
    print (fw_l3_version)
    return jsonify("done")

@app.route('/fw_l3_store_group')
def select_fw_l3_store_group():
    global store_group
    store_group_number = request.args.get('a', 0, type=int)
    store_groups = backend.get_store_groups()
    store_group = store_groups[store_group_number]
    print (store_group)
    return jsonify("done")

# ===== S2S Firewall ========
@app.route('/deploy_s2s')
def deploy_s2s():
    global org_group
    global fw_s2s_version
    if org_group is None or fw_s2s_version is None:
        print ("Invalid: {} {}".format(org_group, fw_s2s_version))
        return jsonify("error")
    backend.bulk_deploy_s2s(org_group, fw_s2s_version)
    return jsonify("done")

@app.route('/fw_s2s_version')
def select_fw_s2s_version():
    global fw_s2s_version
    version_number = request.args.get('a', 0, type=int)
    firewall_versions = backend.get_firewall_s2s_versions()
    fw_s2s_version = firewall_versions[version_number]
    print (fw_s2s_version)
    return jsonify("done")

@app.route('/fw_l3_org_group')
def select_fw_l3_org_group():
    global org_group_l3
    org_group_number = request.args.get('a', 0, type=int)
    org_groups = backend.get_org_groups()
    print (org_groups[org_group_number])
    org_group_l3 = org_groups[org_group_number]
    print (org_group_l3)
    return jsonify("done")



@app.route('/fw_s2s_org_group')
def select_fw_s2s_org_group():
    global org_group
    org_group_number = request.args.get('a', 0, type=int)
    org_groups = backend.get_org_groups()
    print (org_groups[org_group_number])
    org_group = org_groups[org_group_number]
    print (org_group)
    return jsonify("done")


# OUTGOING HTML
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/deploy_s2s_form')
def deploy_s2s_form():
    global organization
    global fw_s2s_version
    organization = None
    fw_s2s_version = None
    firewall_versions = backend.get_firewall_s2s_versions()
    org_groups = backend.get_org_groups()
    return render_template('deploy_s2s_form.html', versions=firewall_versions, org_groups=org_groups )

@app.route('/deploy_l3_form')
def deploy_l3_form():
    global store_group
    global fw_l3_version
    firewall_versions = backend.get_firewall_l3_versions()
    store_groups = backend.get_store_groups()
    org_groups = backend.get_org_groups()
    return render_template('deploy_l3_form.html', versions=firewall_versions, store_groups=store_groups
                           , org_groups=org_groups)


@app.route('/firewall.log')
def firewall_log():
    cwd = os.getcwd()
    src = "{}/../firewall.log".format(cwd)
    with open(src, "r") as f:
        content = f.read()

    return render_template("firewall_log.html", content=content)

@app.route('/vpn-firewall.log')
def vpn_firewall_log():
    cwd = os.getcwd()
    src = "{}/../vpn_firewall.log".format(cwd)
    with open(src, "r") as f:
        content = f.read()

    return render_template("vpn_firewall_log.html", content=content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

