#!/usr/bin/env python
import sys, os

class Element(object):
    def __init__(self):
        self.name = ''
        self.pins = {}
        self.pins_i = {}
        self.reference = ''
        self.footprint = ''

    def parse_pin(self, line):
        l = line.split()
        name, num = l[1], l[2]
        ori = dict([('U', (0, -1)),
               ('D', (0,  1)),
               ('L', (-1, 0)),
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
        #print self.pins.values()
        for v in self.pins.values():
            print v
            _,_,x,y,_ = v[0]
            mx, nx = max(mx, x), min(nx, x)
            my, ny = max(my, y), min(ny, y)
        return mx-nx, my-ny

    def get_bounding_rect(self):
        mx = 0
        my = 0
        nx, ny = 0, 0
        for x,y in self.pins.values():
            mx, nx = max(mx, x), min(nx, x)
            my, ny = max(my, y), min(ny, y)
        return (mx,nx), (my,ny)



class Footprint(object):
    def __init__(self, name = None):
        self.name = name or ''
        self.pads = {}
        self.struct = None
        self.serial = 0
        self.position = None
        self.reference = ''
        self.rot = 'U'
        self.layer = 'F.Cu'

    def new_serial(self):
        self.serial += 1
        return self.serial

    def add_pad(self, struct):
        padname = ''
        if struct[1] == '':
            padname = '__{}'.format(self.new_serial())
        else:
            padname = struct[1][0]
        try:
            self.pads[padname] = struct
        except:
            print struct
            raise

    def assign_nets(self, ids, nets):
        for n in nets:
            self.pads[n].append([('net',), (ids[nets[n]]), (nets[n],)])

    def to_sexp(self):
        p = []
        def replace_layers(s, text):
            o = []
            for p in s:
                #print p
                try:
                    if p[0][0] == 'layer' and p[1][0] == 'F.Cu':
                        p[1] = (text,)
                        o.append(p)
                    elif p[0][0] == 'layers' and p[1][0] == 'F.Cu':
                        p[1] = (text,)
                        o.append(p)
                except:
                    pass
                if type(p) == int:
                    o.append(p)
                elif type(p) == list:
                    o.append(replace_layers(p, text))
                else:
                    o.append(p)
            return o

        def replace_refenence(s, text):
            o = []
            for p in s:
                #print p
                if type(p[0]) == list:
                    o.append(replace_refenence(p[0], text))
                elif p[0][0] == 'fp_text' and p[1][0] == 'reference':
                    p[2] = (text,)
                    o.append(p)
                else:
                    o.append(p)
            return o

        if self.position is not None:
            p = [('placed',), [('layer',), (self.layer,)],
                    [('at',),
                    (str(self.position[0]),),
                    (str(self.position[1]),),
                    (str({'U':0, 'R': 90, 'D': 180, 'L': 270}[self.rot]))]]
        import copy
#        for z in self.pads:
#            for i in self.pads[z]:
#                print i
#                if i[0][0] == 'layers':
#                    i[1] == (self.layer,) 
        s = copy.deepcopy(self.struct)
        s = s[:2] + p + s[2:]
        s = replace_refenence(s, self.reference)
        s = replace_layers(s, self.layer)
        return s

    def show(self):
        import sexp
        print sexp.save(self.struct)

class BrdLoader(object):
    def __init__(self):
        self.footprints = {}

    def lookup(self, name):
        return filter(lambda x: name in x, self.footprints)

    def new_by_name(self, name):
        import copy
        return copy.deepcopy(self.footprints[name])

    def import_dir(self, directory):
        import glob, os.path
        files = glob.glob(os.path.join(directory, '*/*.kicad_mod'))
        files += glob.glob(os.path.join(directory, '*.kicad_mod'))
        # parse it!
        #print files
        print 'Importing footprint modules from {}'.format(directory),
        map(self.parse_file, files)
        print ' {} items from {} files'.format(len(self.footprints.keys()), len(files))

    def parse_file(self, filename):
        #print filename,
        sys.stdout.write('.')
        sys.stdout.flush()
        with open(filename) as fin:
            footprint = None
            import sexp
            exp = sexp.parse(fin.read())
            for e in exp:
                #print e
                if e[0][0] == 'module':
                    name = e[1][0]
                    #print name,
                    footprint = Footprint(name=name)
                    footprint.struct = e
                    self.footprints[name] = footprint

                    for i in e[2:]:
                        if i[0][0] == 'pad':
                            try:
                                footprint.add_pad(i)
                            except:
                                print e
                                raise
            return exp

    def show(self):
        for f in self.footprints:
            self.footprints[f].show()

def unqoute(s):
    s.strip()
    if s[0] == '"':
        s = s[1:]
    if s[-1] == '"':
        s = s[-1]
    return s

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
                    aliases = []
                if parser_mode[-1] == 'def' and l.startswith('F2'):
                    element.footprint = unqoute(l.strip().split()[1])
                if parser_mode[-1] == 'def' and l.startswith('ALIAS'):
                    aliases += l.strip().split()[1:]
                if parser_mode[-1] == 'def' and l.startswith('ENDDEF'):
                    parser_mode.pop()
                    elements[element.name] = element
                    for a in aliases:
                        elements[a] = element
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
        print 'Importing dir with schematic libraries', directory
        for fi in files:
            print '{}, '.format(fi),
            self.add_library(fi)
        print len(self.elements.keys()), 'items from', len(files), 'files'

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
