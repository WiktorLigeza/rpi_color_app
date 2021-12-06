import json
import os
import subprocess
from configparser import ConfigParser as cfg
import platform
from tempfile import NamedTemporaryFile
from os import system
import pathlib
import sys
from passlib.hash import sha256_crypt


def get_configs(obj):
    try:
        file = 'config.ini'
        print("reading configs from: ", os.path.join(obj.global_path, "configs", file))
        config = cfg()
        config.read(os.path.join(obj.global_path, "configs", file))

        # ge credentials
        obj.rPi_TAG = config['device']['TAG']
        obj.secret_key = config['device']['secret_key']
        obj.url = config['server']['url']

        obj.pm.R_pin = int(config['GPIO']['R'])
        obj.pm.G_pin = int(config['GPIO']['G'])
        obj.pm.B_pin = int(config['GPIO']['B'])

        if obj.rPi_TAG == '' or obj.secret_key == '':
            login(obj)
        print("USING:\n    TAG: {}\n    secret_key: {}\n    server url: {}\n    GPIO: R:{}, G:{}, B{}\n".
              format(obj.rPi_TAG, obj.secret_key, obj.url, obj.pm.R_pin, obj.pm.G_pin, obj.pm.B_pin))
    except Exception as e:
        print("error reading config file: {}".format(e))
        obj.rPi_TAG = ""
        obj.secret_key = ""


def set_configs(obj):
    try:
        file = 'config.ini'
        path = os.path.join(obj.global_path, "configs", file)
        config = cfg()
        print(f"setting configs: {path}")
        config.read(path)
        if obj.rPi_TAG is not None:
            config.set('device', 'TAG', obj.rPi_TAG)
        if obj.secret_key is not None:
            config.set('device', 'secret_key', obj.secret_key)
        if obj.pm.R_pin is not None:
            config.set('GPIO', 'R', str(obj.pm.R_pin))
        if obj.pm.G_pin is not None:
            config.set('GPIO', 'G', str(obj.pm.G_pin))
        if obj.pm.B_pin is not None:
            config.set('GPIO', 'B', str(obj.pm.B_pin))
        with open(path, "w") as configfile:
            config.write(configfile)
        print("configs updated")
    except Exception as e:
        print("error setting config file: {}".format(e))


def add_to_crontab(file):
    with os.popen("crontab -l", "r") as pipe:
        current = pipe.read()
    if file in current:
        print("file already exists: ", file)
    else:
        current += f"@reboot sleep 30 && bash {file} &\n"
        print("adding file to crontab: ", file)
        print(current)
        with NamedTemporaryFile("w") as f:
            f.write(current)
            f.flush()
            system(f"crontab {f.name}")


def setup_onstart(obj):
    if "Linux" in platform.system():
        add_to_crontab(obj.main_script)


def login(obj, credentials=True, GPIO_=True, on_start=True):
    if credentials:
        print("Hi welcome to Hall9k, please setup your device\n"
              " remember that credential should match those on your account")
        obj.rPi_TAG = input("enter tag: ")
        secret_key = input("enter secret-key: ")
        obj.secret_key = sha256_crypt.encrypt(str(secret_key))
    if GPIO_:
        print("using GPIO pins: R:{}, G:{}, B{}".format(obj.pm.R_pin, obj.pm.G_pin, obj.pm.B_pin))
        while True:
            gpi_change = input("would you like to change it [y/yes, n/no]: ")
            if 'y' in gpi_change:
                obj.pm.R_pin  = input("enter R pin: ")
                obj.pm.G_pin = input("enter R pin: ")
                obj.pm.B_pin  = input("enter B pin: ")
                break
            if 'n' in gpi_change:
                break
            else:
                print("wrong input")

    if credentials or GPIO_:
        set_configs(obj)

    if on_start:
        setup_onstart(obj)
