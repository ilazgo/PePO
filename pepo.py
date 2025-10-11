import os
import subprocess
import argparse
import logging
import shutil
from datetime import datetime

SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.tiff', '.mp4', '.mov')
DEFAULT_MIN_YEAR = 2004
DEFAULT_MIN_MONTH = 1

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s - %(message)s"
)

def check_datetimeoriginal(file_path, max_year, max_month, min_year, min_month):
    try:
        command = ['exiftool', '-s', '-DateTimeOriginal', file_path]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except FileNotFoundError:
        raise RuntimeError(f"'exiftool' is not installed or is not found on PATH.")

    if result.returncode == 0:
        datetime_original = None

        try:
            for line in result.stdout.splitlines():
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    if key == 'DateTimeOriginal':
                        datetime_original = value
                        break

            if not datetime_original:
                return None, f"ERROR: {file_path} has no DateTimeOriginal."

            # Date format: "YYYY:MM:DD HH:MM:SS"
            dt = datetime.strptime(datetime_original, "%Y:%m:%d %H:%M:%S")

            if (dt.year > max_year) or (dt.year == max_year and dt.month > max_month):
                return None, f"{file_path} has a date after {max_year}/{max_month}: {datetime_original}"
            elif (dt.year < min_year) or (dt.year == min_year and dt.month < min_month):
                return None, f"{file_path} has a date before {min_year}/{min_month}: {datetime_original}"

            return dt.strftime("%Y%m%d_%H%M%S"), None

        except ValueError:
            return None, f"Date format is not YYYY:MM:DD HH:MM:SS in {file_path} - {datetime_original}"


def move_file_to_output(file_path, datetime_str, output_directory, folder_suffix=None):
    dt = datetime.strptime(datetime_str, "%Y%m%d_%H%M%S")
    year = dt.strftime("%Y")
    month = dt.strftime("%m")
    
    year_month_dir = os.path.join(output_directory, year, month)
    os.makedirs(year_month_dir, exist_ok=True)

    _, extension = os.path.splitext(file_path)
    
    if folder_suffix:
        new_filename = f"{datetime_str}_{folder_suffix}{extension}"
    else:
        new_filename = f"{datetime_str}{extension}"
        
    new_file_path = os.path.join(year_month_dir, new_filename)

    shutil.copy(file_path, new_file_path)
    return new_file_path


def main():
    parser = argparse.ArgumentParser(
        description="Loops through a folder recursively and checks the DateTimeOriginal metadata of the images.")
    parser.add_argument('directory', type=str, help="Directory")
    parser.add_argument('output_directory', type=str, help="Output directory for files without errors")
    parser.add_argument('--min-year', type=int, default=DEFAULT_MIN_YEAR,
                       help=f"Minimum allowed year (default: {DEFAULT_MIN_YEAR})")
    parser.add_argument('--min-month', type=int, default=DEFAULT_MIN_MONTH,
                       help=f"Minimum allowed month for min-year (default: {DEFAULT_MIN_MONTH})")
    args = parser.parse_args()

    current_year = datetime.now().year
    current_month = datetime.now().month

    for root, dirs, files in os.walk(args.directory):
        for file in files:
            if file.lower().endswith(SUPPORTED_EXTENSIONS):
                file_path = os.path.join(root, file)
                
                folder_suffix = None
                relative_path = os.path.relpath(root, args.directory)
                
                if relative_path != '.':
                    first_level_folder = relative_path.split(os.sep)[0]
                    
                    if first_level_folder.startswith('_'):
                        folder_suffix = first_level_folder[1:]
                
                output, error = check_datetimeoriginal(file_path, current_year, current_month, args.min_year, args.min_month)
                if output:
                    try:
                        new_file_path = move_file_to_output(file_path, output, args.output_directory, folder_suffix)
                    except Exception as e:
                        logging.error(f"Failed to move {file_path}: {e}")
                else:
                    logging.warning(error)



if __name__ == "__main__":
    main()
