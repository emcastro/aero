import os

DIRECTORY_MODE = 0o040000
FILE_MODE_MASK = 0o170000


def list_delete_files_recursive(dir_name, *, delete=False, level=0):
    entries = os.listdir(dir_name)
    if dir_name == "/":
        dir_name = ""
    for entry in entries:
        fullname = dir_name + "/" + entry
        ident = level * " "
        print(ident, fullname)

        if fullname == "/sd/dem.zarr/dem":
            print(ident, "-skipped...")
            continue

        stats = os.stat(fullname)
        # if file is directory
        directory = stats[0] & FILE_MODE_MASK == DIRECTORY_MODE
        if directory:
            list_delete_files_recursive(fullname, delete=delete, level=level + 1)

        if delete:
            print(ident, "-deleting", fullname)
            if fullname == "/sd/dem.zarr":
                print(ident, " -no deletable")
            else:
                if directory:
                    os.rmdir(fullname)
                else:
                    os.unlink(fullname)


if __name__ == "__main__":
    list_delete_files_recursive("/sd", delete=True)
