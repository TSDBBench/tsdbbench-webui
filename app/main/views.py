from flask import render_template, redirect, url_for, session, request, current_app, escape, jsonify
from app.libcloud_utils import *
from app.ssh_utils import *
from app.ssh_benchmark_controller import *
from . import main
import sys
import time
import re
import urllib.request
import lxml.html


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


@main.route('/getbenchmarkconfigs', methods=['GET'])
def getbenchmarkconfigs():
    name = session['username']['provider']
    return jsonify(current_app.config["TSDBBENCH_SETTINGS"]['provider'][name])


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

@main.route('/getnode', methods=['GET'])
def getnode():
    if session.get('username', None)['provider'] == 'Openstack':
        node_id = str(escape(request.args.get('node_id')))
        nodes = get_node_by_id(get_connection_from_session(), node_id)
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

@main.route('/debugSession', methods=['GET'])
def debugSession():
    return jsonify(session["keypair"])

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

                    if result["success"] is True:
                        result["error"] = False;
                        return jsonify(result)
                    else:
                        return jsonify({"error": str(result)})

                except Exception as e:
                    return jsonify({"error": str(e)})
        else:
            return jsonify({"error": "Keypair is not generated. Please, generate a keypair in user's menu"})

    else:
        return jsonify({"error": "User is not logged in. Please log in"})

def generate_new_key_file():
    ts = str(int(time.time()))
    key = session['username']['user'].replace(".", "_") + ts
    directory = os.path.join(current_app.root_path, current_app.config["KEYDIR"])
    result = generate_key_pair(directory, key)
    if result:
        session['keypair'] = {
            "dir": directory,
            "keyName": key
        }
        return True
    else:
        return False

@main.route('/genkeypair', methods=['POST'])
def genkeypair():
    if 'username' in session:
        shouldGenerateNewFile = True
        if 'keypair' in session:
            #check if key file exists
            #generate a new one if it does not
            keyDir = session['keypair']["dir"]
            keyFile = session['keypair']["keyName"]
            keyFilePath = keyDir + '/' + keyFile + "_private.pem"
            if(check_file_exists(keyFilePath)):
                shouldGenerateNewFile = False

        if shouldGenerateNewFile:
            is_new_file_generated = generate_new_key_file()
            return jsonify(is_new_file_generated)
        else:
            return jsonify(True)
    else:
        return jsonify({"error": "User is not logged in. Please log in"})


@main.route('/checkkeypair', methods=['GET'])
def checkkeypair():
    if 'username' in session:
        if 'keypair' in session:
            #check if keypair exists on filesystem
            keyDir = session['keypair']["dir"]
            keyFile = session['keypair']["keyName"]
            keyFilePath = keyDir + '/' + keyFile + "_private.pem"
            if(check_file_exists(keyFilePath)):
                return jsonify(session['keypair']['keyName'])
            else:
                return jsonify(False)
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


@main.route('/terminatenode', methods=['POST', 'DELETE'])
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

@main.route('/benchmark', methods=['GET', 'POST'])
def benchmark():
    if 'username' in session:
        if request.method == 'POST':
            #ajax benchmark execution
            #start the benchmark through ssh
            #benchmark results files will be returned when the process is finished
            result_files = execute_benchmark_process()
            response = jsonify(result_files)
            response.headers.add('Access-Control-Allow-Origin', '*')

            return jsonify(result_files)
        else:
            #render the benchmark view
            return render_template('benchmark.html', benchmarkActive=True)
    else:
        return jsonify({"error": "User is not logged in. Please log in"})

@main.route('/benchmark_progress', methods=['GET', 'POST'])
def benchmark_progress():
    if 'username' in session:
        if request.method == 'POST':
            progress = get_new_benchmark_progress_messages()
            response = jsonify(progress)
            response.headers.add('Access-Control-Allow-Origin', '*')

            return response
        else:
            progress = get_benchmark_progress_messages()
            response = jsonify(progress)
            response.headers.add('Access-Control-Allow-Origin', '*')

            return response
    else:
        return jsonify({"error": "User is not logged in. Please log in"})

@main.route('/getnodefloatingip', methods=['GET'])
def getnodefloatingip():
    if 'username' in session:
        if session.get('username', None)['provider'] == 'Openstack':
            node_id = str(escape(request.args.get('node')))
            conn = get_connection_from_session()
            result = get_floating_ip_by_node_id(conn, node_id)
            return jsonify(str(result))
    else:
        return jsonify({"error": "User is not logged in. Please log in"})


@main.route('/testssh', methods=['POST'])
def testssh():
    if 'username' in session:
        try:
            tsdbbench_settings = current_app.config["TSDBBENCH_SETTINGS"]
            server_ip = str(escape(request.form['server_ip']))
            key = get_private_key_path(session['keypair']['dir'], session['keypair']['keyName'])
            ssh = make_connection(
                server_ip,
                tsdbbench_settings['vm_user'],
                key
            )
            ssh.close()
            return jsonify(True)

        except Exception as e:
            print(e, file=sys.stderr)
            return jsonify(False)

    else:
        return jsonify({"error": "User is not logged in. Please log in"})


@main.route('/sshexecute', methods=['POST'])
def sshexecute():
    if 'username' in session:
        if session.get('username', None)['provider'] == 'Openstack':
            tsdbbench_settings = current_app.config["TSDBBENCH_SETTINGS"]

            # save POSTed data
            server_ip = str(escape(request.form['server_ip']))
            databases = str(escape(request.form['databases']))
            auth_url = str(escape(request.form['auth_url']))
            tenant = str(escape(request.form['tenant']))
            image = str(escape(request.form['image']))
            image_url = str(escape(request.form['image_url']))
            flavor = str(escape(request.form['flavor']))

            # path to private key
            key = get_private_key_path(session['keypair']['dir'], session['keypair']['keyName'])

            # establish SSH connection
            ssh = make_connection(server_ip, tsdbbench_settings['vm_user'], key)

            # edit config files
            change_config_file(ssh, tsdbbench_settings['config_file_path'], auth_url,session['username']['user'], session['username']['p'], tenant, image, image_url)
            change_gen_db_config_files(ssh, tsdbbench_settings['config_file_path_gen'], flavor)
            change_gen_db_config_files(ssh, tsdbbench_settings['config_file_path_db'], flavor)

            # MAIN BENCHMARK EXECUTION BLOCK
            home_folder = tsdbbench_settings['home_folder']
            temp_folder = tsdbbench_settings['temp_folder']
            vagrant_files = tsdbbench_settings['vagrant_files']
            results_folder = tsdbbench_settings['results_folder']

            # execute commands
            prepare_for_benchmark_execution(ssh, home_folder, temp_folder, results_folder)

            # build commands
            main_command = build_benchmark_execution_command(home_folder, temp_folder, vagrant_files, databases, session['username']['provider'])
            copy_results_command = 'cd ' + home_folder + ' && cp ycsb_*.html ' + results_folder

            execute_command(ssh, main_command)
            execute_command(ssh, copy_results_command)

            sftp = ssh.open_sftp()
            benchmark_results = sftp.listdir(results_folder)
            directory = os.path.join(current_app.root_path, 'static', current_app.config["RESULTDIR"])
            check_directory_exists(directory)

            new_files = []

            resulting_html_list = []

            for f in benchmark_results:
                remote_file_path = 'http://' + server_ip + '/TSDBBench/' + f
                print("new files created: " + remote_file_path)
                new_files.append(remote_file_path)

                file = {'name': f, 'contents': '', 'url': ''}

                with urllib.request.urlopen(remote_file_path) as url:
                    file_output = url.read()

                    doc = lxml.html.fromstring(file_output)
                    link = lxml.html.fromstring('<link rel="stylesheet" href="/static/css/iframes_results.css">').find('.//link')
                    head = doc.find('.//head')
                    title = head.find('title')
                    if title == None:
                        where = 0
                    else:
                        where = head.index(title) + 1
                    head.insert(where, link)

                    file_output = lxml.html.tostring(doc)

                    backend_url = directory + '/' + f
                    with open(backend_url, 'wb') as ofile:
                        ofile.write(file_output)

                    static_url = os.path.join('static', current_app.config["RESULTDIR"], f)
                    file['contents'] = file_output.decode('utf-8')
                    file['url'] = static_url
                    file['remote_url'] = remote_file_path
                    resulting_html_list.append(file)

            sftp.close()
            ssh.close()

            # release floating ips
            conn = get_connection_from_session()
            release_unused_floating_ips(conn)

            return jsonify(resulting_html_list)

    else:
        return jsonify({"error": "User is not logged in. Please log in"})


@main.route('/sshdebuglog', methods=['GET'])
def sshdebuglog():
    if 'username' in session:
        if session.get('username', None)['provider'] == 'Openstack':
            try:
                tsdbbench_settings = current_app.config["TSDBBENCH_SETTINGS"]

                # GET server ip
                server_ip = str(escape(request.args.get('server_ip')))

                # path to private key
                key = get_private_key_path(session['keypair']['dir'], session['keypair']['keyName'])

                # establish SSH connection and get all debug_*.log filenames
                ssh = make_connection(server_ip, tsdbbench_settings['vm_user'], key)
                stdin, stdout, stderr = ssh.exec_command(''.join(('find ', tsdbbench_settings['home_folder'], ' -name debug_*.log')))
                file_list_binary = stdout.read().splitlines()
                newest_log_name = None
                ts = 0

                for f in file_list_binary:
                    file_string = f.decode('utf-8')
                    file_ts = int(re.search(r'\d+', file_string).group())
                    if file_ts > ts:
                        ts = file_ts
                        newest_log_name = file_string

                sftp = ssh.open_sftp()

                if newest_log_name != None:
                    remote_file = sftp.open(newest_log_name)
                    file_contents = []
                    try:
                        for line in remote_file:
                            file_contents.append(line.replace('\n', ''))
                    finally:
                        remote_file.close()
                    sftp.close()
                    ssh.close()
                    return jsonify(file_contents)

                else:
                    sftp.close()
                    ssh.close()
                    return jsonify({"error": "There is no log file in the directory"})
            except Exception as e:
                return jsonify({"error": e})
        else:
            return jsonify({"error": "Provider is not yet supported"})
    else:
        return jsonify({"error": "User is not logged in. Please log in"})


@main.route('/sshbenchmarkresults', methods=['GET'])
def sshbenchmarkresults():
    if 'username' in session:
        if session.get('username', None)['provider'] == 'Openstack':
            tsdbbench_settings = current_app.config["TSDBBENCH_SETTINGS"]
            results_folder = tsdbbench_settings['results_folder']

            # GET server ip
            server_ip = str(escape(request.args.get('server_ip')))

            # path to private key
            key = get_private_key_path(session['keypair']['dir'], session['keypair']['keyName'])

            # establish SSH connection and get all debug_*.log filenames
            ssh = make_connection(server_ip, tsdbbench_settings['vm_user'], key)

            stdin, stdout, stderr = ssh.exec_command(
                ''.join(('find ', tsdbbench_settings['home_folder'], ' -name ycsb_*.html')))

            file_list_binary = stdout.read().splitlines()
            result_names = []

            for f in file_list_binary:
                result_names.append(f.decode('utf-8'))

            print(result_names, file = sys.stderr)

            sftp = ssh.open_sftp()



            result_names = sftp.listdir(results_folder)
            results = []
            for r in result_names:
                results.append(''.join(('http://', server_ip, '/TSDBBench/', r)))

            sftp.close()
            ssh.close()

            return jsonify(results)
        else:
            return jsonify({"error": "Provider is not yet supported"})
    else:
        return jsonify({"error": "User is not logged in. Please log in"})


@main.route('/deletebenchmarkresults', methods=['POST', 'DELETE'])
def deletebenchmarkresults():
    if 'username' in session:
        #todo delete all result files in results_to_delete
        results_to_delete = str(escape(request.form['results_to_delete']))
        print(results_to_delete)
        for r in results_to_delete:
            lastIndex = r.rfind("/")
            fileName = r[lastIndex+1:]
            filePath = tsdbbench_settings['results_folder'] + "/" + fileName
            print("file to delete")
            print(filePath)
            # deleteFile(filePath)
        return jsonify(True)
    else:
        return jsonify({"error": "User is not logged in. Please log in"})

@main.route('/downloadbenchmarkresult', methods=['GET'])
def downloadbenchmarkresult():
    if 'username' in session:
        result_to_download = str(escape(request.form['result_to_download']))
        print(result_to_download)
        lastIndex = r.rfind("/")
        fileName = r[lastIndex+1:]
        filePath = tsdbbench_settings['results_folder'] + "/" + fileName
        print("file to download")
        print(filePath)
        # deleteFile(filePath)
        # return send_from_directory(directory=tsdbbench_settings['results_folder'], filename=fileName)
        return jsonify(True)
    else:
        return jsonify({"error": "User is not logged in. Please log in"})