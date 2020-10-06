import asyncio
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from tempfile import TemporaryDirectory
from timeit import default_timer as timer
from typing import Type

import attr
import click
import click_pathlib
import faker
import yaml
import json

from prompt_toolkit import HTML, PromptSession
from prompt_toolkit.application.current import get_app
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.patch_stdout import patch_stdout
from yaspin import yaspin

from eitri.func import load_yaml


class ToolKit:
    def __init__(self, path) -> None:
        self.path = path
        self.config = self.load_config()
        self.version = "0.1.0"
        self.name = "atuin-toolkit"

    def load_config(self) -> dict:
        config_path = self.path.joinpath("eitri.yaml")
        if config_path.exists():
            return load_yaml(config_path)
        else:
            return {}

    @property
    def absolute(self) -> str:
        return self.path.absolute()

    def __str__(self) -> str:
        return str(self.absolute)


class WorkSpace:
    def __init__(self, path) -> None:
        self.path = path
        self.config = self.load_config()

    @property
    def absolute(self) -> str:
        return self.path.absolute()

    def load_config(self) -> dict:
        config_path = self.path.joinpath(".eitri.yaml")
        if config_path.exists():
            return load_yaml(config_path)
        else:
            return {}

    def __str__(self) -> str:
        return str(self.absolute)


class Environment:

    def __init__(self):
        self.docker_context = self.get_docker_context()

    @property
    def env_path(self) -> Path:
        p = Path.home() / ".config" / "eitri" / "envs"
        p.mkdir(exist_ok=True)
        return p

    def boostrap(self):
        raise NotImplementedError

    def load_env(self, toolkit):
        """Dummy laod env"""
        return ToolKit([d for d in self.env_path.iterdir()][0])

    @property
    def docker_compose(self):
        return shutil.which("docker-compose")

    def get_docker_context(self):
        result = subprocess.run(['docker', 'context', 'inspect'], capture_output=True)
        return json.loads(result.stdout)[0]['Name']

class ComposeSession(PromptSession):
    def __init__(self, workspace, toolkit, env, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.workspace = workspace
        self.toolkit = toolkit
        self.env = env
        self.tmpdir = TemporaryDirectory()
        self.run_time = None
        self.build_time = None
        with self.compose_path.open("w") as f:
            yaml.dump(self.compose, f)

        self.preload()

    def get_time(self):
        if self.build_time and self.run_time:
            return HTML(f"({self.build_time:.5f} | {self.run_time:.5f})")
        else:
            return ""

    @property
    def dockerfile(self):
        return Path(__file__).parent / "templates" / "Dockerfile"

    @property
    def compose_path(self):
        return Path(self.tmpdir.name).joinpath("docker-compose.yml")

    @property
    def compose(self):
        origin = load_yaml(self.toolkit.absolute / "docker-compose.yaml")
        image = origin["services"]["entrypoint"]["image"]
        origin["services"]["entrypoint"]["build"] = {
            "context": str(self.workspace),
            "dockerfile": str(self.dockerfile),
            "args": {"IMAGE": image, "PRE_INSTALL": self.workspace.config.get("pre-install", "")},
        }
        del origin["services"]["entrypoint"]["image"]
        return origin

    def preload(self):
        with yaspin(text="Preloading toolkit..."):
            subprocess.run(["docker-compose", "-f", f"{self.toolkit.absolute / 'docker-compose.yaml'}", "pull"])

    def get_bottom_toolbar(self):
        """Returns formatted bottom toolbar"""
        return HTML(f"<title>  Eitri  </title><context> 🐋 {self.env.docker_context}  </context><toolkit style='bold'>  {self.toolkit.name}: {self.toolkit.version}  </toolkit><workspace> {self.workspace} </workspace>")
    
    def get_style(self):
        return Style.from_dict(
        {
            "bottom-toolbar": "#302b25 bg:#e4d4c8",
            "bottom-toolbar.text": "#302b25 bg:#e4d4c8",
            "title": '#302b25 bg:#b7ba53',
            "context": "#48413a bg:#b7ba53",
        }
    )

    async def update_toolbar(self):
        while True:
            get_app().invalidate()
            await asyncio.sleep(5)

    async def runner(self, cmd):
        
        # prebuild compose
        wrapper = f"docker-compose -f {self.compose_path} build"
        with yaspin(text="Building..."):
            start = timer()
            proc = await asyncio.create_subprocess_shell(
                wrapper, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await proc.wait()
            end = timer()
            self.build_time = end - start

        # run command in docker-compose environment
        start = timer()
        wrapper = f"docker-compose -f {self.compose_path} run entrypoint /bin/bash -c '{cmd}'"
        proc = await asyncio.create_subprocess_shell(wrapper)
        await proc.wait()
        end = timer()
        self.run_time = end - start

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        # todo: make sure all docker resources are also cleared
        self.tmpdir.__exit__(*args, **kwargs)


async def main(path, toolkit, env):
    help_text = "> "
    with ComposeSession(path, toolkit, env) as session:
        while True:
            with patch_stdout():
                result = await session.prompt_async(
                    help_text,
                    rprompt=session.get_time(),
                    bottom_toolbar=lambda: session.get_bottom_toolbar(),
                    auto_suggest=AutoSuggestFromHistory(),
                    style=session.get_style()
                )
                await session.runner(result)
