"""Command-line interface to the Enterprise Cloud 2.0 APIs"""

import getpass
import logging
import sys
import traceback
import os
import appdirs

from cliff import app
from cliff import command
from cliff import complete
from cliff import help
from oslo_utils import importutils
from oslo_utils import strutils

import eclcli
from eclcli.common import clientmanager
from eclcli.common import commandmanager
from eclcli.common import exceptions as exc
from eclcli.common import logs
from eclcli.common import timing
from eclcli.common import utils

from os_client_config import config as cloud_config

osprofiler_profiler = importutils.try_import("osprofiler.profiler")


DEFAULT_DOMAIN = 'default'

APPDIRS = appdirs.AppDirs('ecl', 'EnterpriseCloud', multipath=True)
CONFIG_HOME = APPDIRS.user_config_dir

UNIX_CONFIG_HOME = os.path.join(
    os.path.expanduser(os.path.join('~', '.config')), 'ecl')
UNIX_SITE_CONFIG_HOME = '/etc/ecl'

SITE_CONFIG_HOME = APPDIRS.site_config_dir

CONFIG_SEARCH_PATH = [
    os.getcwd(),
    CONFIG_HOME, UNIX_CONFIG_HOME,
    SITE_CONFIG_HOME, UNIX_SITE_CONFIG_HOME
]
YAML_SUFFIXES = ('.yaml', '.yml')
JSON_SUFFIXES = ('.json',)
CONFIG_FILES = [
    os.path.join(d, 'clouds' + s)
    for d in CONFIG_SEARCH_PATH
    for s in YAML_SUFFIXES + JSON_SUFFIXES
]


def prompt_for_password(prompt=None):
    """Prompt user for a password

    Prompt for a password if stdin is a tty.
    """

    if not prompt:
        prompt = 'Password: '
    pw = None
    # If stdin is a tty, try prompting for the password
    if hasattr(sys.stdin, 'isatty') and sys.stdin.isatty():
        # Check for Ctl-D
        try:
            pw = getpass.getpass(prompt)
        except EOFError:
            pass
    # No password because we did't have a tty or nothing was entered
    if not pw:
        raise exc.CommandError(
            "No password entered, or found via --os-password or OS_PASSWORD",
        )
    return pw


class ECLClient(app.App):

    CONSOLE_MESSAGE_FORMAT = '%(levelname)s: %(name)s %(message)s'

    log = logging.getLogger(__name__)
    timing_data = []

    def __init__(self):
        # Patch command.Command to add a default auth_required = True
        command.Command.auth_required = True

        # Some commands do not need authentication
        help.HelpCommand.auth_required = False
        complete.CompleteCommand.auth_required = False

        # Slight change to the meaning of --debug
        self.DEFAULT_DEBUG_VALUE = None
        self.DEFAULT_DEBUG_HELP = 'Set debug logging and traceback on errors.'

        super(ECLClient, self).__init__(
            description=__doc__.strip(),
            version=eclcli.__version__,
            command_manager=commandmanager.CommandManager('ecl.cli'),
            deferred_help=True)

        del self.command_manager.commands['complete']
        # del self.command_manager.commands['help']

        self.api_version = {}

        # Until we have command line arguments parsed, dump any stack traces
        self.dump_stack_trace = True

        # Assume TLS host certificate verification is enabled
        self.verify = True

        self.client_manager = None
        self.command_options = None

        self.do_profile = False

    def configure_logging(self):
        """Configure logging for the app."""
        self.log_configurator = logs.LogConfigurator(self.options)
        self.dump_stack_trace = self.log_configurator.dump_trace

    def run(self, argv):
        ret_val = 1
        self.command_options = argv
        try:
            ret_val = super(ECLClient, self).run(argv)
            return ret_val
        except Exception as e:
            if not logging.getLogger('').handlers:
                logging.basicConfig()
            if self.dump_stack_trace:
                self.log.error(traceback.format_exc())
            else:
                self.log.error('Exception raised: ' + str(e))

            return ret_val

        finally:
            self.log.info("END return value: %s", ret_val)

    def init_profile(self):
        self.do_profile = osprofiler_profiler and self.options.profile
        if self.do_profile:
            osprofiler_profiler.init(self.options.profile)

    def close_profile(self):
        if self.do_profile:
            trace_id = osprofiler_profiler.get().get_base_id()

            # NOTE(dbelova): let's use warning log level to see these messages
            # printed. In fact we can define custom log level here with value
            # bigger than most big default one (CRITICAL) or something like
            # that (PROFILE = 60 for instance), but not sure we need it here.
            self.log.warning("Trace ID: %s" % trace_id)
            self.log.warning("To display trace use next command:\n"
                             "osprofiler trace show --html %s " % trace_id)

    def run_subcommand(self, argv):
        self.init_profile()
        try:
            ret_value = super(ECLClient, self).run_subcommand(argv)
        finally:
            self.close_profile()
        return ret_value

    def interact(self):
        self.init_profile()
        try:
            ret_value = super(ECLClient, self).interact()
        finally:
            self.close_profile()
        return ret_value

    def build_option_parser(self, description, version):
        parser = super(ECLClient, self).build_option_parser(
            description,
            version)

        # service token auth argument
        parser.add_argument(
            '--os-cloud',
            metavar='<cloud-config-name>',
            dest='cloud',
            default=utils.env('OS_CLOUD'),
            help='Cloud name in clouds.yaml (Env: OS_CLOUD)',
        )
        # Global arguments
        # parser.add_argument(
        #     '--os-region-name',
        #     metavar='<auth-region-name>',
        #     dest='region_name',
        #     default=utils.env('OS_REGION_NAME'),
        #     help='Authentication region name (Env: OS_REGION_NAME)')
        # parser.add_argument(
        #     '--os-cacert',
        #     metavar='<ca-bundle-file>',
        #     dest='cacert',
        #     default=utils.env('OS_CACERT'),
        #     help='CA certificate bundle file (Env: OS_CACERT)')
        # verify_group = parser.add_mutually_exclusive_group()
        # verify_group.add_argument(
        #     '--verify',
        #     action='store_true',
        #     default=None,
        #     help='Verify server certificate (default)',
        # )
        # verify_group.add_argument(
        #     '--insecure',
        #     action='store_true',
        #     default=None,
        #     help='Disable server certificate verification',
        # )
        # parser.add_argument(
        #     '--os-default-domain',
        #     metavar='<auth-domain>',
        #     dest='default_domain',
        #     default=utils.env(
        #         'OS_DEFAULT_DOMAIN',
        #         default=DEFAULT_DOMAIN),
        #     help='Default domain ID, default=' +
        #          DEFAULT_DOMAIN +
        #          ' (Env: OS_DEFAULT_DOMAIN)')
        # parser.add_argument(
        #     '--os-interface',
        #     metavar='<interface>',
        #     dest='interface',
        #     choices=['admin', 'public', 'internal'],
        #     default=utils.env('OS_INTERFACE'),
        #     help='Select an interface type.'
        #          ' Valid interface types: [admin, public, internal].'
        #          ' (Env: OS_INTERFACE)')
        # parser.add_argument(
        #     '--timing',
        #     default=False,
        #     action='store_true',
        #     help="Print API call timing info",
        # )

        # osprofiler HMAC key argument
        # if osprofiler_profiler:
        #     parser.add_argument('--profile',
        #                         metavar='hmac-key',
        #                         help='HMAC key to use for encrypting context '
        #                         'data for performance profiling of operation. '
        #                         'This key should be the value of one of the '
        #                         'HMAC keys configured in osprofiler '
        #                         'middleware in the projects user would like '
        #                         'to profile. It needs to be specified in '
        #                         'configuration files of the required '
        #                         'projects.')

        return clientmanager.build_plugin_option_parser(parser)

    def initialize_app(self, argv):
        """Global app init bits:

        * set up API versions
        * validate authentication info
        * authenticate against Identity if requested
        """

        # Parent __init__ parses argv into self.options
        super(ECLClient, self).initialize_app(argv)
        self.log.info("START with options: %s",
                      strutils.mask_password(self.command_options))
        self.log.debug("options: %s",
                       strutils.mask_password(self.options))

        # Set the default plugin to token_endpoint if url and token are given
        # if (self.options.url and self.options.token):
            # Use service token authentication
            # auth_type = 'token_endpoint'
        # else:
            # auth_type = 'password'
        auth_type = 'password'

        project_id = getattr(self.options, 'project_id', None)
        project_name = getattr(self.options, 'project_name', None)
        tenant_id = getattr(self.options, 'tenant_id', None)
        tenant_name = getattr(self.options, 'tenant_name', None)

        # handle some v2/v3 authentication inconsistencies by just acting like
        # both the project and tenant information are both present. This can
        # go away if we stop registering all the argparse options together.
        if project_id and not tenant_id:
            self.options.tenant_id = project_id
        if project_name and not tenant_name:
            self.options.tenant_name = project_name
        if tenant_id and not project_id:
            self.options.project_id = tenant_id
        if tenant_name and not project_name:
            self.options.project_name = tenant_name

        # Do configuration file handling
        # Ignore the default value of interface. Only if it is set later
        # will it be used.
        try:
            cc = cloud_config.OpenStackConfig(
                config_files=CONFIG_FILES,
                override_defaults={
                    'interface': None,
                    'auth_type': auth_type,
                },
            )
        except (IOError, OSError) as e:
            self.log.critical("Could not read clouds.yaml configuration file")
            self.print_help_if_requested()
            raise e

        # TODO(thowe): Change cliff so the default value for debug
        # can be set to None.
        if not self.options.debug:
            self.options.debug = None
        self.cloud = cc.get_one_cloud(
            cloud=self.options.cloud,
            argparse=self.options,
        )

        self.log_configurator.configure(self.cloud)
        self.dump_stack_trace = self.log_configurator.dump_trace
        self.log.debug("defaults: %s", cc.defaults)
        self.log.debug("cloud cfg: %s",
                       strutils.mask_password(self.cloud.config))

        # Set up client TLS
        # NOTE(dtroyer): --insecure is the non-default condition that
        #                overrides any verify setting in clouds.yaml
        #                so check it first, then fall back to any verify
        #                setting provided.
        self.verify = not self.cloud.config.get(
            'insecure',
            not self.cloud.config.get('verify', True),
        )

        # NOTE(dtroyer): Per bug https://bugs.launchpad.net/bugs/1447784
        #                --insecure now overrides any --os-cacert setting,
        #                where before --insecure was ignored if --os-cacert
        #                was set.
        if self.verify and self.cloud.cacert:
            self.verify = self.cloud.cacert

        # Save default domain
        # self.default_domain = self.options.default_domain
        self.default_domain = DEFAULT_DOMAIN

        # Loop through extensions to get API versions
        for mod in clientmanager.PLUGIN_MODULES:
            default_version = getattr(mod, 'DEFAULT_API_VERSION', None)
            option = mod.API_VERSION_OPTION.replace('os_', '')
            version_opt = str(self.cloud.config.get(option, default_version))
            if version_opt:
                api = mod.API_NAME
                self.api_version[api] = version_opt

                # Add a plugin interface to let the module validate the version
                # requested by the user
                skip_old_check = False
                mod_check_api_version = getattr(mod, 'check_api_version', None)
                if mod_check_api_version:
                    # this throws an exception if invalid
                    skip_old_check = mod_check_api_version(version_opt)

                mod_versions = getattr(mod, 'API_VERSIONS', None)
                if not skip_old_check and mod_versions:
                    if version_opt not in mod_versions:
                        self.log.warning(
                            "%s version %s is not in supported versions %s"
                            % (api, version_opt,
                               ', '.join(mod.API_VERSIONS.keys())))

                # Command groups deal only with major versions
                version = '.v' + version_opt.replace('.', '_').split('_')[0]
                cmd_group = 'ecl.' + api.replace('-', '_') + version
                self.command_manager.add_command_group(cmd_group)
                self.log.debug(
                    '%(name)s API version %(version)s, cmd group %(group)s',
                    {'name': api, 'version': version_opt, 'group': cmd_group}
                )

        # Commands that span multiple APIs
        self.command_manager.add_command_group(
            'ecl.common')

        self.command_manager.add_command_group(
            'ecl.extension')
        # call InitializeXxx() here
        # set up additional clients to stuff in to client_manager??

        # Handle deferred help and exit
        self.print_help_if_requested()

        self.client_manager = clientmanager.ClientManager(
            cli_options=self.cloud,
            verify=self.verify,
            api_version=self.api_version,
            pw_func=prompt_for_password,
        )

    def prepare_to_run_command(self, cmd):
        """Set up auth and API versions"""
        self.log.info(
            'command: %s -> %s.%s',
            getattr(cmd, 'cmd_name', '<none>'),
            cmd.__class__.__module__,
            cmd.__class__.__name__,
        )
        if cmd.auth_required:
            if hasattr(cmd, 'required_scope'):
                # let the command decide whether we need a scoped token
                self.client_manager.setup_auth(cmd.required_scope)
            # Trigger the Identity client to initialize
            self.client_manager.auth_ref
        return

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s: %s', cmd.__class__.__name__, err or '')

        # Process collected timing data
        # if self.options.timing:
            # Get session data
            # self.timing_data.extend(
            #     self.client_manager.session.get_timings(),
            # )

            # Use the Timing pseudo-command to generate the output
            # tcmd = timing.Timing(self, self.options)
            # tparser = tcmd.get_parser('Timing')

            # If anything other than prettytable is specified, force csv
            # format = 'table'
            # Check the formatter used in the actual command
            # if hasattr(cmd, 'formatter') \
            #         and cmd.formatter != cmd._formatter_plugins['table'].obj:
            #     format = 'csv'

            # sys.stdout.write('\n')
            # targs = tparser.parse_args(['-f', format])
            # tcmd.run(targs)


def main(argv=sys.argv[1:]):
    return ECLClient().run(argv)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
