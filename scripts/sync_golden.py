import os
import shutil
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="AI Impl Kit - Sync Golden Outputs")
    parser.add_argument("--prompt", required=True, help="Specific prompt ID to sync")
    parser.add_argument("--case", required=True, help="Specific case name to sync")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    local_dir = os.path.join(project_root, "outputs", "local", args.prompt)
    golden_dir = os.path.join(project_root, "fixtures", "golden", args.prompt)
    
    local_file = os.path.join(local_dir, f"{args.case}.md")
    if not os.path.exists(local_file):
        local_file = os.path.join(local_dir, f"{args.case}.json")
        if not os.path.exists(local_file):
            print(f"Error: Could not find recent local output for case '{args.case}' in {local_dir}")
            exit(1)

    os.makedirs(golden_dir, exist_ok=True)
    filename = os.path.basename(local_file)
    golden_file = os.path.join(golden_dir, filename)
    
    shutil.copy2(local_file, golden_file)
    print(f"Successfully synced Golden Output: {golden_file}")
    print("Please commit the updated golden file to version control.")

if __name__ == "__main__":
    main()
