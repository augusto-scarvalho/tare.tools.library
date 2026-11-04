"""Operator configuration for SSH mesh tools; no machine-specific defaults."""

import os
import shlex
import subprocess


def ssh_target(host, user=None):
    """Let SSH use its own user configuration when no user is selected."""
    return f"{user}@{host}" if user else host


def remote_shell(command, wsl_distro=None):
    """Quote the command for the selected remote operating system."""
    if wsl_distro:
        return subprocess.list2cmdline(["wsl", "-d", wsl_distro, "--", "bash", "-lc", command])
    return "bash -lc " + shlex.quote(command)


def project_command(command, remote_root=None):
    """Run in the configured checkout or under the remote user's home."""
    root = remote_root or os.environ.get("TARE_MESH_REMOTE_ROOT")
    if root and root.startswith("~/"):
        directory = '"$HOME"/' + shlex.quote(root[2:])
    else:
        directory = shlex.quote(root) if root else '"$HOME/src/tare.tools.library"'
    return f"cd {directory} && {command}"
