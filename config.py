import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    PROVIDERS = [
        {
            'provider': 'Openstack',
            'host': 'http://129.69.209.131:5000',
            'project': 'pc-webui-tsdbbench',
            'region': "RegionOne"
        }
    ]
    SESSION_TYPE = 'filesystem'
    KEYDIR = 'disposables'
    VM_USER_NAME = 'vagrant'
    TSDBBENCH_SETTINGS = {
        'provider': {
            'Openstack': {
                'openstack_auth_url': 'http://129.69.209.131:5000/v2.0/tokens',
                'openstack.tenant_name': 'pc-webui-tsdbbench',
                'openstack.image': 'TSDBBench (Debian Jessie 8.6)',
                'openstack.openstack_image_url':                                                                        'http://129.69.209.131:8776/v1/154db9c9c56e44bc8afcd423d1cbc13e',
                'openstack.flavor': 'm1.larger'
            }
        },
        'config_file_path': '/home/vagrant/TSDBBench/vagrant_files/vagrantconf.rb',
        'config_file_path_gen': '/home/vagrant/TSDBBench/vagrant_files/vagrantconf_gen.rb',
        'config_file_path_db': '/home/vagrant/TSDBBench/vagrant_files/vagrantconf_db.rb'
    }


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
