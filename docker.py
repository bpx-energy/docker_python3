""" -*- coding: utf-8 -*- """

import os
import sys
from subprocess import Popen, PIPE

sys.dont_write_bytecode = True


class Docker(object):
    def __init__(self, name, dockerfile):
        self.name = name  # foo/bar:1.0
        self.dockerfile = dockerfile  # /path/to/Dockerfile
        self.context = None  # /path/to/
        self.volumes = []  # run ... --volume=/outside/path:/inside/path
        self.ports = []  # run ... --publish=8080:80
        self.hostname = None  # run ... --hostname=foo
        self.run_name = None  # run ... --name=foo
        self.build_rm = False  # build ... --force-rm=true
        self.run_rm = False  # run ... --rm=true
        self.detach = False  # --detach
        self.tty = False  # --tty
        self.interactive = False  # --interactive
        self.entrypoint = None
        self.extra_args = None  # $@ as str()
        self.build_log = None  # Result of successful `docker build ...`
        self.last_command = None  # proc spool
        self.cmd = '/usr/bin/docker'

    def build(self):
        arguments = ['build']
        if self.build_rm:
            arguments.append('--force-rm=true')
        arguments.append('--file={0}'.format(os.path.realpath(self.dockerfile)))
        arguments.append('--tag={0}'.format(self.name))
        if not self.context:
            self.context = os.path.dirname(os.path.realpath(self.dockerfile))
        arguments.append(self.context)
        self.build_log = self._do(arguments, stdout=PIPE, stderr=PIPE)

    def run(self):
        arguments = ['run']
        if self.hostname:
            arguments.append('--hostname={0}'.format(self.hostname))
        if self.run_name:
            arguments.append('--name={0}'.format(self.run_name))
        if self.run_rm:
            arguments.append('--rm=true')
        if self.ports:
            for port in self.ports:
                arguments.append('--publish={0}'.format(port))
        if self.volumes:
            for volume in self.volumes:
                arguments.append('--volume={0}'.format(volume))
        if self.tty:
            arguments.append('--tty')
        if self.interactive:
            arguments.append('--interactive')
        if self.entrypoint:
            arguments.append('--entrypoint={0}'.format(self.entrypoint))
        arguments.append(self.name)
        if self.extra_args:
            arguments.append(self.extra_args)
        self._do(arguments)

    def _do(self, this, timeout=None, stdout=None, stderr=None):
        standard_out = ''
        standard_err = ''
        command_list = [self.cmd] + this
        self.last_command = command_list
        try:
            cmd0 = Popen(command_list, stdout=stdout, stderr=stderr)
        except:
            print(command_list)
            raise
        try:
            outs, errs = cmd0.communicate(timeout=timeout)
        except TimeoutError:
            cmd0.kill()
            raise
        if outs:
            standard_out = outs.decode('utf-8')
        if errs:
            standard_err = errs.decode('utf-8')
        if cmd0.returncode == 0:
            return standard_out
        error = '{0}\n{1}'.format(cmd0.args, standard_err)
        raise self.ExecuteError(error)

    class ExecuteError(Exception):
        pass
