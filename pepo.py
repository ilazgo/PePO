import datetime
import os
import subprocess
import argparse
from datetime import datetime


def check_datetimeoriginal(file_path, max_year, max_month, min_year, min_month):
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
            try:
                # Date format: "YYYY:MM:DD HH:MM:SS"
                year = int(datetime_original.split(':')[0])
                month = int(datetime_original.split(':')[1])

                if (year > max_year) or (year == max_year and month > max_month):
                    print(f"{file_path} has a date after {max_year}/{max_month}: {datetime_original}")
                elif (year < min_year) or (year == min_year and month < min_month):
                    print(f"{file_path} has a date before {min_year}/{min_month}: {datetime_original}")
                else:
                    print(f"{file_path}:\n{result.stdout}")

            except ValueError:
                print(f"ERROR: Date format is not YYYY:MM:DD HH:MM:SS in {file_path} - {datetime_original}")

        else:
            print(f"ERROR: {file_path} has no DateTimeOriginal.")

    else:
        print(f"ERROR: {file_path} - {result.stderr}")


def main():
    parser = argparse.ArgumentParser(
        description="Loops through a folder recursively and checks the DateTimeOriginal metadata of the images.")
    parser.add_argument('directory', type=str, help="Directory")
    args = parser.parse_args()

    current_year = datetime.now().year
    current_month = datetime.now().month
    min_year = 2004
    min_month = 1

    for root, dirs, files in os.walk(args.directory):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.mp4')):
                file_path = os.path.join(root, file)
                check_datetimeoriginal(file_path, current_year, current_month, min_year, min_month)


if __name__ == "__main__":
    main()
