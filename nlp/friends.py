import tarfile,fnmatch,os
rootPath = r"C:\Users\bryan\Desktop"
pattern = '*.tar.gz'
for root, dirs, files in os.walk(rootPath):
    for filename in fnmatch.filter(files, pattern):
        print(os.path.join(root, filename))
        tarfile.open(os.path.join(root, filename)).extractall(
                os.path.join(root, filename.split(".")[0]))

import tarfile
fname = r"C:\Users\bryan\Desktop\facebook.tar.gz"
if (fname.endswith("tar.gz")):
    tar = tarfile.open(fname, "r:gz")
    tar.extractall()
    tar.close()
elif (fname.endswith("tar")):
    tar = tarfile.open(fname, "r:")
    tar.extractall()
    tar.close()