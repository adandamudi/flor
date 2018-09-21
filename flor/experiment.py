#!/usr/bin/env python3

import os
import inspect

import flor.global_state as global_state
import flor.util as util
import flor.above_ground as ag
from flor.jground import GroundClient
from flor.object_model import *
from flor.experiment_graph import ExperimentGraph
from flor.stateful import State
from flor.data_controller.versioner import Versioner

from datetime import datetime
from ground.client import GroundClient
from grit.client import GroundClient as GritClient
import requests


class Experiment(object):

    def __init__(self, name, backend="git"):
        self.xp_state = State()
        self.xp_state.EXPERIMENT_NAME = name
        self.xp_state.eg = ExperimentGraph()

        if not global_state.interactive:
            # https://stackoverflow.com/a/13699329/9420936
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            filename = module.__file__
            if not global_state.interactive:
                target_dir = '/'.join(filename.split('/')[0:-1])
                if target_dir:
                    os.chdir(target_dir)

        backend = backend.lower().strip()
        if backend == "ground":
            ######################### GROUND GROUND GROUND ###################################################
            # Is Ground Server initialized?
            # Localhost hardcoded into the url
            try:
                requests.get('http://localhost:9000')
            except:
                # No, Ground not initialized
                raise requests.exceptions.ConnectionError('Please start Ground first')
            ######################### </> GROUND GROUND GROUND ###################################################
            self.xp_state.gc = GroundClient()
        elif backend == "git":
            self.xp_state.gc = GritClient()
        else:
            raise ModuleNotFoundError("Only 'git' or 'ground' backends supported, but '{}' entered".format(backend))

    def __enter__(self):
        return self

    def __exit__(self, typ=None, value=None, traceback=None):
        self.xp_state.eg.serialize()
        version = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        Versioner(version, self.xp_state.eg, self.xp_state).save_commit_event()
        ag.CommitTracker(self.xp_state).commit()
        self.xp_state.eg.clean()

    def groundClient(self, backend):
        """
        Keeping for backward compatibility. Will clean up.
        :param backend:
        :return:
        """
        pass

    def literal(self, v=None, name=None, parent=None, version=None):
        """
        TODO: support version
        :param v:
        :param name:
        :param parent:
        :return:
        """
        if v is None and parent is None:
            raise ValueError("The value or the parent of the literal must be set")
        if v is not None and parent is not None:
            raise ValueError("A literal with a value may not have a parent")
        lit = Literal(v, name, parent, self.xp_state, default=None, version=version)
        self.xp_state.eg.node(lit)

        if parent:
            self.xp_state.eg.edge(parent, lit)

        return lit

    def literalForEach(self, v=None, name=None, parent=None, default=None, version=None):
        """
        TODO: Support version
        :param v:
        :param name:
        :param parent:
        :param default:
        :return:
        """
        if v is None and parent is None:
            raise ValueError("The value or the parent of the literal must be set")
        if v is not None and parent is not None:
            raise ValueError("A literal with a value may not have a parent")
        lit = Literal(v, name, parent, self.xp_state, default, version=version)
        self.xp_state.eg.node(lit)
        lit.__forEach__()

        if parent:
            self.xp_state.eg.edge(parent, lit)

        return lit

    def artifact(self, loc, name, parent=None, version=None):
        """

        :param loc:
        :param name:
        :param parent:
        :param version:
        :return:
        """
        art = Artifact(loc, parent, name, version, self.xp_state)
        self.xp_state.eg.node(art)

        if parent:
            self.xp_state.eg.edge(parent, art)

        return art

    def action(self, func, in_artifacts=None):
        """
        # TODO: What's the equivalent of re-using code from a previous experiment version?

        :param func:
        :param in_artifacts:
        :return:
        """
        filenameWithFunc, _, _ = func

        if filenameWithFunc in self.xp_state.eg.loc_map:
            code_artifact = self.xp_state.eg.loc_map[filenameWithFunc]
        else:
            code_artifact = self.artifact(filenameWithFunc, filenameWithFunc.split('.')[0])

        if in_artifacts:
            temp_artifacts = []
            for in_art in in_artifacts:
                if not util.isFlorClass(in_art):
                    if util.isIterable(in_art):
                        in_art = self.literal(in_art)
                        in_art.__forEach__()
                    else:
                        in_art = self.literal(in_art)
                temp_artifacts.append(in_art)
            in_artifacts = temp_artifacts

        in_artifacts = in_artifacts or []

        act = Action(func, [code_artifact, ] + in_artifacts, self.xp_state)
        self.xp_state.eg.node(act)
        self.xp_state.eg.edge(code_artifact, act)
        if in_artifacts:
            for in_art in in_artifacts:
                self.xp_state.eg.edge(in_art, act)

        return act

    # def plate(self, name):
    #     return Plate(self, name)

# class Plate:
#
#     def __init__(self, experiment, name):
#         self.experiment = experiment
#         self.name = name + '.pkl'
#         self.artifacts = []
#
#     def artifact(self, loc, parent=None, manifest=False):
#         artifact = self.experiment.artifact(loc, parent, manifest)
#         self.artifacts.append(artifact)
#         return artifact
#
#     def action(self, func, in_artifacts=None):
#         return self.experiment.action(func, in_artifacts)
#
#     def exit(self):
#
#         @func
#         def plate_aggregate(*args):
#             original_dir = os.getcwd()
#             os.chdir(self.experiment.xp_state.tmpexperiment)
#             dirs = [x for x in os.listdir() if util.isNumber(x)]
#             table = []
#
#             # NOTE: Use the flor.Experiment experimentName in the future
#             experimentName = self.experiment.xp_state.florFile.split('.')[0]
#
#             literalNames = self.experiment.xp_state.ray['literalNames']
#
#             for trial in dirs:
#                 os.chdir(trial)
#                 with open('.' + experimentName + '.flor', 'r') as fp:
#                     config = json.load(fp)
#                 record = {}
#                 for literalName in literalNames:
#                     record[literalName] = config[literalName]
#                 for artifact in self.artifacts:
#                     while True:
#                         try:
#                             # I need to wait for every to finish. not just this one.
#                             record[artifact.loc.split('.')[0]] = util.loadArtifact(artifact.loc)
#                             break
#                         except:
#                             time.sleep(5)
#                     if util.isNumber(record[artifact.loc.split('.')[0]]):
#                         record[artifact.loc.split('.')[0]] = eval(record[artifact.loc.split('.')[0]])
#                 table.append(record)
#                 os.chdir('../')
#
#             os.chdir(original_dir)
#
#             return pd.DataFrame(table)
#
#         plate_aggregate = (self.experiment.xp_state.florFile, plate_aggregate[1], plate_aggregate[2])
#
#         do_action = self.experiment.action(plate_aggregate, self.artifacts)
#         artifact_df = self.experiment.artifact(self.name, do_action)
#
#         return artifact_df
#
