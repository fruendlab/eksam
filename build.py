from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
# use_plugin("python.coverage")
use_plugin("python.distutils")


name = "eksam"
default_task = "publish"
version = '0.1'


@init
def set_properties(project):
    project.depends_on('Flask')
    project.depends_on('pony')
    project.depends_on('pyyaml')
    project.depends_on('pyjwt')
    project.depends_on('requests')
    project.depends_on('docopt')
