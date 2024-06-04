from utils.config import load_config
from utils.interface import launch_interface
from dotenv import load_dotenv
load_dotenv()

def main():
    load_config()
    launch_interface()

if __name__ == "__main__":
    main()