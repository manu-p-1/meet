from flask_assets import Bundle
import uuid


def gen_uuid() -> str:
    return str(uuid.uuid4().hex)


bundles = {

    'base_js': Bundle('js/util/*.js',
                        filters='jsmin',
                        output=f'dist/{gen_uuid()}.js'),

    'base_css': Bundle('css/*.css',
                         filters='cssmin',
                         output=f'dist/{gen_uuid()}.css'),

    'common_js': Bundle('common_bp/js/*.js',
                      filters='jsmin',
                      output=f'dist/{gen_uuid()}.js'),

    'common_css': Bundle('common_bp/css/*.css',
                        filters='cssmin',
                        output=f'dist/{gen_uuid()}.css')
}