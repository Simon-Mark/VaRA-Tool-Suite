"""
Project file for tmux.
"""
from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.cmd import make
from benchbuild.utils.compiler import cc
from benchbuild.utils.download import with_git
from benchbuild.utils.run import run

from plumbum import local

from varats.paper.paper_config import project_filter_generator


@with_git(
    "https://github.com/tmux/tmux.git",
    refspec="HEAD",
    version_filter=project_filter_generator("tmux"))
class Tmux(Project):  # type: ignore
    """ Terminal multiplexer Tmux """

    NAME = 'tmux'
    GROUP = 'c_projects'
    DOMAIN = 'UNIX utils'
    VERSION = 'HEAD'

    BIN_NAMES = ['tmux']
    SRC_FILE = NAME + "-{0}".format(VERSION)

    def run_tests(self, runner: run) -> None:
        pass

    def compile(self) -> None:
        self.download()

        clang = cc(self)
        with local.cwd(self.SRC_FILE):
            with local.env(CC=str(clang)):
                run(local["./autogen.sh"])
                run(local["./configure"])
            run(make["-j", int(CFG["jobs"])])
