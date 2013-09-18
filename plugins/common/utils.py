#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:utils.py
# Date:Fri Sep 13 17:46:30 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
import contextlib
import errno
import functools
import hashlib
import os
import random
import re
import shutil
import socket
import sys
import tempfile
import threading
import time
import uuid
from xml.dom import minidom
from xml.parsers import expat
from xml import sax
from xml.sax import expatreader

from eventlet import corolocal
from eventlet import event
from eventlet import greenthread
from eventlet.green import subprocess
import exception
import lockfile
import netaddr
from django.utils.translation import ugettext as _
from ccf.etc import config
import logging
LOG = logging.getLogger(__file__)


def import_class(import_str):
    """Returns a class from a string including module and class."""
    mod_str, _sep, class_str = import_str.rpartition('.')
    try:
        __import__(mod_str)
        return getattr(sys.modules[mod_str], class_str)
    except (ImportError, ValueError, AttributeError) as exc:
        LOG.debug('Inner Exception: %s', exc)
        raise exception.ClassNotFound(class_name=class_str, exception=exc)


def import_object(import_str):
    """Returns an object including a module or module and class."""
    try:
        __import__(import_str)
        return sys.modules[import_str]
    except ImportError:
        cls = import_class(import_str)
        return cls()


def fetchfile(url, target):
    LOG.debug(_('Fetching %s') % url)
    execute('curl', '--fail', url, '-o', target)


def execute(*cmd, **kwargs):
    """Helper method to execute command with optional retry.

    If you add a run_as_root=True command, don't forget to add the
    corresponding filter to nova.rootwrap !

    :param cmd:                Passed to subprocess.Popen.
    :param process_input:      Send to opened process.
    :param check_exit_code:    Single bool, int, or list of allowed exit
                               codes.  Defaults to [0].  Raise
                               exception.ProcessExecutionError unless
                               program exits with one of these code.
    :param delay_on_retry:     True | False. Defaults to True. If set to
                               True, wait a short amount of time
                               before retrying.
    :param attempts:           How many times to retry cmd.
    :param run_as_root:        True | False. Defaults to False. If set to True,
                               the command is prefixed by the command specified
                               in the root_helper FLAG.

    :raises exception.Error: on receiving unknown arguments
    :raises exception.ProcessExecutionError:

    :returns: a tuple, (stdout, stderr) from the spawned process, or None if
             the command fails.
    """

    process_input = kwargs.pop('process_input', None)
    check_exit_code = kwargs.pop('check_exit_code', [0])
    ignore_exit_code = False
    if isinstance(check_exit_code, bool):
        ignore_exit_code = not check_exit_code
        check_exit_code = [0]
    elif isinstance(check_exit_code, int):
        check_exit_code = [check_exit_code]
    delay_on_retry = kwargs.pop('delay_on_retry', True)
    attempts = kwargs.pop('attempts', 1)
    shell = kwargs.pop('shell', False)
    if len(kwargs):
        raise exception.Error(_('Got unknown keyword args '
                                'to utils.execute: %r') % kwargs)
    cmd = map(str, cmd)
    while attempts > 0:
        attempts -= 1
        try:
            LOG.debug(_('Running cmd (subprocess): %s'), ' '.join(cmd))
            _PIPE = subprocess.PIPE  # pylint: disable=E1101
            obj = subprocess.Popen(cmd,
                                   stdin=_PIPE,
                                   stdout=_PIPE,
                                   stderr=_PIPE,
                                   close_fds=True,
                                   shell=shell)
            result = None
            if process_input is not None:
                result = obj.communicate(process_input)
            else:
                result = obj.communicate()
            obj.stdin.close()  # pylint: disable=E1101
            _returncode = obj.returncode  # pylint: disable=E1101
            if _returncode:
                LOG.debug(_('Result was %s') % _returncode)
                if not ignore_exit_code and _returncode not in check_exit_code:
                    (stdout, stderr) = result
                    raise exception.ProcessExecutionError(
                        exit_code=_returncode,
                        stdout=stdout,
                        stderr=stderr,
                        cmd=' '.join(cmd))
            return result
        except exception.ProcessExecutionError:
            if not attempts:
                raise
            else:
                LOG.debug(_('%r failed. Retrying.'), cmd)
                if delay_on_retry:
                    greenthread.sleep(random.randint(20, 200) / 100.0)
        finally:
            # NOTE(termie): this appears to be necessary to let the subprocess
            #               call clean something up in between calls, without
            #               it two execute calls in a row hangs the second one
            greenthread.sleep(0)


def trycmd(*args, **kwargs):
    """
    A wrapper around execute() to more easily handle warnings and errors.

    Returns an (out, err) tuple of strings containing the output of
    the command's stdout and stderr.  If 'err' is not empty then the
    command can be considered to have failed.

    :discard_warnings   True | False. Defaults to False. If set to True,
                        then for succeeding commands, stderr is cleared

    """
    discard_warnings = kwargs.pop('discard_warnings', False)

    try:
        out, err = execute(*args, **kwargs)
        failed = False
    except exception.ProcessExecutionError as exn:
        out, err = '', str(exn)
        LOG.debug(err)
        failed = True

    if not failed and discard_warnings and err:
        # Handle commands that output to stderr but otherwise succeed
        LOG.debug(err)
        err = ''

    return out, err


def ssh_execute(ssh, cmd, process_input=None,
                addl_env=None, check_exit_code=True):
    LOG.debug(_('Running cmd (SSH): %s'), ' '.join(cmd))
    if addl_env:
        raise exception.Error(_('Environment not supported over SSH'))

    if process_input:
        # This is (probably) fixable if we need it...
        raise exception.Error(_('process_input not supported over SSH'))

    stdin_stream, stdout_stream, stderr_stream = ssh.exec_command(cmd)
    channel = stdout_stream.channel

    # stdin.write('process_input would go here')
    # stdin.flush()

    # NOTE(justinsb): This seems suspicious...
    # ...other SSH clients have buffering issues with this approach
    stdout = stdout_stream.read()
    stderr = stderr_stream.read()
    stdin_stream.close()

    exit_status = channel.recv_exit_status()

    # exit_status == -1 if no exit code was returned
    if exit_status != -1:
        LOG.debug(_('Result was %s') % exit_status)
        if check_exit_code and exit_status != 0:
            raise exception.ProcessExecutionError(exit_code=exit_status,
                                                  stdout=stdout,
                                                  stderr=stderr,
                                                  cmd=' '.join(cmd))

    return (stdout, stderr)


def generate_uid(topic, size=8):
    characters = '01234567890abcdefghijklmnopqrstuvwxyz'
    choices = [random.choice(characters) for x in xrange(size)]
    return '%s-%s' % (topic, ''.join(choices))


def last_octet(address):
    return int(address.split('.')[-1])


def get_my_linklocal(interface):
    try:
        if_str = execute('ip', '-f', 'inet6', '-o', 'addr', 'show', interface)
        condition = '\s+inet6\s+([0-9a-f:]+)/\d+\s+scope\s+link'
        links = [re.search(condition, x) for x in if_str[0].split('\n')]
        address = [w.group(1) for w in links if w is not None]
        if address[0] is not None:
            return address[0]
        else:
            raise exception.Error(_('Link Local address is not found.:%s')
                                  % if_str)
    except Exception as ex:
        raise exception.Error(_("Couldn't get Link Local IP of %(interface)s"
                                " :%(ex)s") % locals())


class LoopingCallDone(Exception):

    """
    Exception to break out and stop a LoopingCall.
    """

    def __init__(self, retvalue=True):
        """:param retvalue: Value that LoopingCall.wait() should return."""
        self.retvalue = retvalue


class LoopingCall(object):

    def __init__(self, f=None, *args, **kw):
        self.args = args
        self.kw = kw
        self.f = f
        self._running = False

    def start(self, interval, now=True):
        self._running = True
        done = event.Event()

        def _inner():
            if not now:
                greenthread.sleep(interval)
            try:
                while self._running:
                    self.f(*self.args, **self.kw)
                    if not self._running:
                        break
                    greenthread.sleep(interval)
            except LoopingCallDone as e:
                self.stop()
                done.send(e.retvalue)
            except Exception:
                LOG.exception(_('in looping call'))
                done.send_exception(*sys.exc_info())
                return
            else:
                done.send(True)

        self.done = done

        greenthread.spawn(_inner)
        return self.done

    def stop(self):
        self._running = False

    def wait(self):
        return self.done.wait()


class ProtectedExpatParser(expatreader.ExpatParser):

    """An expat parser which disables DTD's and entities by default."""

    def __init__(self, forbid_dtd=True, forbid_entities=True,
                 *args, **kwargs):
        # Python 2.x old style class
        expatreader.ExpatParser.__init__(self, *args, **kwargs)
        self.forbid_dtd = forbid_dtd
        self.forbid_entities = forbid_entities

    def start_doctype_decl(self, name, sysid, pubid, has_internal_subset):
        raise ValueError("Inline DTD forbidden")

    def entity_decl(self, entityName, is_parameter_entity, value, base,
                    systemId, publicId, notationName):
        raise ValueError("<!ENTITY> forbidden")

    def unparsed_entity_decl(self, name, base, sysid, pubid, notation_name):
        # expat 1.2
        raise ValueError("<!ENTITY> forbidden")

    def reset(self):
        expatreader.ExpatParser.reset(self)
        if self.forbid_dtd:
            self._parser.StartDoctypeDeclHandler = self.start_doctype_decl
        if self.forbid_entities:
            self._parser.EntityDeclHandler = self.entity_decl
            self._parser.UnparsedEntityDeclHandler = self.unparsed_entity_decl


def safe_minidom_parse_string(xml_string):
    """Parse an XML string using minidom safely.

    """
    try:
        return minidom.parseString(xml_string, parser=ProtectedExpatParser())
    except sax.SAXParseException:
        raise expat.ExpatError()


def utf8(value):
    """
    Try to turn a string into utf-8 if possible.
    """
    if isinstance(value, unicode):
        return value.encode('utf-8')
    assert isinstance(value, str)
    return value


class GreenLockFile(lockfile.FileLock):

    """Implementation of lockfile that allows for a lock per greenthread.

    Simply implements lockfile:LockBase init with an addiontall suffix
    on the unique name of the greenthread identifier
    """
    def __init__(self, path, threaded=True):
        self.path = path
        self.lock_file = os.path.abspath(path) + ".lock"
        self.hostname = socket.gethostname()
        self.pid = os.getpid()
        if threaded:
            t = threading.current_thread()
            # Thread objects in Python 2.4 and earlier do not have ident
            # attrs.  Worm around that.
            ident = getattr(t, "ident", hash(t))
            gident = corolocal.get_ident()
            self.tname = "-%x-%x" % (ident & 0xffffffff, gident & 0xffffffff)
        else:
            self.tname = ""
        dirname = os.path.dirname(self.lock_file)
        self.unique_name = os.path.join(dirname,
                                        "%s%s.%s" % (self.hostname,
                                                     self.tname,
                                                     self.pid))


_semaphores = {}


def cleanup_file_locks():
    """clean up stale locks left behind by process failures

    The lockfile module, used by @synchronized, can leave stale lockfiles
    behind after process failure. These locks can cause process hangs
    at startup, when a process deadlocks on a lock which will never
    be unlocked.

    Intended to be called at service startup.

    """

    # NOTE(mikeyp) this routine incorporates some internal knowledge
    #              from the lockfile module, and this logic really
    #              should be part of that module.
    #
    # cleanup logic:
    # 1) look for the lockfile modules's 'sentinel' files, of the form
    #    hostname.[thread-.*]-pid, extract the pid.
    #    if pid doesn't match a running process, delete the file since
    #    it's from a dead process.
    # 2) check for the actual lockfiles. if lockfile exists with linkcount
    #    of 1, it's bogus, so delete it. A link count >= 2 indicates that
    #    there are probably sentinels still linked to it from active
    #    processes.  This check isn't perfect, but there is no way to
    #    reliably tell which sentinels refer to which lock in the
    #    lockfile implementation.
    hostname = socket.gethostname()
    sentinel_re = hostname + r'-.*\.(\d+$)'
    lockfile_re = r'nova-.*\.lock'
    files = os.listdir(config.lock_path)

    # cleanup sentinels
    for filename in files:
        match = re.match(sentinel_re, filename)
        if match is None:
            continue
        pid = match.group(1)
        LOG.debug(_('Found sentinel %(filename)s for pid %(pid)s') %
                  {'filename': filename, 'pid': pid})
        try:
            os.kill(int(pid), 0)
        except OSError as e:
            if e.errno == errno.ESRCH:
                # PID wasn't found
                delete_if_exists(os.path.join(config.lock_path, filename))
                LOG.debug(_('Cleaned sentinel %(filename)s for pid %(pid)s') %
                          {'filename': filename, 'pid': pid})

    # cleanup lock files
    for filename in files:
        match = re.match(lockfile_re, filename)
        if match is None:
            continue
        try:
            stat_info = os.stat(os.path.join(config.lock_path, filename))
        except OSError as e:
            if e.errno == errno.ENOENT:
                continue
            else:
                raise
        msg = (_('Found lockfile %(file)s with link count %(count)d') %
               {'file': filename, 'count': stat_info.st_nlink})
        LOG.debug(msg)
        if stat_info.st_nlink == 1:
            delete_if_exists(os.path.join(config.lock_path, filename))
            msg = (_('Cleaned lockfile %(file)s with link count %(count)d') %
                   {'file': filename, 'count': stat_info.st_nlink})
            LOG.debug(msg)


def delete_if_exists(pathname):
    """delete a file, but ignore file not found error"""

    try:
        os.unlink(pathname)
    except OSError as e:
        if e.errno == errno.ENOENT:
            return
        else:
            raise


def get_from_path(items, path):
    """Returns a list of items matching the specified path.
    """
    if path is None:
        raise exception.Error('Invalid mini_xpath')

    (first_token, sep, remainder) = path.partition('/')

    if first_token == '':
        raise exception.Error('Invalid mini_xpath')

    results = []

    if items is None:
        return results

    if not isinstance(items, list):
        # Wrap single objects in a list
        items = [items]

    for item in items:
        if item is None:
            continue
        get_method = getattr(item, 'get', None)
        if get_method is None:
            continue
        child = get_method(first_token)
        if child is None:
            continue
        if isinstance(child, list):
            # Flatten intermediate lists
            for x in child:
                results.append(x)
        else:
            results.append(child)

    if not sep:
        # No more tokens
        return results
    else:
        return get_from_path(results, remainder)


def parse_server_string(server_str):
    """
    Parses the given server_string and returns a list of host and port.
    If it's not a combination of host part and port, the port element
    is a null string. If the input is invalid expression, return a null
    list.
    """
    try:
        if server_str.find(':') == -1:
            return (server_str, '')
        (address, port) = server_str.split(':')
        return (address, port)
    except Exception:
        LOG.debug(_('Invalid server_string: %s') % server_str)
        return ('', '')


def gen_uuid():
    return uuid.uuid4()


def is_uuid_like(val):
    """For our purposes, a UUID is a string in canonical form:
        aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa
    """
    try:
        uuid.UUID(val)
        return True
    except (TypeError, ValueError, AttributeError):
        return False


def bool_from_str(val):
    """Convert a string representation of a bool into a bool value"""

    if not val:
        return False
    try:
        return True if int(val) else False
    except ValueError:
        return val.lower() == 'true'


def is_valid_ipv4(address):
    return netaddr.valid_ipv4(address)


def is_valid_cidr(address):
    """Check if the provided ipv4 or ipv6 address is a valid
    CIDR address or not"""
    try:
        netaddr.IPNetwork(address)
    except netaddr.core.AddrFormatError:
        return False
    except UnboundLocalError:
        return False
    ip_segment = address.split('/')
    if (len(ip_segment) <= 1 or
            ip_segment[1] == ''):
        return False
    return True


def timefunc(func):
    """Decorator that logs how long a particular function took to execute"""
    @functools.wraps(func)
    def inner(*args, **kwargs):
        start_time = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            total_time = time.time() - start_time
            LOG.debug(_("timefunc: '%(name)s' took %(total_time).2f secs") %
                      dict(name=func.__name__, total_time=total_time))
    return inner


@contextlib.contextmanager
def save_and_reraise_exception():
    """Save current exception, run some code and then re-raise.

    In some cases the exception context can be cleared, resulting in None
    being attempted to be reraised after an exception handler is run. This
    can happen when eventlet switches greenthreads or when running an
    exception handler, code raises and catches an exception. In both
    cases the exception context will be cleared.

    To work around this, we save the exception state, run handler code, and
    then re-raise the original exception. If another exception occurs, the
    saved exception is logged and the new exception is reraised.
    """
    type_, value, traceback = sys.exc_info()
    try:
        yield
    except Exception:
        # NOTE(jkoelker): Using LOG.error here since it accepts exc_info
        #                 as a kwargs.
        LOG.error(_('Original exception being dropped'),
                  exc_info=(type_, value, traceback))
        raise
    raise type_, value, traceback


def read_cached_file(filename, cache_info, reload_func=None):
    """Read from a file if it has been modified.

    :param cache_info: dictionary to hold opaque cache.
    :param reload_func: optional function to be called with data when
                        file is reloaded due to a modification.

    :returns: data from file

    """
    mtime = os.path.getmtime(filename)
    if not cache_info or mtime != cache_info.get('mtime'):
        with open(filename) as fap:
            cache_info['data'] = fap.read()
        cache_info['mtime'] = mtime
        if reload_func:
            reload_func(cache_info['data'])
    return cache_info['data']


def hash_file(file_like_object):
    """Generate a hash for the contents of a file."""
    checksum = hashlib.sha1()
    any(map(checksum.update, iter(lambda: file_like_object.read(32768), '')))
    return checksum.hexdigest()


def read_file_as_root(file_path):
    """Secure helper to read file as root."""
    try:
        out, _err = execute('cat', file_path, run_as_root=True)
        return out
    except exception.ProcessExecutionError:
        raise exception.FileNotFound(file_path=file_path)


@contextlib.contextmanager
def tempdir(**kwargs):
    tmpdir = tempfile.mkdtemp(**kwargs)
    try:
        yield tmpdir
    finally:
        try:
            shutil.rmtree(tmpdir)
        except OSError as e:
            LOG.debug(_('Could not remove tmpdir: %s'), str(e))


class UndoManager(object):

    """Provides a mechanism to facilitate rolling back a series of actions
    when an exception is raised.
    """
    def __init__(self):
        self.undo_stack = []

    def undo_with(self, undo_func):
        self.undo_stack.append(undo_func)

    def _rollback(self):
        for undo_func in reversed(self.undo_stack):
            undo_func()

    def rollback_and_reraise(self, msg=None):
        """Rollback a series of actions then re-raise the exception.

        .. note:: (sirp) This should only be called within an
                  exception handler.
        """
        with save_and_reraise_exception():
            if msg:
                LOG.exception(msg)
            self._rollback()
