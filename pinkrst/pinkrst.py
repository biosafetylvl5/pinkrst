import argparse


def process_file(file_path):
    try:
        # Read the file
        with open(file_path, "r") as file:
            processed_lines = [
                line.rstrip().replace("\t", " ") for line in file.readlines()
            ]

        while processed_lines[-1] == "\n":
            processed_lines = processed_lines[0:-1]
        processed_lines.append("\n")

        # Write the processed lines back to the file
        with open(file_path, "w") as file:
            if processed_lines:  # Check if there are any lines to write
                file.write("\n".join(processed_lines))

    except Exception as e:
        print(f"Error processing the file {file}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Process a file to remove trailing whitespaces, replace tabs with spaces, and avoid extra newlines at the end."
    )
    parser.add_argument(
        "file", type=str, help="Path to the file to be processed", nargs="+"
    )

    args = parser.parse_args()

    for file in args.file:
        process_file(file)


if __name__ == "__main__":
    main()
