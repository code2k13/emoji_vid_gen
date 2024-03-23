import argparse
from cache import Cache
import unicodedata
import shutil
import os


def copy_to_cache(src_file, cache_dir):
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    filename = os.path.basename(src_file)
    dest_file = os.path.join(cache_dir, filename)

    if os.path.exists(dest_file):
        raise FileExistsError(
            f"File '{filename}' already exists in the cache directory.")

    shutil.copy(src_file, dest_file)
    print(f"File '{filename}' copied to cache directory.")


def delete_from_cache(filename, cache_dir):
    file_path = os.path.join(cache_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File '{filename}' deleted from cache directory.")
    else:
        print(f"File '{filename}' not found in cache directory.")


def add_to_cache(filename, emoji):
    cache = Cache()
    cache.store_text(emoji, filename)
    cache.close()
    copy_to_cache(filename, ".cache")


def remove_from_cache(emoji):
    cache = Cache()
    cached_value = cache.get_file_path(emoji)
    if cached_value:
        cache.delete_entry(emoji)
        cache.close()
        delete_from_cache(cached_value, ".cache")


def main():
    parser = argparse.ArgumentParser(description='Emoji File Store')
    parser.add_argument('action', choices=[
                        'add', 'remove'], help='Action to perform: add or remove')
    parser.add_argument('emoji', type=str, help='Emoji to add or remove')
    parser.add_argument('--filename', type=str,
                        help='Filename to store (only for add action)')

    args = parser.parse_args()
    emoji = unicodedata.name(args.emoji[0])
    if args.action == 'add':
        if args.filename:
            add_to_cache(args.filename, emoji)
        else:
            print("Filename is required for add action")
    elif args.action == 'remove':
        remove_from_cache(emoji)


if __name__ == "__main__":
    main()
