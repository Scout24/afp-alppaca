import sys

from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")


name = "alppaca"
default_task = "publish"


@init
def set_properties(project):
    if sys.version_info[0:2] < (2, 7):
        project.depends_on("ordereddict")
        project.depends_on("unittest2")
    project.depends_on("apscheduler")
    project.depends_on("bottle")
    project.depends_on("mock")
    project.depends_on("requests_mock")
    project.depends_on("webtest")