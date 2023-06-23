import argparse

from dotenv import load_dotenv

from .common import (
    TerraformModuleIdentifier,
    generate_terraformrc,
    generate_token,
    init_root_logger,
    publish_module,
    release_module,
)
from .config import ApplicationConfig

__all__ = ["main"]


def main():
    """Main entry point."""
    init_root_logger()
    load_dotenv()
    config: ApplicationConfig = ApplicationConfig.lookup()

    parser = build_parser(config)

    args = parser.parse_args()
    if "func" in args:
        result = args.func(args)
        if result:
            print(result)
    else:
        parser.print_help()


def build_parser(config: ApplicationConfig):
    """Build arguments parser."""
    parser = argparse.ArgumentParser(prog="tfr", description="Manage terraform registry")
    subparsers = parser.add_subparsers(help='commands')

    for item in [_define_config, _define_generate, _define_terraformrc, _define_publish, _define_release]:
        item(subparsers, config)

    return parser


# mypy: disable-error-code="attr-defined"
def _define_config(subparsers, config: ApplicationConfig):
    parser = subparsers.add_parser('config', help='Show configuration parameters')
    parser.set_defaults(func=lambda args: config.show())

    # easter
    subparsers = parser.add_subparsers(help="")
    parser_mx = subparsers.add_parser('mx', help='have a break')

    def process_mx():
        # dynamic loading
        from .common.matrix import process_config_matrix

        process_config_matrix()

    parser_mx.set_defaults(func=lambda args: process_mx())


def _define_terraformrc(subparsers, config: ApplicationConfig):
    parser = subparsers.add_parser('generate-terraformrc', help='Generate terraformrc configuration file')
    parser.add_argument(
        "-output-directory",
        "--output-directory",
        action="store",
        type=str,
        help="output directory",
        required=True,
    )
    _add_weeks_arg(parser=parser)

    parser.set_defaults(
        func=lambda args: generate_terraformrc(
            config=config,
            output_directory=args.output_directory,
            weeks=args.weeks,
        )
    )


def _define_generate(subparsers, config: ApplicationConfig):
    parser = subparsers.add_parser('generate-token', help='Generate an access token')
    _add_weeks_arg(parser=parser)

    parser.set_defaults(func=lambda args: print(generate_token(config=config, weeks=args.weeks)))


def _define_publish(subparsers, config: ApplicationConfig):
    parser = subparsers.add_parser('publish', help='Publish a terraform module from custom source.')
    _add_common_terraform_module_args(parser=parser)
    parser.set_defaults(
        func=lambda args: publish_module(
            config=config,
            terraform_module=TerraformModuleIdentifier(
                namespace=args.namespace if args.namespace else config.default_namespace,
                name=args.name,
                system=args.system,
            ),
            version=args.version,
            source=args.source,
        )
    )


def _define_release(subparsers, config: ApplicationConfig):
    parser = subparsers.add_parser('release', help='Release a terraform module from custom source.')
    _add_common_terraform_module_args(parser=parser)
    parser.set_defaults(
        func=lambda args: release_module(
            config=config,
            terraform_module=TerraformModuleIdentifier(
                namespace=args.namespace if args.namespace else config.default_namespace,
                name=args.name,
                system=args.system,
            ),
            version=args.version,
            source=args.source,
        )
    )


def _add_weeks_arg(parser):
    parser.add_argument(
        "-weeks",
        "--weeks",
        action="store",
        type=int,
        help="#weeks of validity (52 per default)",
        default=52,
    )


def _add_common_terraform_module_args(parser):
    parser.add_argument(
        "-namespace", "--namespace", action="store", type=str, help="module namespace", required=False, default=None
    )
    parser.add_argument("-name", "--name", action="store", type=str, help="module name", required=True)
    parser.add_argument(
        "-system", "--system", action="store", type=str, help="module system (aws, azure, ...)", required=True
    )
    parser.add_argument("-version", "--version", action="store", type=str, help="module version", required=True)
    parser.add_argument("-source", "--source", action="store", type=str, help="module source", required=True)
