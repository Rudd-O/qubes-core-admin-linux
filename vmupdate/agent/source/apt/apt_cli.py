# coding=utf-8
#
# The Qubes OS Project, http://www.qubes-os.org
#
# Copyright (C) 2022  Piotr Bartman <prbartman@invisiblethingslab.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.

# pylint: disable=unused-argument

import os
from typing import List

from source.common.package_manager import PackageManager
from source.common.process_result import ProcessResult


class APTCLI(PackageManager):
    def __init__(self, log_handler, log_level,):
        super().__init__(log_handler, log_level,)
        self.package_manager: str = "apt-get"

        # to prevent a warning: `debconf: unable to initialize frontend: Dialog`
        os.environ['DEBIAN_FRONTEND'] = 'noninteractive'

    def refresh(self, hard_fail: bool) -> ProcessResult:
        """
        Use package manager to refresh available packages.

        :param hard_fail: raise error if some repo is unavailable
        :return: (exit_code, stdout, stderr)
        """
        cmd = [self.package_manager, "-q", "update"]
        result = self.run_cmd(cmd)
        result.error_from_messages()
        return result

    def get_packages(self):
        """
        Use dpkg-query to return the installed packages and their versions.
        """
        cmd = [
            "dpkg-query",
            "--showformat",
            "${Status} ${Package} ${Version}\n",
            "-W",
        ]
        # EXAMPLE OUTPUT:
        # install ok installed qubes-core-agent 4.1.35-1+deb11u1
        result = self.run_cmd(cmd, realtime=False)

        packages = {}
        for line in result.out.splitlines():
            cols = line.split()
            selection, _flag, status, package, version = cols
            if selection in ("install", "hold") and status == "installed":
                packages.setdefault(package, []).append(version)

        return packages

    def get_action(self, remove_obsolete: bool) -> List[str]:
        """
        Return command `upgrade` or `dist-upgrade` if `remove_obsolete`.
        """
        return ["dist-upgrade"] if remove_obsolete else ["upgrade"]
