"""Project file for libvpx."""
import typing as tp

import benchbuild as bb
from benchbuild.utils.cmd import make
from benchbuild.utils.settings import get_number_of_jobs
from plumbum import local

from varats.data.provider.cve.cve_provider import CVEProviderHook
from varats.paper.paper_config import project_filter_generator
from varats.utils.project_util import (
    wrap_paths_to_binaries,
    ProjectBinaryWrapper,
)
from varats.utils.settings import bb_cfg


class Libvpx(bb.Project, CVEProviderHook):  # type: ignore
    """Codec SDK libvpx (fetched by Git)"""

    NAME = 'libvpx'
    GROUP = 'c_projects'
    DOMAIN = 'codec'

    SOURCE = [
        bb.source.Git(
            remote="https://github.com/webmproject/libvpx.git",
            local="libvpx",
            refspec="HEAD",
            limit=None,
            shallow=False,
            version_filter=project_filter_generator("libvpx")
        )
    ]

    @property
    def binaries(self) -> tp.List[ProjectBinaryWrapper]:
        """Return a list of binaries generated by the project."""
        return wrap_paths_to_binaries(["vpxdec", "vpxenc"])

    def run_tests(self) -> None:
        pass

    def compile(self) -> None:
        """Compile the project."""
        libvpx_source = bb.path(self.source_of_primary)

        self.cflags += ["-fPIC"]

        clang = bb.compiler.cc(self)
        with local.cwd(libvpx_source):
            with local.env(CC=str(clang)):
                bb.watch(local["./configure"])()
            bb.watch(make)("-j", get_number_of_jobs(bb_cfg()))

    @classmethod
    def get_cve_product_info(cls) -> tp.List[tp.Tuple[str, str]]:
        return [("john_koleszar", "libvpx")]