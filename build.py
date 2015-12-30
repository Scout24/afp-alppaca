import sys

from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin("python.integrationtest")
use_plugin('copy_resources')


name = "afp-alppaca"
description = """
    alppaca is a client-side daemon that mimics the AWS meta-data service on link-local 169.254.169.254.
    It is useful for fetching IAM role based credentials for instances not based in Amazon.
    """
default_task = "publish"
version = '1.0'


@init
def set_properties(project):
    project.set_property('install_dependencies_upgrade', True)
    if sys.version_info[0:2] < (2, 7):
        project.depends_on("ordereddict")
        project.depends_on("unittest2")
    project.depends_on("apscheduler")
    project.depends_on("bottle")
    project.depends_on("isodate")
    project.depends_on("pils")
    project.depends_on("succubus")
    project.build_depends_on("mock")
    project.build_depends_on("requests-mock")
    project.depends_on("webtest")
    project.depends_on("argparse")
    project.depends_on("yamlreader")
    project.depends_on("six")
    project.depends_on("boto")
    project.depends_on("datetime")
    project.set_property('copy_resources_target', '$dir_dist')
    project.get_property('copy_resources_glob').append('setup.cfg')
    project.get_property('copy_resources_glob').append('pre-install.sh')
    project.get_property('copy_resources_glob').append('post-install.sh')
    project.install_file('/etc/init.d/alppaca', 'src/main/scripts/alppacad')
    project.get_property('coverage_exceptions').append('afp_alppaca.util')


@init(environments='teamcity')
def set_properties_for_teamcity_builds(project):
    import os
    project.set_property('teamcity_output', True)
    project.version = '%s-%s' % (project.version, os.environ.get('BUILD_NUMBER', 0))
    project.default_task = ['clean', 'install_build_dependencies', 'publish']
    project.set_property('install_dependencies_index_url', os.environ.get('PYPIPROXY_URL'))
    project.get_property('distutils_commands').append('bdist_rpm')
