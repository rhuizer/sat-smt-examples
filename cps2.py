#!/usr/bin/env python

import struct
import itertools
import z3

z3.init('/usr/lib64/python2.7/site-packages/z3/')

fn2_groupA = [ 6, 0, 2, 13, 1,  4, 14,  7 ]
fn2_groupB = [ 3, 5, 9, 10, 8, 15, 12, 11 ]

class CPS2SBox(object):
    def __init__(self, name, *args, **kwargs):
        self._name   = name
        self._sboxes = args

    def inputs(self, sbox_index):
        for i in self._sboxes[sbox_index]['in']:
            yield i

    def outputs(self, sbox_index):
        for o in self._sboxes[sbox_index]['out']:
            yield o

    def sbox(self, sbox_index):
        return self._sboxes[sbox_index]['sbox']

    def to_z3(self, sbox_index):
        name = "{}_{}".format(self._name, sbox_index)
        lut = z3.Array(name, z3.BitVecSort(6), z3.BitVecSort(2))
        constraints = [lut[i] == self.sbox(sbox_index)[i] for i in range(2**6)]
        return lut, constraints

    def inputs_z3(self, data, sbox_index):
        inputs = [z3.Extract(i, i, data) for i in self.inputs(sbox_index)]
        if len(inputs) < 6:
            inputs[-1] = z3.ZeroExt(6 - len(inputs), inputs[-1])

        return z3.simplify(z3.Concat(*reversed(inputs)))

    def outputs_z3(self, data, sbox_index):
        assert data.size() == 2

        idx  = 0
        expr = []
        outputs = list(self.outputs(sbox_index))
        for i in range(8):
            if idx < 2 and outputs[idx] == i:
                expr.append(z3.Extract(idx, idx, data))
                idx += 1
            else:
                expr.append(z3.BitVecVal(0, 1))

        return z3.simplify(z3.Concat(*reversed(expr)))

f2_r1_sbox1 = {
    'sbox': [2,0,2,0,3,0,0,3,1,1,0,1,3,2,0,1,2,0,1,2,0,2,0,2,2,2,3,0,2,1,3,0,
             0,1,0,1,2,2,3,3,0,3,0,2,3,0,1,2,1,1,0,2,0,3,1,1,2,2,1,3,1,1,3,1],
    'in'  : [0,3,4,5,7],
    'out' : [6, 7]
}

f2_r1_sbox2 = {
    'sbox': [1,1,0,3,0,2,0,1,3,0,2,0,1,1,0,0,1,3,2,2,0,2,2,2,2,0,1,3,3,3,1,1,
             1,3,1,3,2,2,2,2,2,2,0,1,0,1,1,2,3,1,1,2,0,3,3,3,2,2,3,1,1,1,3,0],
    'in'  : [1,2,3,4,6],
    'out' : [3, 5]
}

f2_r1_sbox3 = {
    'sbox': [1,0,2,2,3,3,3,3,1,2,2,1,0,1,2,1,1,2,3,1,2,0,0,1,2,3,1,2,0,0,0,2,
             2,0,1,1,0,0,2,0,0,0,2,3,2,3,0,1,3,0,0,0,2,3,2,0,1,3,2,1,3,1,1,3],
    'in'  : [1,2,4,5,6,7],
    'out' : [1, 4]
}

f2_r1_sbox4 = {
    'sbox': [1,3,3,0,3,2,3,1,3,2,1,1,3,3,2,1,2,3,0,3,1,0,0,2,3,0,0,0,3,3,0,1,
             2,3,0,0,0,1,2,1,3,0,0,1,0,2,2,2,3,3,1,2,1,3,0,0,0,3,0,1,3,2,2,0],
    'in'  : [0,2,3,5,6,7],
    'out' : [0, 2]
}

f2_r2_sbox1 = {
    'sbox': [3,1,3,0,3,0,3,1,3,0,0,1,1,3,0,3,1,1,0,1,2,3,2,3,3,1,2,2,2,0,2,3,
             2,2,2,1,1,3,3,0,3,1,2,1,1,1,0,2,0,3,3,0,0,2,0,0,1,1,2,1,2,1,1,0],
    'in'  : [0,2,4,6],
    'out' : [4,6]
}

f2_r2_sbox2 = {
    'sbox': [0,3,0,3,3,2,1,2,3,1,1,1,2,0,2,3,0,3,1,2,2,1,3,3,3,2,1,2,2,0,1,0,
             2,3,0,1,2,0,1,1,2,0,2,1,2,0,2,3,3,1,0,2,3,3,0,3,1,1,3,0,0,1,2,0],
    'in'  : [1,3,4,5,6,7],
    'out' : [0,3]
}

f2_r2_sbox3 = {
    'sbox': [0,0,2,1,3,2,1,0,1,2,2,2,1,1,0,3,1,2,2,3,2,1,1,0,3,0,0,1,1,2,3,1,
             3,3,2,2,1,0,1,1,1,2,0,1,2,3,0,3,3,0,3,2,2,0,2,2,1,2,3,2,1,0,2,1],
    'in'  : [0,1,3,4,5,7],
    'out' : [1,7]
}

f2_r2_sbox4 = {
    'sbox': [0,2,1,2,0,2,2,0,1,3,2,0,3,2,3,0,3,3,2,3,1,2,3,1,2,2,0,0,2,2,1,2,
             2,3,3,3,1,1,0,0,0,3,2,0,3,2,3,1,1,1,1,0,1,0,1,3,0,0,1,2,2,3,2,0],
    'in'  : [1,2,3,5,6,7],
    'out' : [2,5]
}

f2_r3_sbox1 = {
    'sbox': [2,1,2,1,2,3,1,3,2,2,1,3,3,0,0,1,0,2,0,3,3,1,0,0,1,1,0,2,3,2,1,2,
             1,1,2,1,1,3,2,2,0,2,2,3,3,3,2,0,0,0,0,0,3,3,3,0,1,2,1,0,2,3,3,1],
    'in'  : [2,3,4,6],
    'out' : [3,5]
}

f2_r3_sbox2 = {
    'sbox': [3,2,3,3,1,0,3,0,2,0,1,1,1,0,3,0,3,1,3,1,0,1,2,3,2,2,3,2,0,1,1,2,
             3,0,0,2,1,0,0,2,2,0,1,0,0,2,0,0,1,3,1,3,2,0,3,3,1,0,2,2,2,3,0,0],
    'in'  : [0,1,3,5,7],
    'out' : [0,2]
}

f2_r3_sbox3 = {
    'sbox': [2,2,1,0,2,3,3,0,0,0,1,3,1,2,3,2,2,3,1,3,0,3,0,3,3,2,2,1,0,0,0,2,
             1,2,2,2,0,0,1,2,0,1,3,0,2,3,2,1,3,2,2,2,3,1,3,0,2,0,2,1,0,3,3,1],
    'in'  : [0,1,2,3,5,7],
    'out' : [1,6]
}

f2_r3_sbox4 = {
    'sbox': [1,2,3,2,0,2,1,3,3,1,0,1,1,2,2,0,0,1,1,1,2,1,1,2,0,1,3,3,1,1,1,2,
             3,3,1,0,2,1,1,1,2,1,0,0,2,2,3,2,3,2,2,0,2,2,3,3,0,2,3,0,2,2,1,1],
    'in'  : [0,2,4,5,6,7],
    'out' : [4,7]
}

f2_r4_sbox1 = {
    'sbox': [2,0,1,1,2,1,3,3,1,1,1,2,0,1,0,2,0,1,2,0,2,3,0,2,3,3,2,2,3,2,0,1,
             3,0,2,0,2,3,1,3,2,0,0,1,1,2,3,1,1,1,0,1,2,0,3,3,1,1,1,3,3,1,1,0],
    'in'  : [0,1,3,6,7],
    'out' : [0,3]
}

f2_r4_sbox2 = {
    'sbox': [1,2,2,1,0,3,3,1,0,2,2,2,1,0,1,0,1,1,0,1,0,2,1,0,2,1,0,2,3,2,3,3,
             2,2,1,2,2,3,1,3,3,3,0,1,0,1,3,0,0,0,1,2,0,3,3,2,3,2,1,3,2,1,0,2],
    'in'  : [0,1,2,4,5,6],
    'out' : [4,7]
}

f2_r4_sbox3 = {
    'sbox': [2,3,2,1,3,2,3,0,0,2,1,1,0,0,3,2,3,1,0,1,2,2,2,1,3,2,2,1,0,2,1,2,
             0,3,1,0,0,3,1,1,3,3,2,0,1,0,1,3,0,0,1,2,1,2,3,2,1,0,0,3,2,1,1,3],
    'in'  : [0,2,3,4,5,7],
    'out' : [1,2]
}

f2_r4_sbox4 = {
    'sbox': [2,0,0,3,2,2,2,1,3,3,1,1,2,0,0,3,1,0,3,2,1,0,2,0,3,2,2,3,2,0,3,0,
             1,3,0,2,2,1,3,3,0,1,0,3,1,1,3,2,0,3,0,2,3,2,1,3,2,3,0,0,1,3,2,1],
    'in'  : [2,3,4,5,6,7],
    'out' : [5,6]
}

class CPS2Solver(object):
    def __init__(self):
        self.solver     = z3.Solver()

        # Initialize the sboxes we'll use.
        self.f2_sbox = []
        self.f2_sbox.append(CPS2SBox('f2_r1_sbox', f2_r1_sbox1, f2_r1_sbox2, f2_r1_sbox3, f2_r1_sbox4))
        self.f2_sbox.append(CPS2SBox('f2_r2_sbox', f2_r2_sbox1, f2_r2_sbox2, f2_r2_sbox3, f2_r2_sbox4))
        self.f2_sbox.append(CPS2SBox('f2_r3_sbox', f2_r3_sbox1, f2_r3_sbox2, f2_r3_sbox3, f2_r3_sbox4))
        self.f2_sbox.append(CPS2SBox('f2_r4_sbox', f2_r4_sbox1, f2_r4_sbox2, f2_r4_sbox3, f2_r4_sbox4))

        # And add their symbolic expressions.
        self.sboxes = {}
        for sbox in self.f2_sbox:
            self.sboxes[sbox] = []

            for idx in range(4):
                lut, constraints = sbox.to_z3(idx)
                self.sboxes[sbox].append(lut)

                # Add all the constraints for this sbox to the solver.
                for c in constraints:
                    self.solver.add(c)

    def fn(self, inp, sbox, key):
        assert inp.size() == 8
        assert key.size() == 24

        # Get the symbolic expressions for the key parts.
        k1 = z3.Extract( 5,  0, key)
        k2 = z3.Extract(11,  6, key)
        k3 = z3.Extract(17, 12, key)
        k4 = z3.Extract(23, 18, key)

        # Get symbolic expressions for different 6-bit input sets.
        i1 = sbox.inputs_z3(inp, 0)
        i2 = sbox.inputs_z3(inp, 1)
        i3 = sbox.inputs_z3(inp, 2)
        i4 = sbox.inputs_z3(inp, 3)

        # Get symbolic expressions for all sboxes.
        s1 = self.sboxes[sbox][0]
        s2 = self.sboxes[sbox][1]
        s3 = self.sboxes[sbox][2]
        s4 = self.sboxes[sbox][3]

        # Get the output variables as separate 8-bit quantities.
        o1 = sbox.outputs_z3(s1[i1 ^ k1], 0)
        o2 = sbox.outputs_z3(s2[i2 ^ k2], 1)
        o3 = sbox.outputs_z3(s3[i3 ^ k3], 2)
        o4 = sbox.outputs_z3(s4[i4 ^ k4], 3)

        # Compose and simplify them.
        return z3.simplify(o1 | o2 | o3 | o4)

    def feistel(self, inp, key):
        assert key.size() == 96

        # Partition the key into batches of 24 bits.
        k1 = z3.Extract(23,  0, key)
        k2 = z3.Extract(47, 24, key)
        k3 = z3.Extract(71, 48, key)
        k4 = z3.Extract(95, 72, key)

        l = [ z3.Extract(b, b, inp) for b in reversed(fn2_groupB) ]
        l = z3.Concat(l)

        r = [ z3.Extract(a, a, inp) for a in reversed(fn2_groupA) ]
        r = z3.Concat(r)

        l ^= self.fn(r, self.f2_sbox[0], k1)
        r ^= self.fn(l, self.f2_sbox[1], k2)
        l ^= self.fn(r, self.f2_sbox[2], k3)
        r ^= self.fn(l, self.f2_sbox[3], k4)

        # Collect all bits for the return value.
        ret_in  = [ z3.Extract(i, i, l) for i in range(8) ]
        ret_in += [ z3.Extract(i, i, r) for i in range(8) ]

        # Apply the shuffle from groupA and B.
        ret = [None] * 16
        for i, b in enumerate(fn2_groupA + fn2_groupB):
            ret[b] = ret_in[i]

        return z3.simplify(z3.Concat(*reversed(ret)))

cps2 = CPS2Solver()

key = z3.BitVec('key', 96)

pairs = [(0xbeef, 0x2478), (0xbabe, 0x1e4a), (0x4491, 0x57ea), (0x1234, 0x233f), (0x9876, 0x6583), (0xfab4, 0x209e)]
for i, (pt, ct) in enumerate(pairs):
    name = "pt_{:02}".format(i)
    bv   = z3.BitVec(name, 16)
    cps2.solver.add(bv == pt)
    cps2.solver.add(cps2.feistel(bv, key) == ct)

#solver.add(key == 0)
if cps2.solver.check() == z3.sat:
    m = cps2.solver.model()
    print "key:", hex(m.evaluate(key).as_long())
else:
    print "UNSAT"
