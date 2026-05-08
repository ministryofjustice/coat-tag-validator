import os
import shutil
import subprocess


def run(cmd):
    subprocess.run(cmd, shell=True, check=True)


github_action_path = os.environ.get("GITHUB_ACTION_PATH")
workspace = os.environ.get("WORKSPACE")

SOURCE_FILE = f"{github_action_path}/overrides/_tag_check_backend_override.tf"
DEST_FILE = "./_tag_check_backend_override.tf"

print("🪛 Overriding any remote backend with a local one...")
shutil.copy(SOURCE_FILE, DEST_FILE)

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

if os.path.isfile(SOURCE_FILE):
    print("Cleaning up plan artefacts")
    os.remove(SOURCE_FILE)
