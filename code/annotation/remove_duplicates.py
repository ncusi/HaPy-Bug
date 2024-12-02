import glob
import os
import shutil

import click


@click.command()
@click.argument("duplicates", nargs=1)
def run(duplicates):
    "One file per line, only duplicates ie. fdupes -f -1"
    with open(duplicates,"r") as f:
        for line in f:
            # skip blank lines
            if not line.strip():
                continue

            # remove tmp dir from path to get the oryginal filename
            in_path = "/" + "/".join(line.split("/")[3:])

            # get in_path and filename
            in_dir, in_file = os.path.split(in_path)

            # set name to which file will be moved
            out_dir = in_dir.replace("patches", "duplicated_patches")

            # Create dir for duplicated_patches
            os.makedirs(out_dir, exist_ok=True)

            # move duplicates and include all files associaed with duplicate *{sha1}*.*
            for g in glob.glob(in_dir + "/*"+in_file.split('.')[0] + "*.*"):
                out_file = os.path.basename(g)
                # move files
                os.rename(g, f"{out_dir}/{out_file}")

            os.remove(in_dir.replace("patches", "annotation") + f"/{in_file.split('.')[0]}.json")

            # check if any file left in patches directory (if not remove bug)
            files_left = 0
            for g in glob.glob(in_dir + "/*"):
                files_left += 1
            if not files_left:
                rm_dir = in_dir.replace("patches","")
                print(f"Removing directory: {rm_dir}")
                shutil.rmtree(rm_dir)


if __name__ == "__main__":
    run()
