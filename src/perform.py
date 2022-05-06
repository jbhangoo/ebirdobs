import json
import os

from src.filesystem import FileSystem

class Perform(FileSystem):
    def __init__(self, days, results_root):

        # Defaults
        self.resultsdir = None
        self.outfile = None
        self.errfile = None

        # Create a subdirectory in data/results
        resultsdirname, self.resultsdir = self.create_unique_directory(results_root)
        if resultsdirname is None:
            return
        # Create files for stdout and stderr
        self.outfile = os.path.join(self.resultsdir, "stdout.txt")
        self.errfile = os.path.join(self.resultsdir, "stderr.txt")

        # Process
        with open(self.outfile, "w") as outf:
            with open(self.errfile, "w") as errf:
                # Write output and errors
                pass

    def serialize(self):
        return json.dumps(self, default=lambda o: o.__dict__)