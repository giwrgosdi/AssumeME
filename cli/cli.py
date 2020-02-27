import click
from src.configure import ConfigureAwsAssumeRole
from src.utils import Utility
import src.helper as helper

from os.path import expanduser
import os
import yaml

class ConfigSetup(click.Group):
    def __init__(self, profile):
        u = Utility()
        helper_ = helper.Helper()
        self.profile = profile
        self.profile_config = u.read_configuration(self.profile)
        self.current_state = helper_.read_file('state')
        self.application_home_dir = expanduser("~/.assume")
        self.aws_creds_path=expanduser(self.profile_config['credentials'])
        self.aws_config_path=expanduser(self.profile_config['config'])
        self.aws_creds, self.aws_config = u.create_config_parsers([self.aws_creds_path, self.aws_config_path])

APPLICATION_HOME_DIR = expanduser("~/.assume")

@click.group()
@click.pass_context
def actions(ctx):
    pass







@actions.command(help="Configure a new profile with your prefered settings.")
@click.option('--set')
@click.option('--get')
@click.option('--add-profile')
@click.option('--delete-profile')
@click.pass_context
def config(ctx, set, get, add_profile, delete_profile):
    helper_ = helper.Helper()
    u = Utility()
    content = helper_read_file("state")
    if u.is_init():
        if content.get("profile"):
            profile_config = helper_.read_file("{}.prof".format(content["profile"]))
            if set:
                key, value = set.split('=')
                if key.strip() in profile_config.keys():
                    profile_config[key.strip()] = value.strip()
                    helper_.write_file("{}.prof".format(content["profile"]))
            elif get:
                if 'state' in get.strip():
                    u.print_message(helper_.read_file('state'))
                    state = helper_.read_file('state')
                    for k,v in state.items():
                        u.print_message("{}: {}".format(k,v))
                elif get in profile_config:
                    u.print_message("The value for {} is {}".format(get, profile_config[get]))
                else:
                    u.print_message("There is no attribute : {}".format(get))
            elif add_profile:
                user, role_and_account = add_profile.split(".")
                role, account = role_and_account.strip().split(':')
                if user.strip() in profile_config['credentials_profile']:
                    profile_config['credentials_profile'][user.strip()].update({role.strip(): account.strip()})
                    helper_.write_file("{}.prof".format(content["profile"]), profile_config)
                    u.print_message("New role `{}` added with account number `{}` for user `{}`".format(role, account, user))
                else:
                    profile_config['credentials_profile'][user.strip()] = {role.strip(): account.strip()}
                    helper_.write_file("{}.prof".format(content["profile"]), profile_config)
                    u.print_message("New user added `{}` with role `{}` and account number `{}`".format(user, role, account))
            elif delete_profile:
                if "." in delete_profile:
                    user, role = delete_profile.split(".")
                    del profile_config['credentials_profile'][user.strip()][role.strip()]
                    helper_.write_file("{}.prof".format(content["profile"]), profile_config)
                else:
                    del profile_config['credentials_profile'][delete_profile.strip()]
                    helper_.write_file("{}.prof".format(content["profile"]), profile_config)
        else:
            conf = u.configure()
            conf.create_config(conf.config)
    else:
        print("You need to initialize first.")

@actions.command(help="Initialise asm")
@click.pass_context
def init(ctx):
    u = Utility()
    if os.path.isdir(APPLICATION_HOME_DIR):
        directory = True
        if os.path.exists(f"{APPLICATION_HOME_DIR}/state"):
            state = True
        else:
            state = False
    else:
        directory = False
    
    if directory and state:
        print("Good news, `asm` is already initialised !")

    if not directory:
        u.create_directory(APPLICATION_HOME_DIR)
        u.create_file(APPLICATION_HOME_DIR, "state")
        state = True
        print("Initialization was successful..")
    if not state:
        u.create_file("state")


def main():
    actions()
