#!/usr/bin/python
   
import unittest
from enjin.enjin import *

def lt(data1, data2):
    return data1 < data2

class TestEnjin(unittest.TestCase):

    def testJoin(self):
        customers = FileIn('customers', (1, 3, 4, 5, 5, 7, 8, 10))
        orders = FileIn('orders', (5, 6, 7, 7, 10))
        join_by_cid = Join('join_by_cid', lt)
        cust_orders = FileOut('cust_orders')

        S(customers, orders) >> join_by_cid >> cust_orders

        enjin = Enjin((customers, orders))
        enjin.start()
        self.assertEqual(cust_orders.get_data(), [5, 5, 7, 7, 10])

    def testJoinJoin(self):
        customers = FileIn('customers', (1, 3, 4, 5, 7, 8, 10))
        orders = FileIn('orders', (5, 6, 7, 7, 10))
        items = FileIn('items', (6, 7, 8))
        join1 = Join('join_cust_orders', lt)
        join2 = Join('join_with_items', lt)
        output = FileOut('output')

        S(customers, orders) >> join1 
        S(join1, items) >> join2 >> output

        enjin = Enjin((customers, orders, items))
        enjin.start()
        self.assertEqual(output.get_data(), [ 7])

    def testPartition(self):

        def func(data):
            return data % 2

        part_by_id = Partition('part_by_id', func)
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

    def testAggregate(self):
        def groupBy(data):
            return data % 2
        
        def agg(data, state):
            state.count += 1

        def init(data):
            state.count = 0

        def out(key, state):
            if key == 0:
                return {'Odds': state.count}
            else:
                return {'Evens': state.count}
             
         
        nums = FileIn('numbers', [n + 1  for n in range(11)])
        counts = FileOut('counts')

        nums >> Aggregate('count odds and evens', func) >> counts

        enjin = Enjin((nums,))
        enjin.start()
    
        self.assertEqual(counts.get_data(), {'Odds': 6, 'Evens': 5})   

