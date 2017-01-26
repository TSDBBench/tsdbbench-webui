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
        'config_file_path_db': '/home/vagrant/TSDBBench/vagrant_files/vagrantconf_db.rb',
        'supported_databases': {
            'akumuli': ['cl1_rf1'],
            'blueflood': ['cl1_rf1', 'cl5_rf1', 'cl5_rf2', 'cl5_rf5'],
            'databus_rtable': ['cl1_rf1'],
            'databus_rtstable': ['cl1_rf1'],
            'databus_tstable': ['cl1_rf1'],
            'druid': ['cl1_rf1', 'cl5_rf1', 'cl5_rf2', 'cl5_rf5'],
            'elasticsearch': ['cl1_rf1', 'cl5_rf1'],
            'gnocchi': ['cl1'],
            'graphite': ['cl1_rf1'],
            'h5serv': ['cl1_rf1'],
            'influxdb': ['cl1_rf1', 'cl5_rf1', 'cl5_rf2', 'cl5_rf5'],
            'kairosdb': ['cl1_rf1', 'cl5_rf1', 'cl5_rf2', 'cl5_rf5'],
            'kairosdb_h2': ['cl1_rf1'],
            'kdbplus': ['cl1_rf1'],
            'monetdb': ['cl1_rf1'],
            'mysql': ['cl1_rf1'],
            'newts': ['cl1_rf1', 'cl5_rf1', 'cl5_rf2', 'cl5_rf5'],
            'opentsdb': ['cl1_rf1', 'cl5_rf1', 'cl5_rf2', 'cl5_rf5'],
            'postgresql': ['cl1_rf1'],
            'rhombus': ['cl1_rf1', 'cl5_rf1', 'cl5_rf2', 'cl5_rf5'],
            'seriesly': ['cl1_rf1']
        }
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
