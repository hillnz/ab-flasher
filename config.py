#!/usr/bin/env python3

import logging
import os
from os import listdir, makedirs

from pydantic.main import BaseModel

try:
    import typer
    from pydantic import BaseSettings, Field
except:
    print('You need to install dependencies with poetry.')
    print('i.e. poetry install')
    print('Then run in the virtualenv, e.g. poetry run ./config.py')
    exit(1)

def strip(doc: str):
    return '\n'.join([ l.strip() for l in doc.split('\n') ])

class Variables(BaseSettings):

    final_image: str = Field(..., description=strip("""\
        URL to an OS partition image to be flashed by ab-flasher"""))
    
    ssh_key: str = Field(None, description=strip("""\
        If set, RPi will have this SSH public key loaded and SSH enabled."""))

    ssh_ca_key: str = Field(None, description=strip("""\
        If set, RPi's SSH host key will be signed with this CA key. Not kept.
        You probably shouldn't save this secret here. Maybe pass as an env var instead.
        (not implemented yet)"""))

    wifi_country: str = 'NZ'

    wifi_ssid: str = Field(None, description=strip("""\
        If set, RPi will be configured to use this WiFi after configuration (i.e. to download the final image)"""))

    wifi_password: str = Field(None, description=strip("""\
        See WIFI_SSID.
        You probably shouldn't save this secret here. Maybe pass as an env var instead."""))

    class Config:
        env_prefix = 'RPI_'
        env_file = '.env'


log = logging.getLogger('config')
logging.basicConfig(level='INFO')

CONFIG_FLAG = '.configure_me'

def get_mounts():
    # macos
    try:
        return [ f'/Volumes/{d}' for d in listdir('/Volumes') ]
    except FileNotFoundError:
        pass
    # linux
    try:
        with open('/proc/mounts') as f:
            return [ m.split()[1] for m in f.readlines() ]
    except FileNotFoundError:
        pass
    raise Exception("Couldn't list mounts. Maybe you're on Windows (not implemented)")
    
def find_data_mount():
    for mount in get_mounts():
        flag_file = os.path.join(mount, CONFIG_FLAG)
        try:
            with open(flag_file, 'r') as _:
                pass
        except:
            continue
        return mount
    raise Exception("Couldn't find the flashed drive. Maybe it's already configured")

def make_supplicant(country, ssid, pw):
    return f"""ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country={country}

network={{
 ssid="{ssid}"
 psk="{pw}"
}}
"""

def main(recreate_dotenv: bool=False):
    if not os.path.isfile('.env') or recreate_dotenv:
        log.warning('Creating .env file. Fill it in, then re-run.')

        properties = Variables.schema()['properties']
        vars = Variables(final_image='<url_to_image>')

        with open('.env', 'w') as f:
            f.write(strip("""\
                # Fill these in then run ./config.py
                # You can also set any of these as environment variables instead.
                
                """))
            for var_name, var in properties.items():
                if 'description' in var:
                    desc = var['description']
                    f.write('\n'.join([ f'# {l}' for l in desc.split('\n') ]))
                    f.write('\n')
                f.write(f'{next(iter(var["env_names"])).upper()}={getattr(vars, var_name) or ""}')
                f.write('\n\n')
        return

    vars = Variables()
    data_mount = find_data_mount()
    def make_data_dir(name):
        dir = os.path.join(data_mount, name)
        makedirs(dir, exist_ok=True)
        return dir

    # SSH
    if vars.ssh_key:
        log.info('Configuring ssh')
        ssh_dir = make_data_dir('ssh')
        with open(os.path.join(ssh_dir, 'authorized_keys'), 'w') as f:
            f.write(vars.ssh_key + '\n')

    # WiFi
    if vars.wifi_ssid:
        log.info('Configuring wifi')
        wifi_dir = make_data_dir('wifi')
        with open(os.path.join(wifi_dir, 'wpa_supplicant.conf'), 'w') as f:
            f.write(make_supplicant(vars.wifi_country, vars.wifi_ssid, vars.wifi_password))

    # ab-flasher
    log.info('Configuring ab-flasher')
    with open(os.path.join(data_mount, 'ab-flasher.env'), 'w') as f:
        f.write(f'AB_OS_IMAGE_URL={vars.final_image}\n')
        f.write('AB_FORCE=true\n')
        f.write('AB_VERBOSE=1\n')

    flag_file = os.path.join(data_mount, CONFIG_FLAG)
    os.remove(flag_file)

    log.info('Configuration completed')

if __name__ == '__main__':
    typer.run(main)
