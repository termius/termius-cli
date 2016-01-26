import abc
import six
import pickle
import json
import csv
import os
import shutil

from collections import OrderedDict


@six.add_metaclass(abc.ABCMeta)
class Driver(object):

    @abc.abstractmethod
    def dump(self, stream, obj_data):
        """Dump obj_data to stream."""

    @abc.abstractmethod
    def load(self, stream):
        """Load obj_data from stream."""
        stream.seek(0)


class PickleDriver(Driver):

    def dump(self, stream, obj_data):
        pickle.dump(dict(obj_data), stream, 2)

    def load(self, stream):
        super(PickleDriver, self).load(stream)
        return pickle.load(stream)


class JSONDriver(Driver):

    def dump(self, stream, obj_data):
        json.dump(obj_data, stream, separators=(',', ':'))

    def load(self, stream):
        super(JSONDriver, self).load(stream)
        return json.load(stream)


class CSVDriver(Driver):

    def dump(self, stream, obj_data):
        csv.writer(stream).writerows(obj_data.items())

    def load(self, stream):
        super(CSVDriver, self).load(stream)
        return csv.reader(stream)


DRIVERS = OrderedDict((
    ('pickle', PickleDriver()),
    ('json', JSONDriver()),
    ('csv', CSVDriver()),
))


class PersistentDict(OrderedDict):

    '''Persistent dictionary with an API compatible with shelve and anydbm.

    The dict is kept in memory, so the dictionary operations run as fast as
    a regular dictionary.

    Write to disk is delayed until close or sync (similar to gdbm's fast mode).

    Input file format is automatically discovered.
    Output file format is selectable between pickle, json, and csv.
    All three serialization formats are backed by fast C implementations.

    '''

    def __init__(self, filename, flag='c', mode=None, format='json',
                 *args, **kwds):
        self.flag = flag                    # r=readonly, c=create, or n=new
        self.mode = mode                    # None or an octal triple like 0644
        self.format = format                # 'csv', 'json', or 'pickle'
        self.filename = filename
        super(PersistentDict, self).__init__(*args, **kwds)
        if flag != 'n' and os.access(filename, os.R_OK):
            with open(filename, self._read_mode()) as fileobj:
                self.load(fileobj)

    def _write_mode(self):
        return 'wb' if self.format == 'pickle' else 'w'

    def _read_mode(self):
        return 'rb' if format == 'pickle' else 'r'

    def sync(self):
        'Write dict to disk'

        def write_temp_file(filename):
            tempname = filename + '.tmp'
            try:
                with open(tempname, self._write_mode()) as fileobj:
                    self.dump(fileobj)
            except Exception:
                os.remove(tempname)
                raise
            return tempname

        def move_file_and_set_mode(src, dst, dst_mode):
            shutil.move(src, dst)    # atomic commit
            if dst_mode is not None:
                os.chmod(dst, dst_mode)

        if self.flag != 'r':
            tempname = write_temp_file(self.filename)
            move_file_and_set_mode(tempname, self.filename, self.mode)

    def close(self):
        self.sync()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    def dump(self, fileobj):
        try:
            DRIVERS[self.format].dump(fileobj, self)
        except KeyError:
            raise NotImplementedError('Unknown format: ' + repr(self.format))

    def load(self, fileobj):
        for loader in DRIVERS.values():
            try:
                return self.update(loader.load(fileobj))
            except Exception:
                pass
        raise ValueError('File not in a supported format')
