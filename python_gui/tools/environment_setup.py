import os
import sys
import platform

# Third-party module
modules_needed = [
    'pyserial',
    'numpy',
    'opencv-python',
    'PyQt5',
    'pywin32',
]

def install_pip():
    global system
    if system == 'Windows':
        print('Install process:')
        print('\t1.Download get-pip.py to a folder on your computer.')
        print('\t2.Open a command prompt and navigate to the folder containing get-pip.py.')
        print('\t3.Run the following command:')
        print('\t    python get-pip.py')
        # Auto install process
        result = os.system('python get-pip.py')
        if result != 0:
            result = os.system('python tools/get-pip.py')
        if result == 0:
            print('\t4.Pip is now installed!')
        else:
            print("\t4.Pip install failed!, please install by yourself!")
            sys.exit()
            
        if 0 != os.system('pip -V'):
            print('\t5.Check if C:\Python27\Scripts is in your system path. Otherwise, pip will not recognized.')
            sys.exit()
        
        print('\nPip installed!\n')
    else:
        print('Not support yet.')
        sys.exit()

if __name__ == "__main__":
    # 0, check if pyhton 3.x is installed
    print("0, check if pyhton 3x is installed")
    if sys.version_info.major == 3:
        print('\tCheck OK!')
    else:
        print('\tPlesse make sure you have installed python 3.x correctly!')
        sys.exit()
    
    # 1, check the operating system
    print("1, check the operating system")
    system = platform.system()
    print("\tYour system is '%s'." % (system))

    # 2, check if python pip is installed
    print("2, check if python pip is installed")
    result = os.system('pip -V')
    if result != 0:
        install_pip()
    else:
        print('\tPython pip is installed!')

    # 3, check/install third-party module is installed
    print("3, check/install third-party module is installed")
    print('Third-party modules: {}'.format(modules_needed))
    modules_uninstall = []
    for name in modules_needed:
        # check if this module is installed
        result = os.system('pip show %s' % (name))
        if result == 0:
            print("\nInstalled '%s', skip to next!\n" % (name))
            continue

        # install
        result = os.system('pip install %s' % (name))
        if result == 0:
            print("\nInstall '%s' sucess!\n" % (name))
        else:
            modules_uninstall.append(name)
            print("Install false, please install '%s' manually!" % (name))
            print("The cmd is: pip install %s" % (name))
    
    if modules_uninstall != []:
        print("\nPlease install these modules manually again:")
        for name in modules_uninstall:
            print(name)
    else:
        print("\nAll resuired modules are installed!\n")