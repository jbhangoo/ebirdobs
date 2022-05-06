import os
import uuid

"""
FileSystem
Base class for all File and Directory operations
"""
class FileSystem:
    def create_unique_directory(self, dirname):
        subfilename, subdirname = self.create_unique_filename(dirname)
        if subdirname:
            os.mkdir(subdirname)
        return subfilename, subdirname

    def create_unique_filename(self, dirname, prefix='', suffix=''):
        i = 0
        while i < 1000:
            unique_name = str(uuid.uuid4())
            unique_int = int(unique_name[:6], 16)
            new_filename = '{0}{1}{2}'.format(prefix, str(unique_int), suffix)
            new_dirname = os.path.join(dirname, new_filename)
            if not os.path.exists(new_dirname):
                return new_filename, new_dirname
        return None, None

    def create_unique_filenames(self, dirname, prefixes=[], suffixes=[]):
        newnames = []
        for p,s in zip(prefixes,suffixes):
            fname, pathname = self.create_unique_filename(dirname, p, s)
            newnames.append((fname, pathname))
        return newnames