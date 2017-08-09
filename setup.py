#!/usr/bin/python -u
#
# Python Bindings for XZ/LZMA backported from Python 3.3.0
#
# This file copyright (c) 2012 Peter Cock, p.j.a.cock@googlemail.com
# See other files for separate copyright notices.

import sys, os
import subprocess

from distutils.command.build_ext import build_ext
from distutils.core import setup
from distutils.extension import Extension

# We now extract the version number in backports/lzma/__init__.py
# We can't use "from backports import lzma" then "lzma.__version__"
# as that would tell us the version already installed (if any).
__version__ = None
with open('backports/lzma/__init__.py') as handle:
    for line in handle:
        if line.startswith('__version__'):
            exec(line.strip())
            break
if __version__ is None:
    sys.stderr.write("Error getting __version__ from backports/lzma/__init__.py\n")
    sys.exit(1)
print("This is backports.lzma version %s" % __version__)


def pkg_config(*args):
    """Call pkg-config and return stdout data on success."""
    try:
        stdout = subprocess.check_output(
            ["pkg-config"] + list(args),
            universal_newlines=True,
        )
    except Exception as e:
        print("Running pkg-config %s failed: %r" % (" ".join(args), e))
        return
    return stdout.strip()


def get_include_dirs():
    """Return list of include dirs to use for building."""
    pc_dir = pkg_config("--variable=includedir", "liblzma")
    dirs = [
        os.path.join(prefix, 'include'),
        os.path.join(home, 'include'),
        '/opt/local/include',
        '/usr/local/include',
    ]
    if pc_dir:
        dirs.append(pc_dir)
    if sys.platform == "win32":
        dirs.append(os.path.join("windows", "include"))
    return dirs


def get_library_dirs():
    """Return list of library dirs to use for building."""
    pc_dir = pkg_config("--variable=libdir", "liblzma")
    dirs = [
        os.path.join(prefix, 'lib'),
        os.path.join(home, 'lib'),
        '/opt/local/lib',
        '/usr/local/lib',
    ]
    if pc_dir:
        dirs.append(pc_dir)
    if sys.platform == "win32":
        dirs.append(os.path.join("windows", "lib"))
    return dirs


packages = ["backports", "backports.lzma"]
prefix = sys.prefix
home = os.path.expanduser("~")
define_macros = [("LZMA_API_STATIC", None)] if os.name == "nt" else []
extra_objects = [os.path.join("windows", "lib", "liblzma.a")] if os.name == "nt" else []
libraries = [] if os.name == "nt" else ['lzma']
extens = [Extension('backports.lzma._lzma',
                    ['backports/lzma/_lzmamodule.c'],
                    libraries = libraries,
                    include_dirs = get_include_dirs(),
                    library_dirs = get_library_dirs(),
                    define_macros=define_macros,
                    extra_objects=extra_objects,
                    )]

descr = "Backport of Python 3.3's 'lzma' module for XZ/LZMA compressed files."
long_descr = """This is a backport of the 'lzma' module included in Python 3.3 or later
by Nadeem Vawda and Per Oyvind Karlsen, which provides a Python wrapper for XZ Utils
(aka LZMA Utils v2) by Igor Pavlov.

In order to compile this, you will need to install XZ Utils from http://tukaani.org/xz/
"""

if sys.version_info < (2,6):
    sys.stderr.write("ERROR: Python 2.5 and older are not supported, and probably never will be.\n")
    sys.exit(1)

setup(
    name = "backports.lzma",
    version = __version__,
    description = descr,
    author = "Peter Cock, based on work by Nadeem Vawda and Per Oyvind Karlsen",
    author_email = "p.j.a.cock@googlemail.com",
    url = "https://github.com/peterjc/backports.lzma",
    license='3-clause BSD License',
    keywords = "xz lzma compression decompression",
    long_description = long_descr,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        #'Operating System :: OS Independent',
        'Topic :: System :: Archiving :: Compression',
    ],
    packages = packages,
    namespace_packages = ['backports'],
    ext_modules = extens,
    cmdclass = {
        'build_ext': build_ext,
    },
)
