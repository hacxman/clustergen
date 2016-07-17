#!/usr/bin/env python
import sys, os

class Element(object):
    def __init__(self):
        self.name = ''
        self.pins = {}
        self.pins_i = {}
        self.reference = ''

    def parse_pin(self, line):
        l = line.split()
        name, num = l[1], l[2]
        ori = dict([('U', (0, -1)),
               ('D', (0,  1)),
               ('L', (+1, 0)),
               ('R', (1, 0))])
        r = l[6] #orientation
        lenght = int(l[5])
        x = int(l[3]) #- int(ori[l[6]][0]) * lenght
        y = int(l[4]) #- int(ori[l[6]][1]) * lenght
        return (name, num, x, y, r)

    def add_pin(self, line):
        p = self.parse_pin(line)
        name = p[0]
        idx = p[1]
        if self.pins.has_key(name):
            self.pins[name].append(p)
        else:
            self.pins[name] = [p]
        self.pins_i[idx] = p

    def pin_by_name(self, name):
        return self.pins[name]

    def pin_by_id(self, idx):
        return self.pins_i[idx]

    def show(self):
        return "{}\n{}\n".format(self.name,
                '\n'.join(map(lambda x: str(x) + ': ' +str(self.pins_i[x]), self.pins_i)))

    def get_size(self):
        mx = 0
        my = 0
        nx, ny = 0, 0
        for x,y in self.pins.values():
            mx, nx = max(mx, x), min(nx, x)
            my, ny = max(my, y), min(ny, y)
        return mx-nx, my-ny


lines_count = 0
def parse_file(filename):
    global lines_count
    parser_mode = [0]

    elements = {}
    with open(filename) as fin:
        element = None
        for lnum, l in enumerate(fin.readlines()):
            lines_count += 1
            try:
                if parser_mode[-1] == 0 and l.startswith('DEF'):
                    parser_mode.append('def')
                    elename, ref = l.split()[1:3]
                    element = Element()
                    element.name = elename
                    element.reference = ref
                if parser_mode[-1] == 'def' and l.startswith('ENDDEF'):
                    parser_mode.pop()
                    elements[element.name] = element
                if parser_mode[-1] == 'def' and l.startswith('DRAW'):
                    parser_mode.append('draw')
                if parser_mode[-1] == 'draw' and l.startswith('ENDDRAW'):
                    parser_mode.pop()
                if parser_mode[-1] == 'draw':
                    if l.startswith('X'):
                        element.add_pin(l)
            except Exception as e:
                print
                print 'Exception occured at input file', filename, 'line:', lnum+1
                print e
                raise
#    for e in elements:
#        print elements[e].show()
    return elements

class Library(object):
    def __init__(self):
        self.elements = {}
        self.libnames = []

    def add_library(self, filename):
        self.libnames.append(os.path.basename(filename)[:-4])
        self.elements.update(parse_file(filename))

    def import_dir(self, directory):
        import glob, os.path
        files = glob.glob(os.path.join(directory, '*.lib'))
        print 'Importing dir', directory
        for fi in files:
            print '{}, '.format(fi),
            self.add_library(fi)
        print

    def lookup(self, name):
        return filter(lambda x: name in x, self.elements)

    def get_by_name(self, name):
        return self.elements[name]

if __name__=='__main__':
#    parse_file(sys.argv[1])
    import glob
    lib = Library()
#    lib.add_library(sys.argv[1])
    lib.import_dir(sys.argv[1])
    print len(lib.elements), 'symbols in library'
    print 'parsed', lines_count, 'lines'
#    print 'symbols containing STM32F030K in name', lib.lookup('STM32F030K')
#    print 'symbols containing GND in name', lib.lookup('GND')
#    print 'symbols containing D in name', sorted(lib.lookup('D'))
#    print lib.get_by_name('GND').show()
#    print lib.get_by_name('R').show()
#    print lib.get_by_name('LED').show()
#    print lib.get_by_name('STM32F030K6').show()
#    print lib.get_by_name('STM32F030K6').pin_by_name('VSS')
