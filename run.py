import os
import sys

def restart():

    if len(sys.argv) > 1 and sys.argv[1] == '--kill':
        if not os.path.exists(".pid"):
            print("Could not find pid file, skipping kill")
        else:
            with open('.pid', 'r') as f:
                pid = f.read()
                print(f"Killing {str(pid)}")
                os.kill(int(pid), 9)

    os.system('nohup python3 -u bot.py &')

if __name__ == "__main__":
    restart()
