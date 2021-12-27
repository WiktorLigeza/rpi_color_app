from utils.client_class import Client
import os
import sys
from utils.credentials_manager import login
from utils import GPIO_manager as gm
import atexit
import subprocess

TERMINATE = True


def print_manual():
    print(" to run client, type: rpiApp --run \n"
          " to change credentials, type: rpiApp --credentials \n"
          " to change GPIO pins, type: rpiApp --GPIO \n"
          " to set application on reboot, type: rpiApp --addcron \n"
          " to stop currently working application, type: rpiApp --stop \n")


def at_exit():
    global TERMINATE
    if TERMINATE:
        print(f'\n Process has been terminated, cleaning pins')
        gm.PinsManager.clean()


if __name__ == '__main__':
    client = None
    atexit.register(at_exit)
    try:
        main_script = str(os.getcwd()) + "/launcher.sh"
        if len(sys.argv) > 2:
            print("invalid number of arguments, using first one: ", sys.argv[1])
        if len(sys.argv) <= 1:
            print_manual()
        else:
            if "--stop" in sys.argv[1]:
                client = Client(main_script)
                client.get_configs()
                print("stopping..")
                try:
                    kpids = subprocess.check_output(['pgrep', '-f', 'main']).decode().split("\n")
                    print("cleaning pins..")
                    gm.PinsManager.clean()
                except subprocess.CalledProcessError as e:
                    print("pgrep failed because ({}):".format(e.returncode), e.output.decode())
                else:
                    for pid_ in kpids:
                        if pid_ != '':
                            try:
                                os.kill(int(pid_), 9)
                                print(f"Process with pid {pid_} has been terminated")
                            except ProcessLookupError as e:
                                print("We tried to kill an old entry.")
                            except ValueError as e:
                                print(f"Well, there's no process with pid {pid_}...so...yeah.")
                quit()

            elif "--run" in sys.argv[1]:
                client = Client(main_script)
                client.get_configs()
                client.start()
                print("run")

            elif "--credentials" in sys.argv[1]:
                client = Client(main_script)
                client.get_configs()
                print("set credentials")
                login(client, credentials=True, GPIO_=False, on_start=False)
                gm.PinsManager.clean()

            elif "--GPIO" in sys.argv[1]:
                client = Client(main_script)
                client.get_configs()
                print("set GPIO")
                login(client, credentials=False, GPIO_=True, on_start=False)
                gm.PinsManager.clean()

            elif "--login" in sys.argv[1]:
                client = Client(main_script)
                client.get_configs()
                print("log in")
                login(client, credentials=True, GPIO_=True, on_start=False)
                gm.PinsManager.clean()

            elif "--addcron" in sys.argv[1]:
                client = Client(main_script)
                client.get_configs()
                print("addcron")
                login(client, credentials=False, GPIO_=False, on_start=True)
                gm.PinsManager.clean()

            else:
                TERMINATE = False
                print("wrong argument")
                print(f"got {sys.argv[1]}")
                print_manual()

    except KeyboardInterrupt:
        print(f'\n KeyboardInterrupt, cleaning pins')
        if client is not None:
            client.set_last_state()
        gm.PinsManager.clean()
