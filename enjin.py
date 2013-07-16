#!/usr/bin/python

# Hello world python program
import pygame
import sys
import traceback
import math
import time
import threading
import random

# Thing that connects an input node and an output node.
# Each filter has a pipe for an input when it is created
# The _in value is sent when connected to another filters output.
class Pipe:
    def write(self, data):
        raise NotImplementedError()

    def setState(self, state):
        raise NotImplementedError()

    def getState(self):
         raise NotImplementedError(self)

    '''The filter which writes to this pipe'''
    def getIn(self):
        raise NotImplementedError()

    '''The filter being writtern to'''
    def getOut(self):
        raise NotImplementedError(self)

''' Base class for all filters'''
class Filter:
    def __init__(self, name):
        self._name = name
        self._in = []
        self._out = []

    ''' The >> operator connects two filters'''
    def __rshift__(self, other):
        print "Filter >>"
        self.set_out(other.i())
        print other.name(), "_in = ", self.name()
        return other

    def name(self):
        return self._name

    def i(self):
        return self._in
    
    ''' The ouput pipes '''
    def outs(self):
        return self._out

    def set_out(self, ins):
        print "set_out"
        for i in range(len(ins)):
            self._out[i] = ins[i]
            # tell the pipe who we are i.e double link
            ins[i].setIn(self)

    def __str__(self):
        return  self.name() + " _in: " + str(self._in) + \
        " _out: " + str(self._out)

class S(Filter):
    def __init__(self, s1, s2):
        self._s1 = s1
        self._s2 = s2

    def __rshift__(self, other):
        print "S >>"
        print other.name(), "_in = ", self.name()
        
        count = len(self._s1.outs())
        for i in range(count):
            self._s1.outs()[i] = other.i()[i]
            # tell the pipe who we are
            other.i()[i].setIn(self._s1)

        for j in range(len(self._s2.outs())):
            print i, j
            self._s2.outs()[j] = other.i()[i + count]
            # tell the pipe who we are 
            other.i()[i + count].setIn(self._s2)
           
        return other 

    def i(self):
        _in = self._s2.i()
        _in.extend(self._s1.i())
        return _in

    def name(self):
        return self._s1.name() + ', ' + self._s2.name()

MORE_LATER = "ML"
MORE_NOW = "MN"

class InN(Pipe):
    def __init__(self, filter, inputNum):
        self._filter = filter
        self._state = MORE_NOW
        self._inputNum = inputNum

    def write(self, data):
        self._filter.write(data, self._inputNum)

    def setState(self, state):
        if self.getState() != state:
            self.getIn().setState(state)
            self._state = state

    def getState(self):
        return self._state

    def getOut(self):
        return self._filter

    def getIn(self):
        return self._in

    def setIn(self, filter):
        self._in = filter


def other(input):
    if 1 == input:
        return 0
    return 1
      
class Join(Filter):
    def __init__(self, name):
        self._in = [InN(self, 0), InN(self, 1)]
        self._out = [None]
        self._name = name
        self._tmp = [None, None]
        
    def write(self, data, input):
       print self.name(), "got", data, "from", input
       self._tmp[input] = data
       other_ = self._tmp[other(input)]
       if data == other_:
           self._out[0].write(data)
           # when we write the pipe might call set state which percolates back up
       elif other_ == None or data > other_:
           self._in[input].setState(MORE_LATER)
           self._in[other(input)].setState(MORE_NOW)
       elif data < other_:
           self._in[input].setState(MORE_NOW)
           self._in[other(input)].setState(MORE_LATER)
       else:
          raise Exception()

    def setState(self, state):
        if state == MORE_NOW:
            if self._in[0].getState() == MORE_LATER:
                self._in[0].setState(MORE_NOW)
        elif state == MORE_LATER:
            for i in self._in:
                if i.getState() == MORE_NOW:
                    i.setState(MORE_LATER)

    def getState(self):
        return self._out[0].getState()
    
    def eof(self):
        return True

class Sort(Filter):
    def __init__(self, name):
        self._in = [InN(self, 0)]
        self._out = [None]
        self._name = name
        self._data = []
        self._sorted = False
        self._count = None
       
    # Sort must wait until it has seen all the data
    # befor it can sort it
    def write(self, data, inputNum):
        self._data.append(data)

    def prod(self, data):
        if not self._sorted:
            self._data.sort()
            self._len = len(self._data)
            self._count = 0
            self._sorted= True

        if not self.eof():
            self._out[0].write(self._data[self._count])
            self._count += 1
        
    def eof(self):
        if self._count == None :
            return False
        return not self._count < self._len

    def setIn(self, filter):
        self._inFilter = filter

    def getState(self):
        return self._in[0].getState()

class Partition(Filter):
    def __init__(self, name):
        self._in = [InN(self,0)]
        self._out = [None, None]
        self._name = name

    def write(self, data, inputNum):
        if data % 2 == 0:
            self._out[0].write(data)
        else:
            self._out[1].write(data)

    '''Set the filter which writes to this pipe '''
    def setIn(self, filter):
        self._inFilter = filter

    ''' Partition never holds data so eof is always true'''
    def eof(self):
        return True

    def getState(self):
        if any(o.getState() == MORE_LATER for o in self._out):
            return MORE_LATER
        return MORE_NOW


        

class FileIn(Filter):
    def __init__(self, name, data):
        self._out = [None]
        self._in = []
        self._name = name
        self._i = 0
        self._len = len(data)
        self._data = data
        self._state = MORE_NOW

    def prod(self, var):
        if not self.eof():
            self._out[0].write(self._data[self._i])
            self._i += 1


    def setState(self, state):
        self._state = state

    def getState(self):
        print self.name(), "getState", self._state
        return self._state

    def eof(self):
        return not (self._i < self._len)

class FileOut(Filter, Pipe):
    def __init__(self, name):
        self._out = []
        self._in = [self]
        self._name = name
        self._data = []

    def write(self, data):
       self._data.append(data)

    def get_data(self):
        return self._data
    
    ''' An output file always wants more'''
    def getState(self):
        return MORE_NOW;

    def setIn(self, filter):
        self._inIn = filter

    def getIn(self):
        return self._inIn

    # An output file does not have outputs
    def getOut(self):
        return None


class Enjin(object):
    def __init__(self, ins_tuple):
        self._ins = ins_tuple

    def start(self):
        print
        print "Enjin", "start()", self._ins
        n = 0
        while True:
            for i in self._ins:
                while i.getState() == MORE_NOW and not i.eof():
                    i.prod(n)

            if all(j.eof() for j in self._ins):
                print 'eofed'
                break

            if all(k.getState() == MORE_LATER for k in self._ins):
                raise Exception("FUCK! all the inputs say more later!")
                break

        # We get here when the inputs are eof
        tmp = []
        for i in self._ins:
            for j in i.outs():
                if j.getOut() != None:
                    tmp.append(j.getOut())

        print "tmp", tmp

        # If they have any children we try to prod them
        if len(tmp) > 0:
            self._ins = tmp
            self.start()
        else:
            print "We have reached the end"

        print 'LEAVING START'
            
            

import unittest

class TestEnjin(unittest.TestCase):

    def testJoin(self):
        customers = FileIn('customers', (1, 3, 4, 5, 5, 7, 8, 10))
        orders = FileIn('orders', (5, 6, 7, 7, 10))
        join_by_cid = Join('join_by_cid')
        cust_orders = FileOut('cust_orders')

        S(customers, orders) >> join_by_cid >> cust_orders

        enjin = Enjin((customers, orders))
        enjin.start()
        self.assertEqual(cust_orders.get_data(), [5, 5, 7, 7, 10])

    def testJoinJoin(self):
        customers = FileIn('customers', (1, 3, 4, 5, 7, 8, 10))
        orders = FileIn('orders', (5, 6, 7, 7, 10))
        items = FileIn('items', (6, 7, 8))
        join1 = Join('join_cust_orders')
        join2 = Join('join_with_items')
        output = FileOut('output')

        S(customers, orders) >> join1 
        S(join1, items) >> join2 >> output

        enjin = Enjin((customers, orders, items))
        enjin.start()
        self.assertEqual(output.get_data(), [ 7])

    def testPartition(self):
        part_by_id = Partition('part_by_id')
        items = FileIn('items', [n + 1  for n in range(10)])
        odds = FileOut('odds')
        evens = FileOut('evens')

        items >> part_by_id >> S(odds, evens)

        enjin = Enjin((items,))
        enjin.start()
        self.assertEqual(evens.get_data(), [2, 4, 6, 8, 10])
        self.assertEqual(odds.get_data(), [1, 3, 5, 7, 9])

    def testSort(self):
        primes = FileIn('primes', [11, 2, 17, 5, 23, 19])
        sorted_primes = FileOut('sorted_primes')

        primes >> Sort('sort') >> sorted_primes

        enjin = Enjin((primes,))
        enjin.start()
        self.assertEqual(sorted_primes.get_data(), [2, 5, 11, 17, 19, 23])

    

    
    

try:
    unittest.main()
except Exception, e:
    tb = sys.exc_info()[2]
    traceback.print_exception(e.__class__, e, tb)

pygame.quit()
