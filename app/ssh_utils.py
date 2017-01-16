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
        return e


def check_directory_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


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
        print("connecting")
        ssh.connect(hostname=server_ip_address, username=user_name, pkey=k)
        print("connected")
        return ssh
    except Exception as exception:
        e = sys.exc_info()[0]
        print("Exception: " + str(exception))
        print(e)
        return False


def check_connection(ssh):
    try:
        transport = ssh.get_transport()
        transport.send_ignore()
    except EOFError as exception:
        e = sys.exc_info()[0]
        print("Exception: " + str(exception))
        print(e)
        return False
