import subprocess
import sys
import os.path

def multizip(filename,outdir):
    fn = os.path.basename(filename)
    command = '7za -v1m a -y {} {}'.format(os.path.join(outdir,fn + "_.zip"),filename)
    subprocess.run(command, shell = True)

def extract(filename):
    command = '7za x -y {}'.format(filename)
    subprocess.run(command, shell = True)
    

if __name__ == "__main__":
    fileName = sys.argv[1]
    #multizip(fileName)
    extract(fileName)
