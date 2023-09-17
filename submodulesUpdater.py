import os
import subprocess


def update_submodules():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    submodule_dir = 'submodules'
    submodule_path = os.path.join(current_dir, submodule_dir)

    try:
        # Run command git submodule update --remote
        subprocess.run(['git', 'submodule', 'update', '--remote'], check=True, cwd=submodule_path, shell=True)

        print("Submodules Updated")

    except subprocess.CalledProcessError as e:
        print(f"Error during submodules update: {e}")

    except Exception as ex:
        print(f"Undefined error in submodules update: {ex}")


if __name__ == "__main__":
    update_submodules()
