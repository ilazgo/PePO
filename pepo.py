import os
import subprocess
import argparse

def check_datetimeoriginal(file_path):
    command = ['exiftool', '-s', '-DateTimeOriginal', file_path]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        datetime_original = None

        for line in result.stdout.splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                if key == 'DateTimeOriginal':
                    datetime_original = value

        if datetime_original:
            print(f"{file_path}:\n{result.stdout}")
        else:
            print(f"Warning: {file_path} has no DateTimeOriginal.")

    else:
        print(f"Error: {file_path} - {result.stderr}")

def main():
    parser = argparse.ArgumentParser(
        description="Loops through a folder recursively and checks the DateTimeOriginal metadata of the images.")
    parser.add_argument('directory', type=str, help="Directory")
    args = parser.parse_args()

    for root, dirs, files in os.walk(args.directory):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.mp4')):
                file_path = os.path.join(root, file)
                check_datetimeoriginal(file_path)


if __name__ == "__main__":
    main()
