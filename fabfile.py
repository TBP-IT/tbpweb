from fabric import Config
from fabric import Connection
from fabric import task
from invoke import Collection
from invoke.config import merge_dicts

from deploy import git
from deploy import path

import argparse
from typing import Callable
import os

def timestamp(c: Connection) -> str:
    """
    Returns the server date-time, encoded as YYYYMMSS_HHMMSS.
    """
    return c.run("date +%Y%m%d_%H%M%S").stdout.strip()


def create_dirs(c: Connection):
    dirs = (
        c.repo_path,
        c.deploy_path,
        c.releases_path,
        c.shared_path,
        c.release_path,
    )
    for d in dirs:
        c.run(f"mkdir -p {d}")


class DeployConfig(Config):
    @staticmethod
    def global_defaults():
        tbp_defaults = {
            "deploy": {
                "name": "default",
                "user": "tbp",
                "host": "apphost.ocf.berkeley.edu",
                "conda_env": "tbpweb-prod",
                "run_blackbox_postdeploy": True,
                "path": {
                    "root": "/home/t/tb/tbp/tbpweb",
                    "repo": "repo",
                    "releases": "releases",
                    "current": "current",
                    "shared": "shared",
                },
                "repo_url": "https://github.com/TBP-IT/tbpweb.git",
                "branch": "master",
                "linked_files": [],
                "linked_dirs": [],
                "keep_releases": 10,
            },
        }
        return merge_dicts(Config.global_defaults(), tbp_defaults)


targets = {
    "prod": {
        "deploy": {
            "name": "prod",
            "branch": "master",
        },
    },
}

configs = {target: DeployConfig(overrides=config) for target, config in targets.items()}

# pprint(vars(configs['prod']))


def create_release(c: Connection):
    print("-- Creating release")
    git.check(c)
    git.update(c)
    c.commit = git.revision_number(c, c.commit)
    git.create_archive(c)


def symlink_shared(c: Connection):
    print("-- Symlinking shared files")
    with c.cd(c.release_path):
        c.run("ln -s {}/media ./media".format(c.shared_path), echo=True)
        c.run("ln -s {}/private-media ./private-media".format(c.shared_path), echo=True)


def decrypt_secrets(c):
    # print("-- Decrypting secrets")
    # with c.cd(c.release_path):
    #     c.run("blackbox_postdeploy", echo=True)
    print("-- Copying Secrets")
    with c.cd(c.release_path):
        c.run("cp ~/tbpweb_keys.py ./settings/tbpweb_keys.py", echo=True)


def django_migrate(c: Connection):
    print("-- Migrating tables")
    with c.cd(c.release_path):
        with c.prefix("conda activate tbpweb-prod"):
            c.run(f"python ./manage.py migrate")


def django_collectstatic(c: Connection):
    print("-- Collecting static files")
    with c.cd(c.release_path):
        with c.prefix("conda activate tbpweb-prod"):
            c.run(f"python ./manage.py collectstatic --noinput")


def symlink_release(c: Connection):
    print("-- Symlinking current@ to release")
    c.run("ln -sfn {} {}".format(c.release_path, c.current_path), echo=True)


def run_permission(c: Connection):
    print("-- Granting run file permission")
    c.run("chmod +x {}/run".format(c.current_path), echo=True)


def systemd_restart(c: Connection):
    print("-- Restarting systemd unit")
    c.run("systemctl --user restart tbpweb.service", echo=True)


def setup(c: Connection, commit=None, release=None):
    print("== Setup ==")
    if release is None:
        c.release = timestamp(c)
    else:
        c.release = release
    c.deploy_path = path.deploy_path(c)
    c.repo_path = path.repo_path(c)
    c.releases_path = path.releases_path(c)
    c.current_path = path.current_path(c)
    c.shared_path = path.shared_path(c)
    c.release_path = path.release_path(c)
    if commit is None:
        c.commit = c.deploy.branch
    else:
        c.commit = commit
    print("release: {}".format(c.release))
    print("commit: {}".format(c.commit))
    create_dirs(c)


def create_conda(c: Connection):
    print("-- Creating Conda Environment and Installing dependencies (Pip may take a while - about 15 mins, max 30 mins)")
    with c.cd(c.release_path):
        c.run("conda env create -f config/tbpweb-prod.yml")
        c.run("conda info -a")  # Print post-creation properties


def update_conda(c: Connection):
    print("-- Update Conda Environment and dependencies")
    with c.cd(c.release_path):
        # If this command fails due to not enough OCF resources at the time,
        #  ok to comment the line out
        c.run("conda env update -f config/tbpweb-prod.yml")
        c.run("conda info -a")  # Print post-creation properties


def activate_conda(c: Connection):
    c.run("conda activate tbpweb-prod")


def action_deploy(c: Connection, conda_action: Callable):
    create_release(c)
    symlink_shared(c)
    decrypt_secrets(c)
    conda_action(c)
    activate_conda(c)
    django_migrate(c)
    django_collectstatic(c)


def initial_scratch(c: Connection):
    print("== Initialize ==")
    action_deploy(c, create_conda)


def update(c: Connection):
    print("== Update ==")
    action_deploy(c, update_conda)


def publish(c: Connection):
    print("== Publish ==")
    symlink_release(c)
    run_permission(c)
    systemd_restart(c)


def finish(c):
    pass


@task
def deploy(c, commit=None):
    with Connection(c.deploy.host, user=c.deploy.user, config=c.config) as c:
        setup(c, commit=commit)
        update(c)
        publish(c)
        finish(c)


@task
def initialize(c, commit=None):
    with Connection(c.deploy.host, user=c.deploy.user, config=c.config) as c:
        setup(c, commit=commit)
        initial_scratch(c)
        publish(c)
        finish(c)


@task
def rollback(c, release=None):
    with Connection(c.deploy.host, user=c.deploy.user, config=c.config) as c:
        setup(c, release=release)
        update(c)
        publish(c)
        finish(c)

# Default mode is Prod
# Set a different target by setting the FAB_TARGET variable
tbpweb_mode = os.environ.get("FAB_TARGET", "prod")
if tbpweb_mode in ["dev", "prod"]:
    # Validation
    print("Target Set:", tbpweb_mode)
else:
    raise ValueError(f"TARGET '{tbpweb_mode}' is not a valid value")

ns = Collection(deploy, rollback, initialize)
ns.configure(configs[tbpweb_mode])
