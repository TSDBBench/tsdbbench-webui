import paramiko
import time
import sys
import os
from flask import session
from app.ssh_utils import *

# def make_connection(server,user,key_file):
#     try:
#         k = paramiko.RSAKey.from_private_key_file(key_file)

#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         print ("connecting")
#         ssh.connect( hostname = server, username = user, pkey = k )
#         print ("connected")
#         return ssh
#     except Exception as exception:
#         e = sys.exc_info()[0]
#         print ("Exception: " + str(exception))
#         print(e)
#         return False

# def change_config_file(ssh, auth_url, username, password, tenant, image, image_url):
#     ftp = ssh.open_sftp()
#     f = ftp.open("/home/vagrant/TSDBBench/vagrant_files/vagrantconf.rb", "r")
#     lines=f.readlines()
#     f.close()
#     f2 = ftp.open("/home/vagrant/TSDBBench/vagrant_files/vagrantconf.rb", "w")
#     for line in lines:
#         if 'openstack.openstack_auth_url' in line :
#             f2.write( "    openstack.openstack_auth_url ='"+ auth_url + "'\n")
#         elif 'openstack.username' in line:
#             f2.write( "    openstack.username='" + username + "'\n")
#         elif 'openstack.password' in line :
#             f2.write( "    openstack.password ='"+ password + "'\n")
#         elif 'openstack.tenant_name' in line :
#             f2.write( "    openstack.tenant_name ='"+ tenant + "'\n")
#         elif 'openstack.image' in line :
#             f2.write( "    openstack.image ='"+ image + "'\n")
#         elif 'openstack.openstack_image_url' in line :
#             f2.write( "    openstack.openstack_image_url ='"+ image_url + "'\n")
#         else:
#             f2.write(line) 
#     f2.close()
#     print ("done")
#     return

# def change_gen_config_files(ssh, flavor):
#     ftp = ssh.open_sftp()
#     f = ftp.open("/home/vagrant/TSDBBench/vagrant_files/vagrantconf_gen.rb", "r")
#     lines=f.readlines()
#     f.close()
#     f2 = ftp.open("/home/vagrant/TSDBBench/vagrant_files/vagrantconf_gen.rb", "w")
#     for line in lines:
#         if 'openstack.flavor' in line :
#             f2.write( "    openstack.flavor ='"+ flavor + "'\n")
#         else:
#             f2.write(line) 
#     f2.close()
#     print ("done")
#     return

# def change_db_config_files(ssh, flavor):
#     ftp = ssh.open_sftp()
#     f = ftp.open("/home/vagrant/TSDBBench/vagrant_files/vagrantconf_db.rb", "r")
#     lines=f.readlines()
#     f.close()
#     f2 = ftp.open("/home/vagrant/TSDBBench/vagrant_files/vagrantconf_db.rb", "w")
#     for line in lines:
#         if 'openstack.flavor' in line :
#             f2.write( "    openstack.flavor ='"+ flavor + "'\n")
#         else:
#             f2.write(line) 
#     f2.close()
#     print ("done")
#     return

# def execute_command(ssh,command):
#     try:
#         sleeptime = 0.1
#         outdata, errdata = '', ''
#         ssh_transp = ssh.get_transport()
#         chan = ssh_transp.open_session()
#         #chan.settimeout(3 * 60 * 60)
#         chan.get_pty()
#         chan.setblocking(0)
#         chan.exec_command(command)
#         while True:  # monitoring process
#             # Reading from output streams
#             while chan.recv_ready():
#                 output = str(chan.recv(1000))
#                 session["benchmark_progress_messages"].append(output)
#                 print(output) 
#             while chan.recv_stderr_ready():
#                 errdata += str(chan.recv_stderr(1000))
#             if chan.exit_status_ready():  # If completed
#                 break
#             time.sleep(sleeptime)
#         retcode = chan.recv_exit_status()
#         #ssh_transp.close()

#         #print(str(outdata))
#         print(str(errdata))
#         print("done")
#     except:
#         e = sys.exc_info()
#         print (e)
#     return

# def clean_tmp_folder(ssh_session):
#     print ("Cleaning tmp folder")
#     # clean_command_1 = "cd /home/vagrant/tmp"
#     # clean_command_2 = "rm -rf generator_0/"
#     # clean_command_3 = "rm -rf mysql_cl1_rf1_0/"

#     command_kill='pkill -f python2'
#     command_d='rm -rf /home/vagrant/tmp/{*,.*}'

#     execute_command(ssh_session,command_kill)
#     execute_command(ssh_session,command_d)

#     # execute_command(ssh_session,clean_command_1)
#     # execute_command(ssh_session,clean_command_2)
#     # execute_command(ssh_session,clean_command_3)

#     return

# #returns accumulated progress messages
# #deletes all progress messages so that new ones can be stored
# def get_new_benchmark_progress_messages():
#     new_benchmark_progress_messages = []
#     if 'benchmark_progress_messages' in session:
#         new_benchmark_progress_messages = session["benchmark_progress_messages"]
#     session["benchmark_progress_messages"] = []
#     return new_benchmark_progress_messages

# #returns accumulated progress messages
# def get_benchmark_progress_messages():
#     benchmark_progress_messages = []
#     if 'benchmark_progress_messages' in session:
#         benchmark_progress_messages = session["benchmark_progress_messages"]
#     else:
#         session["benchmark_progress_messages"] = []
#     return benchmark_progress_messages

# def execute_benchmark_process():
#     benchmark_progress_messages = []
#     session["benchmark_progress_messages"] = benchmark_progress_messages
#     command_1='cd /home/vagrant/TSDBBench && ./TSDBBench.py -t /home/vagrant/tmp -f /home/vagrant/TSDBBench/vagrant_files/ /home/vagrant/TSDBBench/vagrant_files/ -d mysql_cl1_rf1 postgresql_cl1_rf1 -w testworkloada -l --provider openstack -m'
#     command_2='cd /home/vagrant/TSDBBench && cp ycsb_*_cl1_rf1_testworkloada_*.html ycsb_combined_*.html /var/www/html/TSDBBench/'
#     command_3='ls -a /var/www/html/TSDBBench/'
#     command_4="cd /home/vagrant/TSDBBench && ./TSDBBench.py -t /home/vagrant/tmp -f /home/vagrant/TSDBBench/vagrant_files -d mysql_cl1_rf1 postgresql_cl1_rf1 -w testworkloada -l --provider openstack -m"

#     VM_IP="192.168.209.154"
#     APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
#     ssh_session=make_connection(VM_IP, "vagrant", os.path.join(APP_ROOT, "mohamad_hadi_diab1485036117_private.pem") )

#     change_config_file(
#         ssh_session,
#         'http://129.69.209.131:5000/v2.0/tokens',
#         'mohamad.hadi.diab',
#         'whxgfm78x3x43x34',
#         'pc-webui-tsdbbench', 
#         'TSDBBench Control-VM (Debian Jessie 8.6)', 
#         'http://129.69.209.131:8776/v2/154db9c9c56e44bc8afcd423d1cbc13e'
#     )

#     change_gen_config_files(ssh_session, 'm1.larger')
#     change_db_config_files(ssh_session, 'm1.larger')
#     ftp = ssh_session.open_sftp()
#     list_of_files_before=ftp.listdir('/var/www/html/TSDBBench')

#     clean_tmp_folder(ssh_session)
#     execute_command(ssh_session,command_4)
#     execute_command(ssh_session,command_2)
#     execute_command(ssh_session,command_3)

#     list_of_files_after=ftp.listdir('/var/www/html/TSDBBench')

#     new_files=[]
#     for f in list_of_files_after:
#         if f not in list_of_files_before:
#             print ("new files created:")
#             print (f)
#             new_files.append(f)

#     ssh_session.close()

#     #release floating ips
#     # if session.get('username', None)['provider'] == 'Openstack':
#     #     conn = get_connection_from_session()
#     #     result = release_unused_floating_ips(conn)
#     #     print (str(result))

#     #return the results files
#     return new_files