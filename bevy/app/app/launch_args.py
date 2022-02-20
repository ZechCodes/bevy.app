from bevy.args import ArgumentParser
from bevy.options import Options


launch_parser = ArgumentParser()

launch_parser.add_argument(
    "--workflow",
    "-w",
    default="app.workflow.json",
    help="The full path to the app workflow file.",
)

launch_parser.add_argument(
    "--path",
    "-p",
    dest=Options.path_key,
    help="The folder that the app should work from.",
)
