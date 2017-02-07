from flask import render_template, redirect, url_for, session, request, current_app, escape, jsonify
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import os
import errno
import paramiko
import time
import sys


def generate_key_pair(directory, key_name):
    try:
        # generate private/public key pair
        key = rsa.generate_private_key(
            backend=default_backend(),
            public_exponent=65537,
            key_size=2048
        )
        # get public key in OpenSSH format
        public_key = key.public_key()\
            .public_bytes(serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH)
        # get private key in PEM container format
        pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        # decode to printable strings
        private_key_str = pem.decode('utf-8')
        public_key_str = public_key.decode('utf-8')

        check_directory_exists(directory)

        private_key = directory + '/' + key_name + "_private.pem"
        public_key = directory + '/' + key_name + "_public.pub"

        with open(private_key, "w") as text_file:
            print(private_key_str, file=text_file)
        os.chmod(private_key, 0o600)

        with open(public_key, "w") as text_file2:
            print(public_key_str, file=text_file2)
        os.chmod(public_key, 0o600)
        return True
    except Exception as e:
        print("Exception in generate_key_pair")
        print(e)
        return e


def check_directory_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def check_file_exists(file_path):
    exists = os.path.exists(file_path)
    return exists

def delete_key_pair_files(directory, key_name):
    try:
        check_directory_exists(directory)
        private_key = directory + '/' + key_name + "_private.pem"
        public_key = directory + '/' + key_name + "_public.pub"
        delete_file(private_key)
        delete_file(public_key)
        return True
    except Exception as e:
        return e


def delete_file(path):
    try:
        os.remove(path)
        return True
    except Exception as e:
        return e


def get_public_key_path(directory, key_name):
    return directory + '/' + key_name + "_public.pub"


def get_private_key_path(directory, key_name):
    return directory + '/' + key_name + "_private.pem"


def make_connection(server_ip_address, user_name, key_file):
    try:
        k = paramiko.RSAKey.from_private_key_file(key_file)

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=server_ip_address, username=user_name, pkey=k)
        return ssh
    except Exception as exception:
        e = sys.exc_info()[0]
        print("Exception: " + str(exception))
        print(e)
        return False
    except Exception as e:
        print(e)


def change_config_file(ssh, config_file_path, auth_url, username, password, tenant, image, image_url):
    try:
        ftp = ssh.open_sftp()
        f = ftp.open(config_file_path, "r")
        lines = f.readlines()
        f.close()
        f2 = ftp.open(config_file_path, "w")
        for line in lines:
            if 'openstack.openstack_auth_url' in line:
                f2.write("    openstack.openstack_auth_url ='" + auth_url + "'\n")
            elif 'openstack.username' in line:
                f2.write("    openstack.username='" + username + "'\n")
            elif 'openstack.password' in line:
                f2.write("    openstack.password ='" + password + "'\n")
            elif 'openstack.tenant_name' in line:
                f2.write("    openstack.tenant_name ='" + tenant + "'\n")
            elif 'openstack.image' in line:
                f2.write("    openstack.image ='" + image + "'\n")
            elif 'openstack.openstack_image_url' in line:
                f2.write("    openstack.openstack_image_url ='" + image_url + "'\n")
            else:
                f2.write(line)
        f2.close()
        print("done")
        return True
    except Exception as e:
        print(e)


def change_gen_db_config_files(ssh, config_file_path, flavor):
    ftp = ssh.open_sftp()
    f = ftp.open(config_file_path, "r")
    lines = f.readlines()
    f.close()
    f2 = ftp.open(config_file_path, "w")
    for line in lines:
        if 'openstack.flavor' in line:
            f2.write("    openstack.flavor ='" + flavor + "'\n")
        else:
            f2.write(line)
    f2.close()
    print("done")
    return


def execute_command(ssh, command):
    try:
        sleeptime = 0.1
        outdata, errdata = '', ''
        ssh_transp = ssh.get_transport()
        ssh_transp.window_size = 3 * 1024 * 1024

        chan = ssh_transp.open_session()
        # chan.settimeout(3 * 60 * 60)
        chan.get_pty()
        chan.setblocking(0)
        chan.exec_command(command)
        while True:  # monitoring process
            # Reading from output streams
            while chan.recv_ready():
                output = str(chan.recv(1000))
                print(output)
            while chan.recv_stderr_ready():
                errdata += str(chan.recv_stderr(1000))
            if chan.exit_status_ready():  # If completed
                break
            time.sleep(sleeptime)
        # retcode = chan.recv_exit_status()
        # ssh_transp.close()

        # print(str(outdata))
        if errdata:
            print(str(errdata))
        return True
    except Exception as e:
        exc = sys.exc_info()
        print(exc)
        print(e)
        return False


def prepare_for_benchmark_execution(ssh_session, home_folder, temp_folder, results_folder):
    try:
        # clean temp folder
        command_kill = "pkill -f python2"
        mkdir = "mkdir -p " + temp_folder
        clean_temp = "rm -rf " + temp_folder + "{*,.*}"
        clean_results = 'find ' + home_folder + ' -type f -name "ycsb_*" -delete'
        clean_logs = 'find ' + home_folder + ' -type f -name "*.log" -delete'
        clean_results_folder = 'find ' + results_folder + ' -type f -name "ycsb_*" -delete'

        print("Kill benchmark execution ")
        execute_command(ssh_session, command_kill)
        print("Create tmp if not exists")
        execute_command(ssh_session, mkdir)
        print("Clean tmp")
        execute_command(ssh_session, clean_temp)
        print("Clean old result files")
        execute_command(ssh_session, clean_results)
        print("Clean old .log files")
        execute_command(ssh_session, clean_logs)
        print("Clean old result files in result folder")
        execute_command(ssh_session, clean_results_folder)

        return True

    except Exception as e:
        print(e)
        return False

def check_connection(ssh):
    try:
        transport = ssh.get_transport()
        transport.send_ignore()
        return True
    except EOFError as exception:
        e = sys.exc_info()[0]
        print("Exception: " + str(exception))
        print(e)
        return False

def build_benchmark_execution_command(home_folder, temp_folder, vagrant_files, databases, provider):
    result = "cd " + home_folder + " && ./TSDBBench.py -t " + temp_folder + " -f " + vagrant_files + " -d " + databases + " -w testworkloada -l --provider " + provider.lower() + " -m"
    return result

