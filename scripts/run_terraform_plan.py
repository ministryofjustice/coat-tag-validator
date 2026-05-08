import os
import shutil
import subprocess
import sys


def run(cmd):
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        sys.exit(result.returncode)


github_action_path = os.environ.get("GITHUB_ACTION_PATH")
workspace = os.environ.get("WORKSPACE")

source_file = f"{github_action_path}/overrides/_tag_check_backend_override.tf"
dest_file = "./_tag_check_backend_override.tf"

print("🪛 Overriding any remote backend with a local one...")
shutil.copy(source_file, dest_file)

print("🔧 Initializing Terraform...")
run("terraform init -reconfigure -input=false")

if workspace:
    print(f"🗂  Selecting workspace: {workspace}")
    run(f'terraform workspace select -or-create "{workspace}"')

print("📝 Generating Terraform plan...")
run("terraform plan -out=tfplan.binary -input=false -lock=false")

print("🔄 Converting plan to JSON...")
run("terraform show -json tfplan.binary > tfplan.json")

print("✅ Plan generated successfully")

if os.path.isfile(source_file):
    print("Cleaning up plan artefacts")
    os.remove(source_file)