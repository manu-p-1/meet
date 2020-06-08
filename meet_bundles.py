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
                         output=f'dist/{gen_uuid()}.css'),

    'dash_js': Bundle('user_bp/js/shards-dashboards.1.1.0.js',
                      'user_bp/js/shards.js',
                      'user_bp/js/dash_common.js',
                      filters=closure,
                      output=f'dist/dash/{gen_uuid()}.js'),

    "dash_css": Bundle('user_bp/css/dash-base.css',
                       'user_bp/css/shards-dashboards.1.1.0.css',
                       filters='cssmin',
                       output=f'dist/dash/{gen_uuid()}.css'),

    "dash_overview_js": Bundle('user_bp/js/overview/*.js',
                               filters=closure,
                               output=f'dist/dash/overview/{gen_uuid()}.js'),

    "dash_overview_css": Bundle('user_bp/css/overview/*.css',
                                filters='cssmin',
                                output=f'dist/dash/overview/{gen_uuid()}.css'),

    "dash_plan_css": Bundle('user_bp/css/plan_base.css',
                            filters='cssmin',
                            output=f'dist/dash/{gen_uuid()}.css'),

    "dash_create_plan_js": Bundle('user_bp/js/form_common.js',
                                  'user_bp/js/create_plan/*.js',
                                  filters=closure,
                                  output=f'dist/dash/create_plan/{gen_uuid()}.js'),

    "dash_manage_plan_js": Bundle('user_bp/js/form_common.js',
                                  'user_bp/js/manage_plan/*.js',
                                  filters=closure,
                                  output=f'dist/dash/manage_plan/{gen_uuid()}.js')

}
