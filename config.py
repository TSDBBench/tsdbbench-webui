import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'zJodBOgCOq0sPWNogYQM'
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
    RESULTDIR = 'benchmark_results'
    TSDBBENCH_SETTINGS = {
        'home_folder': '/home/vagrant/TSDBBench/',
        'results_folder': '/var/www/html/TSDBBench/',
        'temp_folder': '/home/vagrant/tmp/',
        'vagrant_files': '/home/vagrant/TSDBBench/vagrant_files/',
        'config_file_path': '/home/vagrant/TSDBBench/vagrant_files/vagrantconf.rb',
        'config_file_path_gen': '/home/vagrant/TSDBBench/vagrant_files/vagrantconf_gen.rb',
        'config_file_path_db': '/home/vagrant/TSDBBench/vagrant_files/vagrantconf_db.rb',
        'vm_user': 'vagrant',
        'provider': {
            'Openstack': {
                'openstack_auth_url': 'http://129.69.209.131:5000/v2.0/tokens',
                'openstack.tenant_name': 'pc-webui-tsdbbench',
                'openstack.image': 'TSDBBench (Debian Jessie 8.6)',
                'openstack.openstack_image_url':                                                                        'http://129.69.209.131:8776/v1/154db9c9c56e44bc8afcd423d1cbc13e',
                'openstack.flavor': 'm1.larger'
            }
        },

        'supported_databases': [
            { 'name': 'akumuli', 'configs': ['cl1_rf1'] },
            { 'name': 'blueflood', 'configs': ['cl1_rf1', 'cl5_rf1', 'cl5_rf2', 'cl5_rf5'] },
            { 'name': 'databus_rtable', 'configs': ['cl1_rf1'] },
            { 'name': 'databus_rtstable', 'configs': ['cl1_rf1'] },
            { 'name': 'databus_tstable', 'configs': ['cl1_rf1'] },
            { 'name': 'druid', 'configs': ['cl1_rf1', 'cl5_rf1', 'cl5_rf2', 'cl5_rf5'] },
            { 'name': 'elasticsearch', 'configs': ['cl1_rf1', 'cl5_rf1'] },
            { 'name': 'gnocchi', 'configs': ['cl1'] },
            { 'name': 'graphite', 'configs': ['cl1_rf1'] },
            { 'name': 'h5serv', 'configs': ['cl1_rf1'] },
            { 'name': 'influxdb', 'configs': ['cl1_rf1', 'cl5_rf1', 'cl5_rf2', 'cl5_rf5'] },
            { 'name': 'kairosdb', 'configs': ['cl1_rf1', 'cl5_rf1', 'cl5_rf2', 'cl5_rf5'] },
            { 'name': 'kairosdb_h2', 'configs': ['cl1_rf1'] },
            { 'name': 'kdbplus', 'configs': ['cl1_rf1'] },
            { 'name': 'monetdb', 'configs': ['cl1_rf1'] },
            { 'name': 'mysql', 'configs': ['cl1_rf1'] },
            { 'name': 'newts', 'configs': ['cl1_rf1', 'cl5_rf1', 'cl5_rf2', 'cl5_rf5'] },
            { 'name': 'opentsdb', 'configs': ['cl1_rf1', 'cl5_rf1', 'cl5_rf2', 'cl5_rf5'] },
            { 'name': 'postgresql', 'configs': ['cl1_rf1'] },
            { 'name': 'rhombus', 'configs': ['cl1_rf1', 'cl5_rf1', 'cl5_rf2', 'cl5_rf5'] },
            { 'name': 'seriesly', 'configs': ['cl1_rf1'] }
        ]
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
