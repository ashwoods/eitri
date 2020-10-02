import asyncio
import os
import tempfile
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Type

import attr
import click
import click_pathlib
import faker
import yaml
from prompt_toolkit import HTML, PromptSession
from prompt_toolkit.application.current import get_app
from prompt_toolkit.patch_stdout import patch_stdout

from eitri.func import load_yaml

class Toolkit:
    pass


class WorkSpace:
    pass


class Environment:
    @property
    def env_path(self) -> Path:
        p = Path.home() / ".config" / "eitri" / "envs"
        p.mkdir(exist_ok=True)
        return p

    def boostrap(self):
        raise NotImplementedError

    def load_env(self, toolkit):
        """Dummy laod env"""
        return [d for d in self.env_path.iterdir()][0]


class ComposeSession(PromptSession):
    def __init__(self, workspace, toolkit, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.workspace = workspace
        self.toolkit = toolkit
        self.tmpdir = TemporaryDirectory()


        with self.compose_path.open("w") as f:
            yaml.dump(self.compose, f)

        self.preload()

    @property
    def dockerfile(self):
        return Path(__file__).parent / "templates" / "Dockerfile"

    @property
    def compose_path(self):
        return Path(self.tmpdir.name).joinpath("docker-compose.yml")

    @property
    def compose(self):
        origin = load_yaml(self.toolkit / "docker-compose.yaml")
        image = origin["services"]["entrypoint"]["image"]
        origin["services"]["entrypoint"]["build"] = {
            "context": str(self.workspace),
            "dockerfile": str(self.dockerfile),
            "args": {"IMAGE": image},
        }
        del origin["services"]["entrypoint"]["image"]
        return origin

    def preload(self):
        subprocess.run(["docker-compose", "-f", f"{self.toolkit / 'docker-compose.yaml'}", "pull"])  

    def get_bottom_toolbar(self):
        """Returns formatted bottom toolbar"""
        return HTML(f"<style bg='ansired'>Eitri </style> {self.toolkit}")

    async def update_toolbar(self):
        while True:
            # self.text = "hello %s" % self.faker.name()
            get_app().invalidate()
            await asyncio.sleep(5)

    async def runner(self, cmd):

        wrapper = f"docker-compose -f {self.compose_path} build"
        proc = await asyncio.create_subprocess_shell(
            wrapper, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.wait()

        wrapper = f"docker-compose -f {self.compose_path} run entrypoint /bin/bash -c '{cmd}'"
        proc = await asyncio.create_subprocess_shell(wrapper)
        await proc.wait()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        # todo: make sure all docker resources are also cleared
        self.tmpdir.__exit__(*args, **kwargs)


async def main(path, toolkit):
    help_text = "> "
    with ComposeSession(path, toolkit) as session:
        while True:
            with patch_stdout():
                result = await session.prompt_async(
                    help_text, bottom_toolbar=lambda: session.get_bottom_toolbar()
                )
                await session.runner(result)


@click.command()
@click.argument("workspace", type=click_pathlib.Path(exists=True), default=lambda: Path.cwd())
@click.option("-t", "--toolkit")
def run(workspace, toolkit):
    # load configuration or create default
    # load environments
    toolkit = Environment().load_env(toolkit)
    asyncio.run(main(workspace.absolute(), toolkit))
