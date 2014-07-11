#!python
"""Bootstrap setuptools installation

If you want to use setuptools in your package's setup.py, just include this
file in the same directory with it, and add this to the top of your setup.py::

    from ez_setup import use_setuptools
    use_setuptools()

If you want to require a specific version of setuptools, set a download
mirror, or use an alternate download directory, you can do so by supplying
the appropriate options to ``use_setuptools()``.

This file can also be run as a script to install or upgrade setuptools.
"""
import os
import shutil
import sys
import tempfile
import tarfile
import optparse
import subprocess
import platform

from distutils import log

try:
    from site import USER_SITE
except ImportError:
    USER_SITE = None

DEFAULT_VERSION = "1.1.7"
DEFAULT_URL = "https://pypi.python.org/packages/source/s/setuptools/"

def _python_cmd(*args):
    args = (sys.executable,) + args
    return subprocess.call(args) == 0

def _check_call_py24(cmd, *args, **kwargs):
    res = subprocess.call(cmd, *args, **kwargs)
    class CalledProcessError(Exception):
        pass
    if not res == 0:
        msg = "Command '%s' return non-zero exit status %d" % (cmd, res)
        raise CalledProcessError(msg)
vars(subprocess).setdefault('check_call', _check_call_py24)

def _install(tarball, install_args=()):
    # extracting the tarball
    tmpdir = tempfile.mkdtemp()
    log.warn('Extracting in %s', tmpdir)
    old_wd = os.getcwd()
    try:
        os.chdir(tmpdir)
        tar = tarfile.open(tarball)
        _extractall(tar)
        tar.close()

        # going in the directory
        subdir = os.path.join(tmpdir, os.listdir(tmpdir)[0])
        os.chdir(subdir)
        log.warn('Now working in %s', subdir)

        # installing
        log.warn('Installing Setuptools')
        if not _python_cmd('setup.py', 'install', *install_args):
            log.warn('Something went wrong during the installation.')
            log.warn('See the error message above.')
            # exitcode will be 2
            return 2
    finally:
        os.chdir(old_wd)
        shutil.rmtree(tmpdir)


def _build_egg(egg, tarball, to_dir):
    # extracting the tarball
    tmpdir = tempfile.mkdtemp()
    log.warn('Extracting in %s', tmpdir)
    old_wd = os.getcwd()
    try:
        os.chdir(tmpdir)
        tar = tarfile.open(tarball)
        _extractall(tar)
        tar.close()

        # going in the directory
        subdir = os.path.join(tmpdir, os.listdir(tmpdir)[0])
        os.chdir(subdir)
        log.warn('Now working in %s', subdir)

        # building an egg
        log.warn('Building a Setuptools egg in %s', to_dir)
        _python_cmd('setup.py', '-q', 'bdist_egg', '--dist-dir', to_dir)

    finally:
        os.chdir(old_wd)
        shutil.rmtree(tmpdir)
    # returning the result
    log.warn(egg)
    if not os.path.exists(egg):
        raise IOError('Could not build the egg.')


def _do_download(version, download_base, to_dir, download_delay):
    egg = os.path.join(to_dir, 'setuptools-%s-py%d.%d.egg'
                       % (version, sys.version_info[0], sys.version_info[1]))
    if not os.path.exists(egg):
        tarball = download_setuptools(version, download_base,
                                      to_dir, download_delay)
        _build_egg(egg, tarball, to_dir)
    sys.path.insert(0, egg)

    # Remove previously-imported pkg_resources if present (see
    # https://bitbucket.org/pypa/setuptools/pull-request/7/ for details).
    if 'pkg_resources' in sys.modules:
        del sys.modules['pkg_resources']

    import setuptools
    setuptools.bootstrap_install_from = egg


def use_setuptools(version=DEFAULT_VERSION, download_base=DEFAULT_URL,
                   to_dir=os.curdir, download_delay=15):
    # making sure we use the absolute path
    to_dir = os.path.abspath(to_dir)
    was_imported = 'pkg_resources' in sys.modules or \
        'setuptools' in sys.modules
    try:
        import pkg_resources
    except ImportError:
        return _do_download(version, download_base, to_dir, download_delay)
    try:
        pkg_resources.require("setuptools>=" + version)
        return
    except pkg_resources.VersionConflict:
        e = sys.exc_info()[1]
        if was_imported:
            sys.stderr.write(
            "The required version of setuptools (>=%s) is not available,\n"
            "and can't be installed while this script is running. Please\n"
            "install a more recent version first, using\n"
            "'easy_install -U setuptools'."
            "\n\n(Currently using %r)\n" % (version, e.args[0]))
            sys.exit(2)
        else:
            del pkg_resources, sys.modules['pkg_resources']    # reload ok
            return _do_download(version, download_base, to_dir,
                                download_delay)
    except pkg_resources.DistributionNotFound:
        return _do_download(version, download_base, to_dir,
                            download_delay)

def _clean_check(cmd, target):
    """
    Run the command to download target. If the command fails, clean up before
    re-raising the error.
    """
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        if os.access(target, os.F_OK):
            os.unlink(target)
        raise

def download_file_powershell(url, target):
    """
    Download the file at url to target using Powershell (which will validate
    trust). Raise an exception if the command cannot complete.
    """
    target = os.path.abspath(target)
    cmd = [
        'powershell',
        '-Command',
        "(new-object System.Net.WebClient).DownloadFile(%(url)r, %(target)r)" % vars(),
    ]
    _clean_check(cmd, target)

def has_powershell():
    if platform.system() != 'Windows':
        return False
    cmd = ['powershell', '-Command', 'echo test']
    devnull = open(os.path.devnull, 'wb')
    try:
        try:
            subprocess.check_call(cmd, stdout=devnull, stderr=devnull)
        except:
            return False
    finally:
        devnull.close()
    return True

download_file_powershell.viable = has_powershell

def download_file_curl(url, target):
    cmd = ['curl', url, '--silent', '--output', target]
    _clean_check(cmd, target)

def has_curl():
    cmd = ['curl', '--version']
    devnull = open(os.path.devnull, 'wb')
    try:
        try:
            subprocess.check_call(cmd, stdout=devnull, stderr=devnull)
        except:
            return False
    finally:
        devnull.close()
    return True

download_file_curl.viable = has_curl

def download_file_wget(url, target):
    cmd = ['wget', url, '--quiet', '--output-document', target]
    _clean_check(cmd, target)

def has_wget():
    cmd = ['wget', '--version']
    devnull = open(os.path.devnull, 'wb')
    try:
        try:
            subprocess.check_call(cmd, stdout=devnull, stderr=devnull)
        except:
            return False
    finally:
        devnull.close()
    return True

download_file_wget.viable = has_wget

def download_file_insecure(url, target):
    """
    Use Python to download the file, even though it cannot authenticate the
    connection.
    """
    try:
        from urllib.request import urlopen
    except ImportError:
        from urllib2 import urlopen
    src = dst = None
    try:
        src = urlopen(url)
        # Read/write all in one block, so we don't create a corrupt file
        # if the download is interrupted.
        data = src.read()
        dst = open(target, "wb")
        dst.write(data)
    finally:
        if src:
            src.close()
        if dst:
            dst.close()

download_file_insecure.viable = lambda: True

def get_best_downloader():
    downloaders = [
        download_file_powershell,
        download_file_curl,
        download_file_wget,
        download_file_insecure,
    ]

    for dl in downloaders:
        if dl.viable():
            return dl

def download_setuptools(version=DEFAULT_VERSION, download_base=DEFAULT_URL,
                        to_dir=os.curdir, delay=15,
                        downloader_factory=get_best_downloader):
    """Download setuptools from a specified location and return its filename
