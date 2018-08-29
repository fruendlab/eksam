#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'eksam',
        version = '0.1',
        description = '',
        long_description = '',
        author = '',
        author_email = '',
        license = '',
        url = '',
        scripts = [
            'scripts/eksam-server',
            'scripts/eksam-cli'
        ],
        packages = ['eksam'],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        entry_points = {},
        data_files = [],
        package_data = {
            'eksam': ['templates/base.html.j2', 'templates/exam.html.j2', 'templates/finish.html.j2', 'templates/register.html.j2']
        },
        install_requires = [
            'Flask',
            'docopt',
            'jinja2',
            'pony',
            'pyjwt',
            'pyyaml',
            'requests',
            'selenium'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
