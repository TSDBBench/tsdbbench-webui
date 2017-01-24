from flask import render_template, redirect, url_for, session, request, current_app, escape, jsonify
from app.libcloud_utils import *
from app.ssh_utils import *
from . import main
import sys
import time


def get_connection_from_session():
    auth = session.get('username', None)
    driver = get_openstack_connection(
        auth['user'],
        auth['p'],
        auth['host'],
        auth['project'],
        auth['region'],
    )
    return driver['connection']


@main.route('/index', methods=['GET', 'POST'])
@main.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:

        return render_template('index.html', rootActive=True)

    else:

        if request.method == 'POST':
            provider = str(escape(request.form['provider']))

            if provider == 'Openstack':

                user = str(escape(request.form['user']))
                pwd = str(escape(request.form['pwd']))
                host = str(escape(request.form['host']))
                project = str(escape(request.form['project']))
                region = str(escape(request.form['region']))

                result = get_openstack_connection(user, pwd, host, project, region)

                # print(result['connection'], file=sys.stderr)

                if 'exception' not in result:
                    session['username'] = {
                        'provider': provider,
                        'user': user,
                        'p': pwd,
                        'host': host,
                        'project': project,
                        'region': region

                    }

                    print("=== " + user + " logged in ===", file=sys.stderr)
                    return redirect(url_for('.index'))
                else:
                    return render_template(
                        'login.html',
                        exception=result['exception'],
                        exceptionType=result['exceptionType']
                    )

        if request.method == 'GET':

            return render_template('login.html')


@main.route('/logout', methods=['GET'])
def logout():
    if 'keypair' in session:
        key_name = session['keypair']['keyName']
        key_dir = session['keypair']['dir']
        conn = get_connection_from_session()
        if key_remove_is_allowed(conn, key_name):
            delete_key_pair(conn, key_name)
            delete_key_pair_files(key_dir, key_name)
            session.pop('keypair', None)

    print("=== " + session['username']['user'] + " logged out ===", file=sys.stderr)
    session.pop('username', None)
    return redirect(url_for('.index'))


@main.route('/getimages', methods=['GET'])
def getimages():
    if session.get('username', None)['provider'] == 'Openstack':
        images = get_openstack_image_catalog(get_connection_from_session())
        return jsonify(images)
    else:
        return jsonify(None)


@main.route('/getprovidersettings', methods=['GET'])
def getprovidersettings():
    return jsonify(current_app.config["PROVIDERS"])


@main.route('/getdatabases', methods=['GET'])
def getdatabases():
    return jsonify(current_app.config["TSDBBENCH_SETTINGS"]['supported_databases'])


@main.route('/getflavors', methods=['GET'])
def getflavors():
    if session.get('username', None)['provider'] == 'Openstack':
        flavors = get_openstack_flavor_catalog(get_connection_from_session())
        return jsonify(flavors)
    else:
        return jsonify(None)


@main.route('/getnodes', methods=['GET'])
def getnodes():
    if session.get('username', None)['provider'] == 'Openstack':
        nodes = get_openstack_node_catalog(get_connection_from_session())
        return jsonify(nodes)
    else:
        return jsonify(None)


@main.route('/getsecuritygroups', methods=['GET'])
def getsecuritygroups():
    if session.get('username', None)['provider'] == 'Openstack':
        sgroups = get_openstack_security_group_list(get_connection_from_session())
        return jsonify(sgroups)
    else:
        return jsonify(None)


@main.route('/getfloatingips', methods=['GET'])
def getfloatingips():
    if session.get('username', None)['provider'] == 'Openstack':
        floating_ips = get_floating_ips_catalog(get_connection_from_session())
        if len(floating_ips) > 0:
            return jsonify(floating_ips)
        else:
            return jsonify({'error': 'No floating IPs, delete unused and allocate a new one'})
    else:
        return jsonify(None)


@main.route('/allocatefloatingip', methods=['POST'])
def allocatefloatingip():
    if session.get('username', None)['provider'] == 'Openstack':
        return jsonify(allocate_floating_ip(get_connection_from_session()))
    else:
        return jsonify(None)


@main.route('/instances', methods=['GET'])
def instances():
    if 'username' in session:
        return render_template('instances.html', createNodeActive=True)
    else:
        return redirect(url_for('.index'))


@main.route('/createnode', methods=['POST'])
def createnode():
    if 'username' in session:
        if 'keypair' in session:
            if session.get('username', None)['provider'] == 'Openstack':
                try:
                    conn = get_connection_from_session()
                    instance_name = str(escape(request.form['instanceName']))
                    image = str(escape(request.form['image']))
                    flavor = str(escape(request.form['flavor']))
                    sgroup = str(escape(request.form['sgroup']))

                    key_name = session['keypair']['keyName']
                    key_path = session['keypair']['dir']

                    import_key_pair(conn, key_name, get_public_key_path(key_path, key_name))

                    result = instantiate_node(
                        conn,
                        instance_name,
                        image,
                        flavor,
                        key_name,
                        sgroup
                    )

                    if result is True:
                        return jsonify(True)
                    else:
                        return jsonify({"error": str(result)})

                except Exception as e:
                    return jsonify({"error": str(e)})
        else:
            return jsonify({"error": "Keypair is not generated. Please, generate a keypair in user's menu"})

    else:
        return jsonify({"error": "User is not logged in. Please log in"})


@main.route('/genkeypair', methods=['POST'])
def genkeypair():
    if 'username' in session:
        if 'keypair' in session:
            return jsonify(True)
        else:
            ts = str(int(time.time()))
            key = session['username']['user'].replace(".", "_") + ts
            directory = os.path.join(current_app.root_path, current_app.config["KEYDIR"])
            result = generate_key_pair(directory, key)
            if result:
                session['keypair'] = {
                    "dir": directory,
                    "keyName": key
                }
                return jsonify(True)
            else:
                return jsonify(False)
    else:
        return jsonify({"error": "User is not logged in. Please log in"})


@main.route('/checkkeypair', methods=['GET'])
def checkkeypair():
    if 'username' in session:
        if 'keypair' in session:
            return jsonify(True)
        else:
            return jsonify(False)
    else:
        return jsonify({"error": "User is not logged in. Please log in"})


@main.route('/rebootnode', methods=['POST'])
def rebootnode():
    if 'username' in session:
        if session.get('username', None)['provider'] == 'Openstack':
            node_id = str(escape(request.form['instance']))
            conn = get_connection_from_session()
            if reboot_instance(conn, node_id):
                return jsonify(True)
            else:
                return jsonify(False)
    else:
        return jsonify({"error": "User is not logged in. Please log in"})


@main.route('/stopnode', methods=['POST'])
def stopnode():
    if 'username' in session:
        if session.get('username', None)['provider'] == 'Openstack':
            node_id = str(escape(request.form['instance']))
            conn = get_connection_from_session()
            if stop_instance(conn, node_id):
                return jsonify(True)
            else:
                return jsonify(False)
    else:
        return jsonify({"error": "User is not logged in. Please log in"})


@main.route('/startnode', methods=['POST'])
def startnode():
    if 'username' in session:
        if session.get('username', None)['provider'] == 'Openstack':
            node_id = str(escape(request.form['instance']))
            conn = get_connection_from_session()
            if start_instance(conn, node_id):
                return jsonify(True)
            else:
                return jsonify(False)
    else:
        return jsonify({"error": "User is not logged in. Please log in"})


@main.route('/terminatenode', methods=['POST'])
def terminatenode():
    if 'username' in session:
        if session.get('username', None)['provider'] == 'Openstack':
            node = str(escape(request.form['instance']))
            conn = get_connection_from_session()
            terminate_instance(conn, node)
            return jsonify(True)
    else:
        return jsonify({"error": "User is not logged in. Please log in"})


@main.route('/attachfloatingip', methods=['POST'])
def attachfloatingip():
    if 'username' in session:
        if session.get('username', None)['provider'] == 'Openstack':
            node = str(escape(request.form['instance']))
            floating_ip = str(escape(request.form['floating_ip']))
            conn = get_connection_from_session()
            result = attach_floating_ip(conn, floating_ip, node)
            return jsonify(str(result))
    else:
        return jsonify({"error": "User is not logged in. Please log in"})


@main.route('/releasefloatingips', methods=['POST'])
def releasefloatingips():
    if 'username' in session:
        if session.get('username', None)['provider'] == 'Openstack':
            conn = get_connection_from_session()
            result = release_unused_floating_ips(conn)
            return jsonify(str(result))
    else:
        return jsonify({"error": "User is not logged in. Please log in"})


@main.route('/ssh', methods=['GET'])
def ssh():
    if 'username' in session:
        return render_template('ssh.html', sshActive=True)
    else:
        return jsonify({"error": "User is not logged in. Please log in"})
