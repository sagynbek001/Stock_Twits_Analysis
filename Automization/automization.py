import subprocess
import os
import glob
import time

# Define the remote path and local directory
remote_path = "netID@b80-l-ak8096-soc.abudhabi.nyu.edu:/data/responses/data/csv"
local_dir = "/path/to/local/directory"

# Define the SCP command
scp_command = f"scp -P 4410 '{remote_path}' {local_dir}"

def run_scp_command():
  try:
    subprocess.run(scp_command, shell=True, check=True)
    print("SCP command executed successfully.")
  except subprocess.CalledProcessError as e:
    print(f"Error executing SCP command: {e}")

def convert_notebooks_to_python():
  try:
    notebooks = glob.glob(os.path.join(local_dir, "*.ipynb"))

    for notebook in notebooks:
      # Convert each notebook to a Python script
      python_script = notebook.replace(".ipynb", ".py")
      subprocess.run(["jupyter", "nbconvert", "--to", "script", notebook], check=True)
      print(f"Converted {notebook} to {python_script}")
  except subprocess.CalledProcessError as e:
    print(f"Error converting notebooks: {e}")

def run_python_scripts():
  try:
    python_scripts = glob.glob(os.path.join(local_dir, "*.py"))

    for script in python_scripts:
      subprocess.run(["python", script], check=True)
      print(f"Executed {script}")
  except subprocess.CalledProcessError as e:
    print(f"Error executing Python script: {e}")

def main():
  while True:
    run_scp_command()
    convert_notebooks_to_python()
    run_python_scripts()
    # Sleep for one week (7 days)
    time.sleep(7 * 24 * 60 * 60)

if __name__ == "__main__":
  main()
