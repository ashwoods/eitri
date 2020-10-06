import click
import click_pathlib
import asyncio

from pathlib import Path

from eitri.core import WorkSpace, Environment, ToolKit
from eitri.core import main

@click.group()
@click.pass_context
def cli(ctx, **kwargs):
    """Eitri is a prompt tool that wraps cli commands and runs them in a docker context"""
    if ctx.obj is None:
        ctx.obj = {}

@cli.command()
@click.argument("workspace", type=click_pathlib.Path(exists=True), default=lambda: Path.cwd(),)
@click.option("-t", "--toolkit", type=str, help="Toolkit name")
def run(workspace, toolkit):
    """
    Run a toolkit session on WORKSPACE
    """

    workspace = WorkSpace(workspace)
    env = Environment()
    toolkit = env.load_env(toolkit) 
    asyncio.run(main(workspace, toolkit, env))

@cli.command(help="Add a toolkit")
@click.argument("toolkit", type=click_pathlib.Path(exists=True), default=lambda: Path.cwd())
@click.argument("name", type=str)
def add(toolkit, name):
    pass

@cli.command(help="Remove a toolkit")
@click.argument("name", type=str)
def rm():
    pass

@cli.command(help="List toolkits")
def ls():
    pass

