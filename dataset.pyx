from libc.stdio cimport fscanf, fdopen, fseek, ftell, FILE, SEEK_SET, SEEK_CUR
from posix.mman cimport mmap, munmap, PROT_READ, MAP_PRIVATE
from libc.stdlib cimport strtod
from posix.stat cimport fstat, struct_stat
from posix.types cimport off_t
cimport numpy as np
cimport cython

__all__ = ['read_iccap_dataset']

@cython.cdivision(True)
cdef int ndigits(int number, int base):
    cdef int ret = 0
    while True:
        ret += 1
        number = number // base
        if number == 0:
            break
    return ret

cdef off_t filelength(int fileno):
    cdef struct_stat stat_;
    fstat(fileno, &stat_);
    return stat_.st_size;

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def read_iccap_dataset(int fileno, unsigned int offset, double[:,:] dest):
    cdef int skip = 11
    cdef off_t length = filelength(fileno);

    cdef void *base = mmap(NULL, length, PROT_READ, MAP_PRIVATE, fileno, 0)
    cdef char *readptr = <char *> base + offset
    cdef int index, npoints = dest.shape[0]
    for index in range(npoints):
        if readptr[:6] != b'point ':
            # Missing data
            break
        # Skip 'point NN 1 1 '
        readptr += 11 + ndigits(index, 10)
        dest[index,0] = strtod(readptr, &readptr)
        dest[index,1] = strtod(readptr+1, &readptr)
        # Skip \r\n
        readptr += 2
    munmap(base, length)
    return readptr - (<char*>base + offset)

