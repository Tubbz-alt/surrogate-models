__author__ = "Juri Bieler"
__version__ = "0.0.1"
__status__ = "Development"

# ==============================================================================
# description     :offers API to gmsh, which is used to generate a mesh from a cad geometry
# date            :2018-01-11
# notes           :
# python_version  :3.6
# ==============================================================================

import subprocess
import os
import signal
#import fcntl
import numpy as np
import time
import threading
import select
import sys
from threading import Thread
from timeit import default_timer as timer
import psutil

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x


class RealTimeSubprocess:

    def __init__(self):
        self.useTimeout = False
        print('done')

    def wait_for_keyword(self, que, word):
        while (True):
            try:
                line = que.get_nowait()  # or q.get(timeout=.1)
                if sys.version_info[0] >= 3:
                    line = line.decode('UTF-8')
            except Empty:
                #print('no output yet')
                time.sleep(0.01)
            else:  # got line
                print(line)
                if word in line:
                    return True

    def wait(self):
        while not self.terminated:
            if not self.timeout <= 0.:
                if timer() - self.startTime > self.timeout:
                    os.kill(os.getpgid(self.process.pid), signal.SIGTERM)
                    print('kill')
            print(str(timer() - self.startTime))
            time.sleep(0.001)

    def enqueue_output(self, out, queue):
        for line in iter(out.readline, b''):
            try:
                queue.put(line.decode('UTF-8'))
                print(line.decode('UTF-8'))
            except:
                queue.put(line)
                print(line)
        self.terminated = True
        print('closing')
        out.close()

    def write_to_console_and_enter(self, p, str):
        outStr = str + '\n'
        if sys.version_info[0] >= 3:
            outStr = outStr.encode('UTF-8')
        p.stdin.write(outStr)
        p.stdin.flush()

    def execute(self, commandList, working_dir='.', timeout=0.):
        self.errorFlag = False
        self.terminated = False
        self.startTime = timer()
        self.timeout = timeout
        ON_POSIX = 'posix' in sys.builtin_module_names
        self.process = subprocess.Popen(commandList,
                             cwd=working_dir,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             bufsize=1,
                             close_fds=ON_POSIX)
        self.q = Queue()
        t = Thread(target=self.enqueue_output, args=(self.process.stdout, self.q))
        #t.daemon = True  # thread dies with the program
        t.start()

        """
        self.wait_for_keyword(q, 'QUIT')
        self.write_to_console_and_enter(p, input_dat_file_name)
        self.wait_for_keyword(q, 'QUIT')

        #enter airfoil surface options
        self.write_to_console_and_enter(p, 'SOPT')
        self.wait_for_keyword(q, 'QUIT')
        #points on surface
        self.write_to_console_and_enter(p, 'NSRF')
        self.wait_for_keyword(q, 'Current')
        self.write_to_console_and_enter(p, str(self.pointNrAirfoilSurface))
        self.wait_for_keyword(q, 'QUIT')
        #farfield radius
        self.write_to_console_and_enter(p, 'RADI')
        self.wait_for_keyword(q, 'Current')
        self.write_to_console_and_enter(p, str(self.farfieldRadius))
        self.wait_for_keyword(q, 'QUIT')
        #go back
        self.write_to_console_and_enter(p, 'QUIT')
        self.wait_for_keyword(q, 'QUIT')

        #enter volume grid options
        self.write_to_console_and_enter(p, 'VOPT')
        self.wait_for_keyword(q, 'QUIT')
        #select mesh type
        self.write_to_console_and_enter(p, 'TOPO')
        self.wait_for_keyword(q, 'Sharp')
        if self.useCGrid:
            self.write_to_console_and_enter(p, 'CGRD')
        else:
            self.write_to_console_and_enter(p, 'OGRD')
        self.wait_for_keyword(q, 'QUIT')
        #set num of points in normal direction
        self.write_to_console_and_enter(p, 'JMAX')
        self.wait_for_keyword(q, 'Current')
        self.write_to_console_and_enter(p, str(self.pointsInNormalDir))
        self.wait_for_keyword(q, 'QUIT')
        #enter reynolds number
        self.write_to_console_and_enter(p, 'RECD')
        self.wait_for_keyword(q, 'Current')
        self.write_to_console_and_enter(p, str(self.reynoldsNum))
        self.wait_for_keyword(q, 'QUIT')




        # go back
        self.write_to_console_and_enter(p, 'QUIT')
        self.wait_for_keyword(q, 'QUIT')


        #start meshing
        self.write_to_console_and_enter(p, 'GRID')
        self.wait_for_keyword(q, 'QUIT')
        self.write_to_console_and_enter(p, 'SMTH')
        self.wait_for_keyword(q, 'QUIT')
        #quit
        self.write_to_console_and_enter(p, 'QUIT')

        if os.path.isfile(working_dir + '/' + input_dat_file_name.replace('.dat', '.p3d')):
            print('p3d file created successfully')
        else:
            print('ERROR: the p3d file could not be created as expected')
            self.errorFlag = True

        print('done')
        """


if __name__ == '__main__':
    prc = RealTimeSubprocess()
    prc.execute(['D:/prog/portable/Luftfahrt/bConverged/CalculiX/bin/cgx.bat',
                 '-b',
                 'wing_post.fbd'],
                working_dir='../../data_out/firstTry',
                timeout=.1)
    #while not prc.terminated:
    #    time.sleep(0.01)
    prc.wait()
    print('done')