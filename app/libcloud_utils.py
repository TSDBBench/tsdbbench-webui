from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


def get_openstack_connection(auth_username, auth_password, auth_url, project_name, region_name):
    try:
        provider = get_driver(Provider.OPENSTACK)
        conn = provider(auth_username,
                        auth_password,
                        ex_force_auth_url=auth_url,
                        ex_force_auth_version='2.0_password',
                        ex_tenant_name=project_name,
                        ex_force_service_region=region_name)
        # list all security groups to test the connection
        conn.ex_list_security_groups()
        return {
            'user': auth_username,
            'connection': conn
        }

    except Exception as exception:
        # print(type(exception))  # the exception instance
        # print(exception.args)  # arguments stored in .args
        # print(exception)
        return {
            'user': auth_username,
            'exception': exception,
            'exceptionType': type(exception)
        }


def get_openstack_image_object_catalog(conn):
    try:
        image_objects = conn.list_images()
        return image_objects
    except Exception as e:
        print(str(e))
        return e


def get_openstack_image_catalog(conn):
    try:
        result = []
        for image in conn.list_images():
            i = {
                'id': image.id,
                'name': image.name
            }
            result.append(i)
        return result
    except Exception as e:
        print(str(e))
        return e


def get_openstack_flavor_object_catalog(conn):
    try:
        flavor_objects = conn.list_sizes()
        return flavor_objects
    except Exception as e:
        print(str(e))
        return e


def get_openstack_flavor_catalog(conn):
    try:
        result = []
        for flavor in conn.list_sizes():
            f = {
                'bandwidth': flavor.bandwidth,
                'disk': flavor.disk,
                'ephemeral_disk': flavor.ephemeral_disk,
                'extra': flavor.extra,
                'id': flavor.id,
                'name': flavor.name,
                'price': flavor.price,
                'ram': flavor.ram,
                'swap': flavor.swap,
                'uuid': flavor.uuid,
                'vcpus': flavor.vcpus
            }
            result.append(f)
        return result
    except Exception as e:
        print(str(e))
        return e


def get_openstack_node_catalog(conn):
    try:
        result = []
        for node in conn.list_nodes():
            n = {
                'created_at': node.created_at,
                'extra': node.extra,
                'id': node.id,
                'image': node.image,
                'name': node.name,
                'private_ips': node.private_ips,
                'public_ips': node.public_ips,
                'size': node.size,
                'state': node.state,
                'uuid': node.uuid
            }
            result.append(n)
        return result
    except Exception as e:
        print(str(e))
        return e


def get_openstack_node_object_catalog(conn):
    try:
        node_objects = conn.list_nodes()
        return node_objects
    except Exception as e:
        print(str(e))
        return e


def get_openstack_security_group_list(conn):
    try:
        result = []
        for group in conn.ex_list_security_groups():
            g = {
                'description': group.description,
                'extra': group.extra,
                'id': group.id,
                'name': group.name,
                'rules': [],
                'tenant_id': group.tenant_id
            }
            for rule in group.rules:
                r = {
                    'extra': rule.extra,
                    'from_port': rule.from_port,
                    'group': rule.group,
                    'id': rule.id,
                    'ip_protocol': rule.ip_protocol,
                    'ip_range': rule.ip_range,
                    'parent_group_id': rule.parent_group_id,
                    'tenant_id': rule.tenant_id,
                    'to_port': rule.to_port
                }
                g['rules'].append(r)
            result.append(g)
        return result
    except Exception as e:
        print(str(e))
        return e


def get_openstack_sec_group_object_catalog(conn):
    try:
        sgroup_objects = conn.ex_list_security_groups()
        return sgroup_objects
    except Exception as e:
        print(str(e))
        return e


def import_key_pair(conn, key_pair_name, public_key_path):
    try:
        conn.import_key_pair_from_file(name=key_pair_name, key_file_path=public_key_path)
        return True
    except Exception as e:
        print(str(e))
        return e


def get_key_pair_by_name(conn, key_name):
    try:
        key = conn.get_key_pair(name=key_name)
        return key
    except Exception as e:
        print(str(e))
        return e


def get_sec_group_object_by_name(conn, security_group_name):
    try:
        for security_group in conn.ex_list_security_groups():
            if security_group.name == security_group_name:
                return security_group
            else:
                return False
    except Exception as e:
        print(str(e))
        return e


def instantiate_node(conn, instance_name, image, flavor, key_pair_name, sec_group):
    try:
        print('Checking for existing instance...')
        instance_exists = False
        for instance in conn.list_nodes():
            if instance.name == instance_name:
                instance_exists = True

        if instance_exists:
            print('Instance ' + instance_name + ' already exists. Skipping creation.')
        else:
            print('Instance ' + instance_name + ' does not exist. Creating...')
            image_obj = conn.get_image(image)
            flavor_obj = conn.ex_get_size(flavor)
            sec_group_obj = get_sec_group_object_by_name(conn, sec_group)
            testing_instance = conn.create_node(name=instance_name,
                                                image=image_obj,
                                                size=flavor_obj,
                                                ex_keyname=key_pair_name,
                                                ex_security_groups=[sec_group_obj])
            conn.wait_until_running([testing_instance])
        print('Instance was successfully created')
        
        new_node = {}
        new_node["success"] = True
        new_node["uuid"] = testing_instance.uuid
        new_node["name"] = testing_instance.name
        new_node["created_at"] = testing_instance.created_at
        new_node["image"] = testing_instance.image
        new_node["extra"] = testing_instance.extra
        new_node["private_ips"] = testing_instance.private_ips
        new_node["public_ips"] = testing_instance.public_ips
        new_node["size"] = testing_instance.size
        new_node["state"] = testing_instance.state
        new_node["id"] = testing_instance.id

        return new_node

    except Exception as e:
        print("instantiate_node exception: " + str(e))
        return e


def reboot_instance(conn, node_id):
    try:
        n = get_node_by_id(conn, node_id)
        if n is not None:
            return conn.reboot_node(n)
        return False
    except Exception as e:
        print("reboot_instance exception: " + str(e))
        return e


def stop_instance(conn, node_id):
    try:
        n = get_node_by_id(conn, node_id)
        if n is not None:
            return conn.ex_stop_node(n)
        return False
    except Exception as e:
        print(str(e))
        return e


def start_instance(conn, node_id):
    try:
        n = get_node_by_id(conn, node_id)
        if n is not None:
            return conn.ex_start_node(n)
        return False
    except Exception as e:
        print(str(e))
        return e


def terminate_instance(conn, node_id):
    try:
        n = get_node_by_id(conn, node_id)
        if n is not None:
            return conn.destroy_node(n)
        return None
    except Exception as e:
        return e


def delete_key_pair(conn, key_name):
    try:
        print("start delete keypair")
        key_obj = get_key_pair_by_name(conn, key_name)
        conn.delete_key_pair(key_obj)
        return True
    except Exception as e:
        return e


def get_floating_ips_catalog(conn):
    try:
        floating_ips = []

        for fip in conn.ex_list_floating_ips():
            if fip.node_id == None:
                f = {
                    'id': fip.id,
                    'ip_address': fip.ip_address,
                    'node_id': fip.node_id
                }
                floating_ips.append(f)

        return floating_ips

    except Exception as e:
        return e


def allocate_floating_ip(conn):
    try:
        pools = conn.ex_list_floating_ip_pools()
        for pool in pools:
            if pool.name == 'float':
                print('Allocating new Floating IP from pool: {}'.format(pool))
                unused_fip = pool.create_floating_ip()
                print(unused_fip)
                return {
                    'id': unused_fip.id,
                    'ip_address': unused_fip.ip_address,
                    'node_id': unused_fip.node_id
                }
        return False
    except Exception as e:
        return e

def get_floating_ip_by_id(conn, ip_id):
    try:
        for fip in conn.ex_list_floating_ips():
            if fip.id == ip_id:
                return fip
        return None
    except Exception as e:
        return e


def get_floating_ip_by_node_id(conn, node_id):
    try:
        for fip in conn.ex_list_floating_ips():
            if fip.node_id == node_id:
                return fip.ip_address
        return None
    except Exception as e:
        return e


def get_node_by_id(conn, node_id):
    try:
        for node in conn.list_nodes():
            if node.id == node_id:
                return node
        return None
    except Exception as e:
        return e


def attach_floating_ip(conn, floating_ip, node_id):
    try:
        f = get_floating_ip_by_id(conn, floating_ip)
        n = get_node_by_id(conn, node_id)
        if f is not None and n is not None:
            return conn.ex_attach_floating_ip_to_node(n, f)
        return False
    except Exception as e:
        return e


def release_unused_floating_ips(conn):
    try:
        float_ips = conn.ex_list_floating_ips()
        for ip in float_ips:
            if "None" in str(ip.node_id):
                ip.delete()
        return True
    except Exception as e:
        return e


def key_remove_is_allowed(conn, key_name):
    try:
        for node in conn.list_nodes():
            if node.extra['key_name'] == key_name:
                return False
        return True
    except Exception as e:
        return e
