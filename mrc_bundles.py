from flask_assets import Bundle
from webassets.filter import get_filter
from webassets.filter.closure import ClosureJS
from sys import stderr
import uuid
import os


def gen_uuid() -> str:
    return str(uuid.uuid4().hex)


closure: ClosureJS = get_filter('closure_js')
os.environ['CLOSURE_COMPRESSOR_OPTIMIZATION'] = 'SIMPLE_OPTIMIZATIONS'
print(type(closure), file=stderr)

bundles = {

    'base_js': Bundle('js/util/*.js',
                        filters=closure,
                        output=f'dist/{gen_uuid()}.js'),

    'base_css': Bundle('css/*.css',
                         filters='cssmin',
                         output=f'dist/{gen_uuid()}.css'),

    'common_js': Bundle('common_bp/js/*.js',
                      filters=closure,
                      output=f'dist/{gen_uuid()}.js'),

    'common_css': Bundle('common_bp/css/*.css',
                        filters='cssmin',
                        output=f'dist/{gen_uuid()}.css')
}

