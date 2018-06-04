#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2013-2018 Paulo Freitas
# MIT License (see LICENSE file)
'''
Filesystem helper module

This module provides classes to work with filesystem files and directories.
'''
# Imports

# Built-in dependencies

import os
import pathlib
import uuid

# Package dependencies

from geodatabr.formats import FormatRepository, FormatError

# Classes


class Path(type(pathlib.Path())):
    '''
    A filesystem path object.
    '''

    def __enter__(self):
        '''
        Magic method to allow changing the working directory to this path.
        '''
        self._old_dir = self.cwd()
        os.chdir(str(self))

        return self

    def __exit__(self, *_):
        '''
        Magic method to allow changing the working directory to the previous
        path.
        '''
        os.chdir(str(self._old_dir))

    def __contains__(self, segment):
        '''
        Magic method to test if a path segment is in this path.

        Arguments:
            segment (str): A path segment

        Returns:
            bool: Whether or not the given path segment is in this path
        '''
        return segment in str(self)

    def __iter__(self):
        '''
        Magic method to allow iterating this path components.

        Returns:
            iterator: An iterator with this path components
        '''
        return iter(Path(part) for part in self.parts)

    # Properties

    @property
    def atime(self):
        '''
        Returns the path's last access time.
        '''
        return self.stat().st_atime

    @property
    def ctime(self):
        '''
        Returns the path's last change time.
        '''
        return self.stat().st_ctime

    @property
    def gid(self):
        '''
        Returns the path's owner group ID.
        '''
        return self._gid

    @property
    def mode(self):
        '''
        Returns the path's mode.
        '''
        return self.stat().st_mode

    @property
    def mtime(self):
        '''
        Returns the path's last modification time.
        '''
        return self.stat().st_mtime

    @property
    def size(self):
        '''
        Returns the path's size in bytes.
        '''
        return self.stat().st_size

    @property
    def uid(self):
        '''
        Returns the path's owner user ID.
        '''
        return self.stat().st_uid

    # Method aliases

    def join(self, *args):
        '''
        Alias for .joinpath() method.
        '''
        return self.joinpath(*args)

    # Property aliases

    accessed = atime
    accessTime = atime
    changed = ctime
    changeTime = ctime
    groupId = gid
    modificated = mtime
    modificationTime = mtime
    userId = uid

    @property
    def basename(self):
        '''
        Alias for .stem property.
        '''
        return self.stem


class Directory(Path):
    '''
    A filesystem directory object.
    '''

    def create(self, mode=0o777, parents=False):
        '''
        Creates a new directory at this given path.

        Arguments:
            mode (int): The file mode
            parents (bool): Whether the missing parents of this path should be
                created as needed or not

        Returns:
            bool: Whether the directory has been created or not
        '''
        try:
            self.mkdir(mode, parents)

            return True
        except OSError:
            return False

    def directories(self, pattern='*', recursive=False):
        '''
        Yields a generator with all directories matching the given pattern.

        Arguments:
            pattern (str): The search pattern
            recursive (bool): Whether or not it should return directories
                recursively

        Yields:
            A generator with all directories matching the given pattern
        '''
        search_method = self.rglob if recursive else self.glob

        for path in search_method(pattern):
            if path.is_dir():
                yield Directory(path)

    def files(self, pattern='*', recursive=False):
        '''
        Yields a generator with all files matching the given pattern.

        Arguments:
            pattern (str): The search pattern
            recursive (bool): Whether or not it should return files recursively

        Yields:
            A generator with all files matching the given pattern
        '''
        search_method = self.rglob if recursive else self.glob

        for path in search_method(pattern):
            if path.is_file():
                yield File(path)


class CacheDirectory(Directory):
    '''
    A filesystem cache directory object.
    '''

    def __new__(cls, *args, **kwargs):
        '''
        Constructor.
        '''
        return Directory(Path.home() / '.geodatabr', *args, **kwargs)


class File(Path):
    '''
    A filesystem file object.
    '''

    def read(self, **kwargs):
        '''
        Returns the decoded file contents as string.

        Returns:
            str: The file contents
        '''
        with self.open('r', **kwargs) as file_:
            return file_.read()

    def readBytes(self, **kwargs):
        '''
        Returns the decoded file contents as bytes.

        Returns:
            bytes: The file contents
        '''
        with self.open('rb', **kwargs) as file_:
            return file_.read()

    def write(self, data, **kwargs):
        '''
        Opens the file in text mode, write data to it, and closes the file.

        Arguments:
            data (str): The content to be written
        '''
        with self.open('w', **kwargs) as file_:
            file_.write(data)

    def writeBytes(self, data, **kwargs):
        '''
        Opens the file in binary mode, write data to it, and closes the file.

        Arguments:
            data (bytes): The content to be written
        '''
        with self.open('wb', **kwargs) as file_:
            file_.write(data)

    # Properties

    @property
    def extension(self):
        '''
        Returns the file extension.

        Returns:
            str: The file extension
        '''
        return self.suffixes[-1] if self.suffixes else ''

    @property
    def format(self):
        '''
        Returns the file format.

        Returns:
            The file format
        '''
        try:
            return FormatRepository.findByExtension(self.extension)
        except FormatError:
            return None


class CacheFile(File):
    '''
    A filesystem cache file object.
    '''

    def __new__(cls, *args, **kwargs):
        '''
        Constructor.
        '''
        if not args:
            args += (str(uuid.uuid4()),)

        return File(CacheDirectory(), *args, **kwargs)
