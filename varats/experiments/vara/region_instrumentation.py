"""Experiment that adds tracing markers for highlight regions."""
import typing as tp

from benchbuild import Experiment, Project
from benchbuild.extensions import compiler, run, time
from benchbuild.utils.actions import Step

from varats.experiments.wllvm import RunWLLVM


class RegionAnalyser(Experiment):  # type: ignore
    """Small region instrumentation experiment to test vara tracer."""

    NAME = "RegionAnalyser"

    def actions_for_project(self, project: Project) -> tp.List[Step]:
        project.runtime_extension = run.RuntimeExtension(project, self
                                                        ) << time.RunWithTime()

        project.compiler_extension = compiler.RunCompiler(
            project, self
        ) << RunWLLVM() << time.RunWithTime()

        project.ldflags = ["-lTrace"]
        project.cflags = ["-fvara-handleRM=High", "-mllvm", "-vara-tracer"]

        actns: tp.List[Step] = self.default_runtime_actions(project)
        return actns