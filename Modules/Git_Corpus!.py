import os
import subprocess
import nltk
from nltk.tokenize import word_tokenize
import shutil

# Download NLTK tokenizer data
nltk.download('punkt')

def clone_repository(repo_url, clone_dir):
    """Clone the GitHub repository to the specified directory."""
    try:
        subprocess.run(['git', 'clone', repo_url, clone_dir], check=True)
        print(f"Repository cloned to {clone_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        return False
    return True

def count_words_in_file(file_path):
    """Count the words in a given file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            words = word_tokenize(content)
            return len(words)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return 0

def count_words_in_directory(directory, output_file):
    """Recursively count the words in all files in a directory and log details."""
    total_word_count = 0
    with open(output_file, 'w', encoding='utf-8') as log_file:
        log_file.write("Word Count Report\n")
        log_file.write("=" * 50 + "\n")
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                word_count = count_words_in_file(file_path)
                total_word_count += word_count
                log_file.write(f"{file_path}: {word_count} words\n")
                print(f"Counted {word_count} words in {file_path}")
        log_file.write("=" * 50 + "\n")
        log_file.write(f"Total word count in repository: {total_word_count}\n")
    return total_word_count

if __name__ == "__main__":
    repo_url = "https://github.com/Mirror-Prismals/Mirror-SDK"
    clone_dir = "./Mirror-SDK"
    output_file = "word_count_report.txt"

    # Clone the repository
    if clone_repository(repo_url, clone_dir):
        # Count words and save to the output file
        total_words = count_words_in_directory(clone_dir, output_file)
        print(f"Total word count in the repository: {total_words}")
        print(f"Word count report saved to {output_file}")

        # Optionally, remove the cloned repository after counting
        try:
            shutil.rmtree(clone_dir)
            print(f"Removed cloned repository at {clone_dir}")
        except Exception as e:
            print(f"Error removing directory {clone_dir}: {e}")
