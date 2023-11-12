import os
import subprocess

# Set the working directory
os.chdir('/app/')

# Install MySQL development headers and libraries
subprocess.run(['apt-get', 'update'])
subprocess.run(['apt-get', 'install', '-y', 'libmysqlclient-dev'])

# Install the MySQL client library
subprocess.run(['pip', 'install', 'mysqlclient'])

# Copy Nixpacks file
subprocess.run(['cp', '.nixpacks/nixpkgs-5148520bfab61f99fd25fb9ff7bfbb50dad3c9db.nix', '.nixpacks/nixpkgs-5148520bfab61f99fd25fb9ff7bfbb50dad3c9db.nix'])

# Install Nixpacks
subprocess.run(['nix-env', '-if', '.nixpacks/nixpkgs-5148520bfab61f99fd25fb9ff7bfbb50dad3c9db.nix'])
subprocess.run(['nix-collect-garbage', '-d'])

# Copy the rest of the files
subprocess.run(['cp', '-r', '.', '/app/'])

# Build phase
subprocess.run(['python', '-m', 'venv', '--copies', '/opt/venv'])
subprocess.run(['. /opt/venv/bin/activate && pip install -r requirements.txt'], shell=True)
