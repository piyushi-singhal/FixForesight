import os
import signal
import subprocess

pids_to_kill = [33389, 44545, 50233, 50234]

for pid in pids_to_kill:
    try:
        print(f"Terminating PID: {pid}")
        os.kill(pid, signal.SIGKILL)
        print(f"Successfully killed {pid}")
    except Exception as e:
        print(f"Could not kill {pid}: {e}")
