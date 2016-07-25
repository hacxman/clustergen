#/usr/bin/env python

import time
import libparser
import sys
import numpy as np

R = {'U': ( 1, 0, 0, -1),
     'D': ( -1, 0, 0, 1),
     'L': (0, -1, -1, 0),
     'R': (0, 1, 1, 0)}

def rotate_by_chars(a, b):
    l = {'U': 0, 'R': 1, 'D': 2, 'L': 3}
    ll = {0: 'U', 1: 'R', 2: 'D', 3: 'L'}
#    ll = {0: 'R', 1: 'U', 2: 'L', 3: 'D'}
#    r = {'L': '2', 'R': '0', 'U':'1', 'D':'3'}
    return ll[(l[a]+l[b])%4]

def diff_by_chars(a, b):
    l = {'U': 0, 'R': 1, 'D': 2, 'L': 3}
    ll = {0: 'U', 1: 'R', 2: 'D', 3: 'L'}
#    ll = {0: 'R', 1: 'U', 2: 'L', 3: 'D'}
#    r = {'L': '2', 'R': '0', 'U':'1', 'D':'3'}
    return ll[(l[a]-l[b])%4]

__timestamp = int(time.time())
def get_timestamp():
    global __timestamp
    __timestamp+=1
    return hex(__timestamp)

class Component(object):
    def __init__(self, part, lib):
        self.instance = ''
        self.part = part
        self.library = lib
        self.element = lib.get_by_name(part)
        self.x = 0
        self.y = 0
        self.r = 'U'
        self.connected = []
        self.groups = set() #component groups, like classes in CSS
        if len(self.element.pins.values()) in [1,2]:
            print self.element.pins.values()
            #r = self.element.pins.values()[0][0][4]
            #self.r = {'L': 'R', 'R': 'L', 'U':'D', 'D':'U'}[r]
            print self.instance, self.r

    def footprint(self):
        return self.element.footprint

    def get_pin_pos(self, pin):
        x,y = self.element.pin_by_id(pin)[2:4]
        print 'pinpos',x,y
        print (R[self.r][0:2], R[self.r][2:4])
        r = np.matrix( (R[self.r][0:2], R[self.r][2:4]) )
        p = np.matrix((x, y))
        m = p * r
        x = m[0,0]
        y = m[0,1]
        return [x, y]

    def show(self):
        o = ''
        for p in self.element.pins_i:
            if not (p in self.connected):
                print self.instance, p, self.connected
                pin = self.element.pin_by_id(p)
                o += """NoConn ~ {} {}
""".format(self.x+self.get_pin_pos(p)[0], self.y+self.get_pin_pos(p)[1])
#    -1  0   0   1
#    0 -1    1 0
        return o+"""$Comp
L {} {}
U 1 1 {}
P {} {}
F 0 "{}" H {} {} 60 0 C CNN
    1   {}  {}
    {}  {}   {}   {}
$EndComp
""".format(self.part, self.instance,
        get_timestamp()[2:].upper(),
        self.x, self.y,
        self.instance, self.x-20, self.y-50,
        self.x, self.y,
        R[self.r][0], R[self.r][1], R[self.r][2], R[self.r][3])

class Netlabel(object):
    def __init__(self):
        self.name = ''
        self.part = 'Netlabel'
        self.x = 0
        self.y = 0
        self.r = 'R'
        self.connected = []
        self.element = self
        self.pins = {'1': []}
        self.pins_i = {'1': []}
        self.groups = set()

    def footprint(self):
        return ''

    def pin_by_id(self, pin):
        return (self.name, '1', self.x, self.y, rotate_by_chars('U', self.r))

    def set_name(self, name):
        self.name = name
        self.pins[1] = self.name

    def get_pin_pos(self, pin):
        return [0, 0]

    def show(self):
        #r = {'L': '0', 'R': '2', 'U':'3', 'D':'1'}[self.r]
        r = {'L': '2', 'R': '0', 'U':'3', 'D':'1'}[self.r]
        return """Text Label {} {} {} {} ~
{}
""".format(self.x, self.y, (int(r)+0)%4, 20*len(self.name), self.name)

class Schematic(object):
    def show_header(self):
        return """EESchema Schematic File Version 1
{} 
EELAYER 00 00
EELAYER END
$Descr A3 16535 11700
Sheet 1 1
""
Date "{}"
Rev "1"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 "autogenerated"
$EndDescr
""".format('LIBS: '+'\nLIBS: '.join(self.lib.libnames),
        time.asctime())

    def __init__(self):
        self.lib = libparser.Library()
        self.lib.import_dir('/usr/share/kicad/library/')
        self.components = {}
        self.nets = {}
        self.nets_pos = {}
        self.group_names = set()
        self._current_group = ''

    def begin_group(self, name):
        self._current_group = name
        self.group_names |= {name}

    def end_group(self):
        self._current_group = ''

    def get_group(self, name):
        out = []
        for c in self.components:
            if name in self.components[c].groups:
                out.append(c)
        return out

    def save(self, filename):
        with open(filename, 'w+') as fout:
            fout.write(self.show_header())
            for c in self.components:
                fout.write(self.components[c].show())
            fout.write('$EndSCHEMATIC')

    def count_components_by_ref(self, ref):
        return len(filter(lambda x: x.startswith(ref), self.components))

    def add_component(self, part):
        c = Component(part, self.lib)
        inst = '{}{}'.format(c.element.reference, 1 + self.count_components_by_ref(c.element.reference))
        self.components.update({inst: c})
        c.instance = inst
        c.groups |= {self._current_group}
        return inst

    def get_by_inst(self, inst):
        return self.components[inst]

    def add_net(self, netname, what):
        if not self.nets.has_key(netname):
            self.nets[netname] = []
        self.nets[netname].append( what )
        #self.nets_pos[
        #        self.get_by_inst(what[0]).x,
        #        self.get_by_inst(what[0]).y
        #        ].append( (netname, what) )


    def connect_pin_to_pin(self, cwhat, cwhere, pinwhat, pinwhere):
        ca = self.get_by_inst(cwhat)
        cb = self.get_by_inst(cwhere)
        netname = ''
        if len(ca.element.pins_i) == 1:
            netname = ca.element.name
            print 'OTHER PIN NAMES OF {} :'.format(cwhat), ca.element.pins
        elif len(cb.element.pins) == 1:
            netname = cb.element.name
            print 'OTHER PIN NAMES OF {} :'.format(cwhere), cb.element.pins
        else:
            netname = get_timestamp()
        print 'RESULTING NETNAME IS', netname
        rpin = self.get_by_inst(cwhere).element.pin_by_id(pinwhere)[4]
        rpinw = self.get_by_inst(cwhat).element.pin_by_id(pinwhat)[4]
        print 'CONNECTING {} -> {}, {} -> {}'.format(cwhat, cwhere, rpin, rpinw)
        print '{} - {} = {}'.format(rpinw, rpin, diff_by_chars(rpinw, rpin))
        print ' _ + {} = {}'.format(self.get_by_inst(cwhat).r, rotate_by_chars(diff_by_chars(rpinw, rpin), self.get_by_inst(cwhat).r))
        self.get_by_inst(cwhat).r = rotate_by_chars(self.get_by_inst(cwhat).r, 
                diff_by_chars(rotate_by_chars(rpin, self.get_by_inst(cwhere).r),
                              rotate_by_chars('D',rotate_by_chars(rpinw, self.get_by_inst(cwhat).r))))
        c1 = self.get_by_inst(cwhat).get_pin_pos(pinwhat)
        c2 = self.get_by_inst(cwhere).get_pin_pos(pinwhere)

        x = self.get_by_inst(cwhere).x
        y = self.get_by_inst(cwhere).y
        print c1, c2
        self.get_by_inst(cwhat).x = c2[0] + x - c1[0]
        self.get_by_inst(cwhat).y = c2[1] + y - c1[1]

        self.get_by_inst(cwhat).connected.append(pinwhat)
        self.get_by_inst(cwhere).connected.append(pinwhere)

        self.add_net(netname, (cwhat, pinwhat))
        self.add_net(netname, (cwhere, pinwhere))

        print self.get_by_inst(cwhat).x
        print self.get_by_inst(cwhat).y

    def connect_netlabel(self, netname, cwhere, pin):
        c = Netlabel()
        c.set_name(netname)
        cnt = 1 + self.count_components_by_ref('LABEL')
        inst = '{}{}'.format('LABEL',cnt)
        self.components.update({inst: c})
        self.connect_pin_to_pin(inst, cwhere, '0', pin)
        c.r = rotate_by_chars(c.r, 'R')
        return inst

    def connect_part_to_GND(self, partname, cwhere, pin):
        r = self.add_component(partname)
        gnd = self.add_component('GND')
        self.connect_pin_to_pin(r, cwhere, '1', pin)
        self.connect_pin_to_pin(gnd, r, '1', '2')

    def connect_R_to_GND(self, cwhere, pin):
        r = self.add_component('R_Small')
        gnd = self.add_component('GND')
        print 'connect_R_to_GND:', cwhere
        self.connect_pin_to_pin(r, cwhere, '2', pin)
        self.connect_pin_to_pin(gnd, r, '1', '1')
        return r

    def connect_to_GND(self, what, pin):
        gnd = self.add_component('GND')
        self.connect_pin_to_pin(gnd, what, '1', pin)


if __name__ == '__main__':
    sch = Schematic()
#    print sch.add_component('R')
#    print sch.add_component('R')
#    print sch.add_component('R')
#    sch.get_by_inst('R1').x = 100
#    sch.get_by_inst('R2').x = 200
#    sch.get_by_inst('R3').x = 400
#    sch.connect_pin_to_pin('R2', 'R3', '1', '2')
#    sch.connect_pin_to_pin('R1', 'R2', '1', '2')
    print sch.lib.lookup('F050')
    CNT = 5

    pwr = sch.add_component('CONN_01X02')
    print pwr
    sch.get_by_inst(pwr).x = -5000
    sch.get_by_inst(pwr).y = 0
    VCC = sch.add_component('VCC')
    sch.connect_pin_to_pin(VCC, pwr, '1', '1')
    gnd = sch.add_component('GND')
    sch.connect_pin_to_pin(gnd, pwr, '1', '2')

    gnd = sch.add_component('GND')
    flg = sch.add_component('PWR_FLAG')
    sch.get_by_inst(flg).x = -5000
    sch.get_by_inst(flg).y = 1000
    sch.connect_pin_to_pin(gnd, flg, '1', '1')

    vcc = sch.add_component('VCC')
    flg = sch.add_component('PWR_FLAG')
    sch.get_by_inst(flg).x = -4500
    sch.get_by_inst(flg).y = 1000
    sch.connect_pin_to_pin(vcc, flg, '1', '1')
    

    uart = sch.add_component('CONN_01X03')
    sch.get_by_inst(uart).x = -5000
    sch.get_by_inst(uart).y = 2000
    gnd = sch.add_component('GND')
    sch.connect_pin_to_pin(gnd, uart, '1', '3')
    sch.connect_netlabel('S00R', uart, '1')
    sch.connect_netlabel('S00T', uart, '2')

    for x in range(CNT):
        for y in range(CNT):
            ci = sch.add_component('STM32F050C4') #'STM32F100VB') #'STM32F417VE') #'STM32F050C4')
            i = sch.get_by_inst(ci)
            c_off = i.element.get_size()
            i.x = int(x*(c_off[0]+4000))
            i.y = int(y*(c_off[1]+4000))
            gnd = sch.add_component('GND')
            sch.connect_pin_to_pin(gnd, ci, '1', '47')
            gnd = sch.add_component('GND')
            sch.connect_pin_to_pin(gnd, ci, '1', '23')
            gnd = sch.add_component('GND')
            sch.connect_pin_to_pin(gnd, ci, '1', '8')

            VCC = sch.add_component('VCC')
            sch.connect_pin_to_pin(VCC, ci, '1', '48')
            VCC = sch.add_component('VCC')
            sch.connect_pin_to_pin(VCC, ci, '1', '24')
            VCC = sch.add_component('VCC')
            sch.connect_pin_to_pin(VCC, ci, '1', '9')

            sch.connect_R_to_GND(ci, '7')
#            for i in range(40, 46):
#                sch.connect_R_to_GND(ci, str(i))
#            for i in range(13, 20):
#                sch.connect_part_to_GND('LED', ci, str(i))
    m = [[0] * CNT + [1] for x in range(CNT)] + [[1]*(CNT+1)]
    print m
    V = {0: (1, 0), 1: (0, 1), 2: (-1, 0), 3: (0, -1)}
    p = [0,0]
    v = 0
    L = {'U': 0, 'R': 1, 'D': 2, 'L': 3}
    #L = {'U': 3, 'R': 2, 'D': 1, 'L': 0}
    for i in range(CNT**2):
        idx = p[0] + p[1]*CNT
        sch.connect_netlabel('S{}{}R'.format(p[0], p[1]), 'U{}'.format(idx+1), '12')
        sch.connect_netlabel('S{}{}T'.format(p[0], p[1]), 'U{}'.format(idx+1), '13')
        m[p[0]][p[1]] = 1
        pp = [p[0]+V[v][0], p[1]+V[v][1]]
        if m[pp[0]][pp[1]] == 1:
            v += 1
            v %= 4
            pp = [p[0]+V[v][0], p[1]+V[v][1]]
        p = pp
        sch.connect_netlabel('S{}{}R'.format(p[0], p[1]), 'U{}'.format(idx+1), '37')
        sch.connect_netlabel('S{}{}T'.format(p[0], p[1]), 'U{}'.format(idx+1), '38')


    for y in range(CNT):
        for x in range(CNT):
            led = sch.add_component('LED')
            l = sch.get_by_inst(led)

            n = sch.connect_netlabel('NWA{}{}'.format(x,y), 'U{}'.format(1+x+y*CNT), '5')
            l.r = rotate_by_chars('L', sch.get_by_inst(n).r)
            l.x = sch.get_by_inst(n).x + int(0.4*V[L[l.r]][0]*2000)
            l.y = sch.get_by_inst(n).y + V[L[l.r]][1]*500 + 800
            sch.connect_netlabel('NWA{}{}'.format(x,y), led, '2')
            sch.connect_R_to_GND(led, '1')

            led = sch.add_component('LED')
            l = sch.get_by_inst(led)

            n = sch.connect_netlabel('NWB{}{}'.format(x,y), 'U{}'.format(1+x+y*CNT), '6')
            l.r = rotate_by_chars('L', sch.get_by_inst(n).r)
            l.x = sch.get_by_inst(n).x + int(0.4*(V[L[l.r]][0])*2000)
            l.y = sch.get_by_inst(n).y + (2*V[L[l.r]][1])*500 + 800
            sch.connect_netlabel('NWB{}{}'.format(x,y), led, '2')
            sch.connect_R_to_GND(led, '1')

            led = sch.add_component('LED')
            l = sch.get_by_inst(led)

            n = sch.connect_netlabel('NEA{}{}'.format(x,y), 'U{}'.format(1+x+y*CNT), '35')
            l.r = rotate_by_chars('L', sch.get_by_inst(n).r)
            l.x = sch.get_by_inst(n).x + int(0.4*(V[L[l.r]][0])*2000)
            l.y = sch.get_by_inst(n).y + (3*V[L[l.r]][1])*500 + 800
            print 'L.r = ', l.r, ' rot', V[L[l.r]]
            sch.connect_netlabel('NEA{}{}'.format(x,y), led, '2')
            sch.connect_R_to_GND(led, '1')

            led = sch.add_component('LED')
            l = sch.get_by_inst(led)

            n = sch.connect_netlabel('NEB{}{}'.format(x,y), 'U{}'.format(1+x+y*CNT), '36')
            l.r = rotate_by_chars('L', sch.get_by_inst(n).r)
            l.x = sch.get_by_inst(n).x + int(0.4*(V[L[l.r]][0])*2000)
            l.y = sch.get_by_inst(n).y + (4*V[L[l.r]][1])*500 + 800
            sch.connect_netlabel('NEB{}{}'.format(x,y), led, '2')
            sch.connect_R_to_GND(led, '1')



            led = sch.add_component('LED')
            l = sch.get_by_inst(led)
            n = sch.connect_netlabel('NSA{}{}'.format(x,y), 'U{}'.format(1+x+y*CNT), '18')
            l.r = rotate_by_chars('L', sch.get_by_inst(n).r)
            l.x = sch.get_by_inst(n).x + int(0.7*V[L[l.r]][0]*2000)
            l.y = sch.get_by_inst(n).y + V[L[l.r]][1]*500 + 800
            sch.connect_netlabel('NSA{}{}'.format(x,y), led, '2')
            sch.connect_R_to_GND(led, '1')

            led = sch.add_component('LED')
            l = sch.get_by_inst(led)

            n = sch.connect_netlabel('NSB{}{}'.format(x,y), 'U{}'.format(1+x+y*CNT), '19')
            l.r = rotate_by_chars('L', sch.get_by_inst(n).r)
            print 'L.r = ', l.r, ' rot', V[L[l.r]]
            l.x = sch.get_by_inst(n).x + int(0.7*V[L[l.r]][0]*2000)
            l.y = sch.get_by_inst(n).y + (2*V[L[l.r]][1]*500) + 800
            sch.connect_netlabel('NSB{}{}'.format(x,y), led, '2')
            sch.connect_R_to_GND(led, '1')

            led = sch.add_component('LED')
            l = sch.get_by_inst(led)

            n = sch.connect_netlabel('NNA{}{}'.format(x,y), 'U{}'.format(1+x+y*CNT), '42')
            l.r = rotate_by_chars('L', sch.get_by_inst(n).r)
            l.x = sch.get_by_inst(n).x + int(0.7*V[L[l.r]][0]*2000)
            l.y = sch.get_by_inst(n).y + (3*V[L[l.r]][1]*500) + 800
            sch.connect_netlabel('NNA{}{}'.format(x,y), led, '2')
            sch.connect_R_to_GND(led, '1')

            led = sch.add_component('LED')
            l = sch.get_by_inst(led)

            n = sch.connect_netlabel('NNB{}{}'.format(x,y), 'U{}'.format(1+x+y*CNT), '43')
            l.r = rotate_by_chars('L', sch.get_by_inst(n).r)
            l.x = sch.get_by_inst(n).x + int(0.7*V[L[l.r]][0]*2000)
            l.y = sch.get_by_inst(n).y + (4*V[L[l.r]][1]*500) + 800
            sch.connect_netlabel('NNB{}{}'.format(x,y), led, '2')
            sch.connect_R_to_GND(led, '1')




            sch.connect_netlabel('NWA{}{}'.format(x,y), 'U{}'.format(1+((x+1)%CNT)+y*CNT), '30')
            sch.connect_netlabel('NWB{}{}'.format(x,y), 'U{}'.format(1+((x+2)%CNT)+y*CNT), '31')
            sch.connect_netlabel('NEA{}{}'.format(x,y), 'U{}'.format(1+((x-1)%CNT)+y*CNT), '10')
            sch.connect_netlabel('NEB{}{}'.format(x,y), 'U{}'.format(1+((x-2)%CNT)+y*CNT), '11')

            sch.connect_netlabel('NSA{}{}'.format(x,y), 'U{}'.format(1+x+((y+1)%CNT)*CNT), '40')
            sch.connect_netlabel('NSB{}{}'.format(x,y), 'U{}'.format(1+x+((y+2)%CNT)*CNT), '41')
            sch.connect_netlabel('NNA{}{}'.format(x,y), 'U{}'.format(1+x+((y-1)%CNT)*CNT), '21')
            sch.connect_netlabel('NNB{}{}'.format(x,y), 'U{}'.format(1+x+((y-2)%CNT)*CNT), '22')

#            r = sch.add_component('R_Small')
#            gnd = sch.add_component('GND')
#            sch.connect_pin_to_pin(r, ci, '2', '7')
#            sch.connect_pin_to_pin(gnd, r, '1', '2')
#
#            r = sch.add_component('R_Small')
#            gnd = sch.add_component('GND')
#            sch.connect_pin_to_pin(r, ci, '2', '43')
#            sch.connect_pin_to_pin(gnd, r, '1', '2')

#            gnd = sch.add_component('GND')
#            sch.connect_pin_to_pin(gnd, ci, '1', '12')
#            sch.connect_netlabel('YOLO', ci, '25')
#            sch.connect_netlabel('YOLO', ci, '26')
    sch.save(sys.argv[1])
