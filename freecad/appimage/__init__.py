import os

def get_package_info(package=None):
    version_file = os.path.join(os.path.dirname(os.environ["PREFIX"]), "packages.txt")
    with open(version_file, "r") as fn:
        while True:
            line = fn.readline()
            if line.startswith("# Name"):
                header = line
                break
        if not package:
            print(header + fn.read())
        else:
            for line in fn:
                if line.split()[0].startswith(package):
                    print(header + line)
