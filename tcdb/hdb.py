# -*- coding: utf-8 -*-
# Tokyo Cabinet Python ctypes binding.

"""
HDB is an implementation of bsddb-like API for Tokyo Cabinet hash
database.

We need to import 'hdb' class, and use like that:

>>> from tcdb.hdb import hdb

>>> db = hdb()             # Create a new database object
>>> db.open('casket.tch')  # By default create it if don't exist

>>> db.put("foo", "hop")
True
>>> db.put("bar", "step")
True
>>> db.put("baz", "jump")
True

>>> db.get("foo")
'hop'

>>> db.close()

"""

import ctypes
import datetime

import tc
import util


# enumeration for additional flags
FOPEN    = 1 << 0               # whether opened
FFATAL   = 1 << 1               # whether with fatal error

# enumeration for tuning options
TLARGE   = 1 << 0               # use 64-bit bucket array
TDEFLATE = 1 << 1               # compress each record with Deflate
TBZIP    = 1 << 2               # compress each record with BZIP2
TTCBS    = 1 << 3               # compress each record with TCBS
TEXCODEC = 1 << 4               # compress each record with custom functions

# enumeration for open modes
OREADER  = 1 << 0               # open as a reader
OWRITER  = 1 << 1               # open as a writer
OCREAT   = 1 << 2               # writer creating
OTRUNC   = 1 << 3               # writer truncating
ONOLCK   = 1 << 4               # open without locking
OLCKNB   = 1 << 5               # lock without blocking
OTSYNC   = 1 << 6               # synchronize every transaction


class hdb(object):
    def __init__(self):
        """Create a hash database object."""
        self.db = tc.hdb_new()

    def __del__(self):
        """Delete a hash database object."""
        tc.hdb_del(self.db)

    def setmutex(self):
        """Set mutual exclusion control of a hash database object for
        threading."""
        return tc.hdb_setmutex(self.db)

    def tune(self, bnum, apow, fpow, opts):
        """Set the tuning parameters of a hash database object."""
        return tc.hdb_tume(self.db, bnum, apow, fpow, opts)

    def setcache(self, rcnum):
        """Set the caching parameters of a hash database object."""
        return tc.hdb_setcache(self.db, rcnum)

    def setxmsiz(self, xmsiz):
        """Set the size of the extra mapped memory of a hash database
        object."""
        return tc.hdb_setxmsiz(self.db, xmsiz)

    def setdfunit(self, dfunit):
        """Set the unit step number of auto defragmentation of a hash
        database object."""
        return tc.hdb_setdfunit(self.db, dfunit)

    def open(self, path, omode=OWRITER|OCREAT, bnum=None, apow=None, fpow=None,
             opts=None, rcnum=None, xmsiz=None, dfunit=None):
        """Open a database file and connect a hash database object."""
        if rcnum:
            self.setcache(rcnum)

        if xmsiz:
            self.setxmsiz(xmsiz)

        if dfunit:
            self.setdfunit(dfunit)

        kwargs = dict([x for x in (('bnum', bnum),
                                   ('apow', apow),
                                   ('fpow', fpow),
                                   ('opts', opts)) if x[1]])
        if kwargs:
            if not tc.hdb_tune(self.db, **kwargs):
                raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))

        if not tc.hdb_open(self.db, path, omode):
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))

    def close(self):
        """Close a hash database object."""
        result = tc.hdb_close(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def __setitem__(self, key, value):
        """Store any Python object into a hash database object."""
        return self.put(key, value)

    def put(self, key, value):
        """Store any Python object into a hash database object."""
        (c_key, c_key_len) = util.serialize_obj(key)
        (c_value, c_value_len) = util.serialize_obj(value)
        result = tc.hdb_put(self.db, c_key, c_key_len, c_value, c_value_len)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def put_str(self, key, value):
        """Store a string record into a hash database object."""
        assert isinstance(value, str), 'Value is not a string'
        return self._put(key, value)

    def put_unicode(self, key, value):
        """Store an unicode string record into a hash database object."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self._put(key, value)

    def put_int(self, key, value):
        """Store an integer record into a hash database object."""
        assert isinstance(value, int), 'Value is not an integer'
        return self._put(key, value)

    def put_float(self, key, value):
        """Store a double precision record into a hash database
        object."""
        assert isinstance(value, float), 'Value is not a float'
        return self._put(key, value)

    def _put(self, key, value):
        """Store an object record into a hash database object."""
        (c_key, c_key_len) = util.serialize_obj(key)
        (c_value, c_value_len) = util.serialize_value(value)
        result = tc.hdb_put(self.db, c_key, c_key_len, c_value, c_value_len)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def putkeep(self, key, value):
        """Store a new Python object into a hash database object."""
        (c_key, c_key_len) = util.serialize_obj(key)
        (c_value, c_value_len) = util.serialize_obj(value)
        result = tc.hdb_putkeep(self.db, c_key, c_key_len, c_value, c_value_len)
        return result

    def putkeep_str(self, key, value):
        """Store a new string record into a hash database object."""
        assert isinstance(value, str), 'Value is not a string'
        return self._putkeep(key, value)

    def putkeep_unicode(self, key, value):
        """Store a new unicode string record into a hash database
        object."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self._putkeep(key, value)

    def putkeep_int(self, key, value):
        """Store a new integer record into a hash database object."""
        assert isinstance(value, int), 'Value is not an integer'
        return self._putkeep(key, value)

    def putkeep_float(self, key, value):
        """Store a new double precision record into a hash database
        object."""
        assert isinstance(value, float), 'Value is not a float'
        return self._putkeep(key, value)

    def _putkeep(self, key, value):
        """Store a new object record into a hash database object."""
        (c_key, c_key_len) = util.serialize_obj(key)
        (c_value, c_value_len) = util.serialize_value(value)
        result = tc.hdb_putkeep(self.db, c_key, c_key_len, c_value, c_value_len)
        return result

    def putcat_str(self, key, value):
        """Concatenate a string value at the end of the existing
        record in a hash database object."""
        assert isinstance(value, str), 'Value is not a string'
        return self._putcat(key, value)

    def putcat_unicode(self, key, value):
        """Concatenate an unicode string value at the end of the
        existing record in a hash database object."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self._putcat(key, value)

    def _putcat(self, key, value):
        """Concatenate an object value at the end of the existing
        record in a hash database object."""
        (c_key, c_key_len) = util.serialize_obj(key)
        (c_value, c_value_len) = util.serialize_value(value)
        result = tc.hdb_putcat(self.db, c_key, c_key_len, c_value, c_value_len)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def putasync(self, key, value):
        """Store a Python object into a hash database object in
        asynchronous fashion."""
        (c_key, c_key_len) = util.serialize_obj(key)
        (c_value, c_value_len) = util.serialize_obj(value)
        result = tc.hdb_putasync(self.db, c_key, c_key_len, c_value, c_value_len)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def putasync_str(self, key, value):
        """Store a string record into a hash database object in
        asynchronous fashion."""
        assert isinstance(value, str), 'Value is not a string'
        return self._putasync(key, value)

    def putasync_unicode(self, key, value):
        """Store an unicode string record into a hash database object
        in asynchronous fashion."""
        assert isinstance(value, unicode), 'Value is not an unicode string'
        return self._putasync(key, value)

    def putasync_int(self, key, value):
        """Store an integer record into a hash database object in
        asynchronous fashion."""
        assert isinstance(value, int), 'Value is not an integer'
        return self._putasync(key, value)

    def putasync_float(self, key, value):
        """Store a double precision record into a hash database object
        in asynchronous fashion."""
        assert isinstance(value, float), 'Value is not a float'
        return self._putasync(key, value)

    def _putasync(self, key, value):
        """Store an object record into a hash database object in
        asynchronous fashion."""
        (c_key, c_key_len) = util.serialize_obj(key)
        (c_value, c_value_len) = util.serialize_value(value)
        result = tc.hdb_putasync(self.db, c_key, c_key_len, c_value, c_value_len)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def __delitem__(self, key):
        """Remove a Python object of a hash database object."""
        return self.out(key)

    def out(self, key):
        """Remove a Python object of a hash database object."""
        (c_key, c_key_len) = util.serialize_obj(key)
        result = tc.hdb_out(self.db, c_key, c_key_len)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def __getitem__(self, key):
        """Retrieve a Python object in a hash database object."""
        return self.get(key)

    def get(self, key):
        """Retrieve a Python object in a hash database object."""
        (c_value, c_value_len) = self._get(key)
        return util.deserialize_obj(c_value, c_value_len)

    def get_str(self, key):
        """Retrieve a string record in a hash database object."""
        (c_value, c_value_len) = self._get(key)
        return util.deserialize_str(c_value, c_value_len)

    def get_unicode(self, key):
        """Retrieve an unicode string record in a hash database
        object."""
        (c_value, c_value_len) = self._get(key)
        return util.deserialize_unicode(c_value, c_value_len)

    def get_int(self, key):
        """Retrieve an integer record in a hash database object."""
        (c_value, c_value_len) = self._get(key)
        return util.deserialize_int(c_value, c_value_len)

    def get_float(self, key):
        """Retrieve a double precision record in a hash database
        object."""
        (c_value, c_value_len) = self._get(key)
        return util.deserialize_float(c_value, c_value_len)

    def _get(self, key):
        """Retrieve a Python object in a hash database object."""
        (c_key, c_key_len) = util.serialize_obj(key)
        (c_value, c_value_len) = tc.hdb_get(self.db, c_key, c_key_len)
        if not c_value:
            raise KeyError(key)
        return (c_value, c_value_len)

    def vsiz(self, key):
        """Get the size of the value of a Python object in a hash
        database object."""
        (c_key, c_key_len) = util.serialize_obj(key)
        result = tc.hdb_vsiz(self.db, c_key, c_key_len)
        if result == -1:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def keys(self):
        """Get all the keys of a hash database object."""
        return list(self.iterkeys())

    def iterkeys(self):
        """Iterate for every key in a hash database object."""
        if not tc.hdb_iterinit(self.db):
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        while True:
            c_key, c_key_len = tc.hdb_iternext(self.db)
            if not c_key:
                break
            key = util.deserialize_obj(c_key, c_key_len)
            yield key

    def values(self):
        """Get all the values of a hash database object."""
        return list(self.itervalues())

    def itervalues(self):
        """Iterate for every value in a hash database object."""
        if not tc.hdb_iterinit(self.db):
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        while True:
            c_key, c_key_len = tc.hdb_iternext(self.db)
            if not c_key:
                break
            (c_value, c_value_len) = tc.hdb_get(self.db, c_key, c_key_len)
            value = util.deserialize_obj(c_value, c_value_len)
            yield value

    def iteritems(self):
        """Iterate for every key / value in a hash database object."""
        if not tc.hdb_iterinit(self.db):
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        while True:
            xstr_key = tc.tcxstrnew()
            xstr_value = tc.tcxstrnew()
            result = tc.hdb_iternext3(self.db, xstr_key, xstr_value)
            if not result:
                break
            key = util.deserialize_xstr_obj(xstr_key)
            value = util.deserialize_xstr_obj(xstr_value)
            yield (key, value)

    def __iter__(self):
        """Iterate for every key in a hash database object."""
        return self.iterkeys()

    def fwmkeys(self, prefix):
        """Get forward matching string keys in a hash database object."""
        (c_prefix, c_prefix_len) = util.serialize_obj(prefix)
        tclist_objs = tc.hdb_fwmkeys(self.db, c_prefix, c_prefix_len)
        if not tclist_objs:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return util.deserialize_objs(tclist_objs)

    def add_int(self, key, num):
        """Add an integer to a record in a hash database object."""
        assert isinstance(num, int), 'Value is not an integer'
        (c_key, c_key_len) = util.serialize_obj(key)
        result = tc.hdb_addint(self.db, c_key, c_key_len, num)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def add_float(self, key, num):
        """Add a real number to a record in a hash database object."""
        assert isinstance(num, float), 'Value is not a float'
        (c_key, c_key_len) = util.serialize_obj(key)
        result = tc.hdb_adddouble(self.db, c_key, c_key_len, num)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def sync(self):
        """Synchronize updated contents of a hash database object with
        the file and the device."""
        result = tc.hdb_sync(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def optimize(self, bnum=None, apow=None, fpow=None, opts=None):
        """Optimize the file of a hash database object."""
        kwargs = dict([x for x in (('bnum', bnum),
                                   ('apow', apow),
                                   ('fpow', fpow),
                                   ('opts', opts)) if x[1]])
        result = tc.hdb_optimize(self.db, *kwargs)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def vanish(self):
        """Remove all records of a hash database object."""
        result = tc.hdb_vanish(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def copy(self, path):
        """Copy the database file of a hash database object."""
        result = tc.hdb_copy(self.db, path)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def tranbegin(self):
        """Begin the transaction of a hash database object."""
        result = tc.hdb_tranbegin(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def trancommit(self):
        """Commit the transaction of a hash database object."""
        result = tc.hdb_trancommit(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def tranabort(self):
        """Abort the transaction of a hash database object."""
        result = tc.hdb_tranabort(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def __enter__(self):
        """Enter in the 'with' statement and begin the transaction."""
        self.tranbegin()
        return self

    def __exit__(self, type, value, traceback):
        """Exit from 'with' statement and ends the transaction."""
        if type is None:
            self.trancommit()
        else:
            self.tranabort()

    def path(self):
        """Get the file path of a hash database object."""
        result = tc.hdb_path(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def __len__(self):
        """Get the number of records of a hash database object."""
        return tc.hdb_rnum(self.db)

    def fsiz(self):
        """Get the size of the database file of a hash database
        object."""
        result = tc.hdb_fsiz(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def setecode(self, ecode, filename, line, func):
        """Set the error code of a hash database object."""
        tc.setecode(self.db, ecode, filename, line, func)

    def settype(self, type_):
        """Set the type of a hash database object."""
        tc.settype(self.db, type_)

    def setdbgfd(self, fd):
        """Set the file descriptor for debugging output."""
        tc.setdbgfd(self.db, fd)

    def dbgfd(self):
        """Get the file descriptor for debugging output."""
        return tc.dbgfd(self.db)

    def hasmutex(self):
        """Check whether mutual exclusion control is set to a hash
        database object."""
        return tc.hdb_hasmutex(self.db)

    def memsync(self, phys):
        """Synchronize updating contents on memory of a hash database
        object."""
        result = tc.hdb_memsync(self.db, phys)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def cacheclear(self):
        """Clear the cache of a hash tree database object."""
        result = tc.hdb_cacheclear(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def bnum(self):
        """Get the number of elements of the bucket array of a hash
        database object."""
        return tc.hdb_bnum(self.db)

    def align(self):
        """Get the record alignment of a hash database object."""
        return tc.hdb_align(self.db)

    def fbpmax(self):
        """Get the maximum number of the free block pool of a a hash
        database object."""
        return tc.hdb_fbpmax(self.db)

    def xmsiz(self):
        """Get the size of the extra mapped memory of a hash database
        object."""
        return tc.hdb_xmsiz(self.db)

    def inode(self):
        """Get the inode number of the database file of a hash
        database object."""
        return tc.hdb_inode(self.db)

    def mtime(self):
        """Get the modification time of the database file of a hash
        database object."""
        return datetime.datetime.fromtimestamp(tc.hdb_mtime(self.db))

    def omode(self):
        """Get the connection mode of a hash database object."""
        return tc.hdb_omode(self.db)

    def type(self):
        """Get the database type of a hash database object."""
        return tc.hdb_type(self.db)

    def flags(self):
        """Get the additional flags of a hash database object."""
        return tc.hdb_flags(self.db)

    def opts(self):
        """Get the options of a hash database object."""
        return tc.hdb_opts(self.db)

    def opaque(self):
        """Get the pointer to the opaque field of a hash database
        object."""
        return tc.hdb_opaque(self.db)

    def bnumused(self):
        """Get the number of used elements of the bucket array of a
        hash database object."""
        return tc.hdb_bnumused(self.db)

    # def setcodecfunc(self, enc, encop, dec, decop):
    #     """Set the custom codec functions of a hash database
    #     object."""
    #     result = tc.hdb_setcodecfunc(self.db, TCCODEC(enc), encop,
    #                                  TCCODEC(dec), decop)
    #     if not result:
    #         raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
    #     return result

    # def codecfunc(self):
    #     """Get the custom codec functions of a hash database
    #     object."""
    #     # See tc.hdb_codecfunc

    def dfunit(self):
        """Get the unit step number of auto defragmentation of a hash
        database object."""
        return tc.hdb_dfunit(self.db)

    def defrag(self, step):
        """Perform dynamic defragmentation of a hash database
        object."""
        result = tc.hdb_defrag(self.db, step)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    # def putproc(self, key, value, proc, op):
    #     """Store a record into a hash database object with a
    #     duplication handler."""
    #     # See tc.hdb_putproc

    def foreach(self, proc, op):
        """Process each record atomically of a hash database
        object."""
        def proc_wraper(c_key, c_key_len, c_value, c_value_len, op):
            key = util.deserialize_obj(ctypes.cast(c_key, ctypes.c_void_p),
                                       c_key_len)
            value = util.deserialize_obj(ctypes.cast(c_value, ctypes.c_void_p),
                                         c_value_len)
            return proc(key, value, ctypes.cast(op, ctypes.c_char_p).value)

        result = tc.hdb_foreach(self.db, tc.TCITER(proc_wraper), op)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def tranvoid(self):
        """Void the transaction of a hash database object."""
        result = tc.hdb_tranvoid(self.db)
        if not result:
            raise tc.TCException(tc.hdb_errmsg(tc.hdb_ecode(self.db)))
        return result

    def __contains__(self, key):
        """Return True in hash database object has the key."""
        (c_key, c_key_len) = util.serialize_obj(key)
        return tc.hdb_iterinit2(self.db, c_key, c_key_len)
