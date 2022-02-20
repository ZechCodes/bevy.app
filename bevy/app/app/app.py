from bevy import AutoInject, Context, detect_dependencies
from bevy.args import CLIArgs
from bevy.app.launch_args import launch_parser
from bevy.options import Options
from typing import Sequence


@detect_dependencies
class App(AutoInject):
    options: Options

    def launch(self):
        workflow = self._load_workflow()
        workflow.run()

    def _load_workflow(self):
        self.options.add_using_arg_parser(launch_parser)
        self.options["workflow"]

    @classmethod
    def create(
        cls, *, cli_args: Sequence[str] | None = None, context: Context | None = None
    ):
        context = (
            Context.new(context)
            << CLIArgs(cli_args)
            << Options @ Context
            << cls @ Context
        )
        (cls << context).launch()
