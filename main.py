from utils.client_class import Client
import os
import sys
from utils.credentials_manager import login
from utils import GPIO_manager as gm


def print_manual():
    print(" to run client, type: rpiApp --run \n"
          " to change credentials, type: rpiApp --credentials \n"
          " to change GPIO pins, type: rpiApp --GPIO \n"
          " to set application on reboot, type: rpiApp --addcron \n")


if __name__ == '__main__':
    try:
        main_script = str(os.getcwd()) + "/launcher.sh"
        if len(sys.argv) > 2:
            print("invalid number of arguments, using first one: ", sys.argv[1])
        if len(sys.argv) <= 1:
            print_manual()
        else:
            client = Client(main_script)
            client.get_configs()
            if sys.argv[1] == "--run":
                client.start()
                print("run")

            elif sys.argv[1] == "--credentials":
                print("set credentials")
                login(client, credentials=True, GPIO_=False, on_start=False)

            elif sys.argv[1] == "--GPIO":
                print("set GPIO")
                login(client, credentials=False, GPIO_=True, on_start=False)

            elif sys.argv[1] == "--login":
                print("log in")
                login(client, credentials=True, GPIO_=True, on_start=False)

            elif sys.argv[1] == "--addcron":
                print("addcron")
                login(client, credentials=False, GPIO_=False, on_start=True)

            else:
                print("wrong argument")
                print_manual()

    except KeyboardInterrupt:
        print(f'KeyboardInterrupt, cleaning pins')
        gm.PinsManager.clean()
