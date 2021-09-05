"""Project file for x264."""
import typing as tp

import benchbuild as bb
from benchbuild.utils.cmd import make
from benchbuild.utils.settings import get_number_of_jobs
from plumbum import local

from varats.paper_mgmt.paper_config import project_filter_generator
from varats.project.project_domain import ProjectDomains
from varats.project.project_util import (
    get_all_revisions_between,
    wrap_paths_to_binaries,
    ProjectBinaryWrapper,
    get_local_project_git_path,
    BinaryType,
    verify_binaries,
)
from varats.project.varats_project import VProject
from varats.utils.git_util import ShortCommitHash
from varats.utils.settings import bb_cfg


class X264(VProject):
    """Video encoder x264 (fetched by Git)"""

    NAME = 'x264'
    GROUP = 'c_projects'
    DOMAIN = ProjectDomains.CODEC

    SOURCE = [
        bb.source.Git(
            remote="https://code.videolan.org/videolan/x264.git",
            local="x264",
            refspec="HEAD",
            limit=None,
            shallow=False,
            version_filter=project_filter_generator("x264")
        )
    ]

    @staticmethod
    def binaries_for_revision(
        revision: ShortCommitHash  # pylint: disable=W0613
    ) -> tp.List[ProjectBinaryWrapper]:
        return wrap_paths_to_binaries([("x264", BinaryType.EXECUTABLE)])

    def run_tests(self) -> None:
        pass

    def compile(self) -> None:
        """Compile the project."""
        x264_git_path = get_local_project_git_path(self.NAME)
        x264_version_source = local.path(self.source_of_primary)
        x264_version = self.version_of_primary

        with local.cwd(x264_git_path):
            old_revisions = get_all_revisions_between(
                "5dc0aae2f900064d1f58579929a2285ab289a436",
                "290de9638e5364c37316010ac648a6c959f6dd26"
            )

        if x264_version in old_revisions:
            self.cflags += ["-fPIC"]

        clang = bb.compiler.cc(self)
        with local.cwd(x264_version_source):
            with local.env(CC=str(clang)):
                bb.watch(local["./configure"])("--disable-asm")
            bb.watch(make)("-j", get_number_of_jobs(bb_cfg()))

            verify_binaries(self)
