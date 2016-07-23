#/usr/bin/env python

from libparser import BrdLoader
import sexp

import time
__tstamps = int(time.time())
class Board(object):
    def __init__(self, library, schema=None):
        self.schema = schema
        self.packages = {}
        if not (type(library) == BrdLoader):
            raise Exception()
        self.library = library #BrdLoader instance
        self.nets = {} #nets by id
        self.nets_n = {} #nets by name
        self.last_net = 1
        self.layer_count = 2

    def add_net(self, net_name):
        if not self.nets_n.has_key(net_name):
            self.nets[self.last_net] = net_name
            self.nets_n[net_name] = self.last_net # str(self.last_net)
            self.last_net += 1


    def place_package(self, instance_name, package, nets=None):
        p = self.library.new_by_name(package) 
        p.reference = instance_name
        if nets is None:
            #n = self.schema.nets[instance_name] #get_by_inst(instance_name).nets
            n = []
            nets = {}
            for nn in self.schema.nets:
                for (what, pin) in self.schema.nets[nn]:
                    if what == instance_name:
                        nets[pin] = nn
                    #map(lambda (a,b): b[0], x)

                    #filter(lambda 
                    #if l

            
        map(self.add_net, nets.values())
        p.assign_nets(self.nets_n, nets)
        self.packages[instance_name] = p

    def to_sexp(self):
        o = []
        o.append( [('net',), (0,), ('""',)])
        for n in self.nets:
            o.append( [('net',), (n,), (self.nets[n],)])

        oo = []
        oo.append( [('clearance',), ('0.1',)] )
        oo.append( [('trace_width',), ('0.25',)] )
        oo.append( [('via_dia',), ('0.6',)] )
        oo.append( [('via_drill',), ('0.4',)] )
        oo.append( [('uvia_dia',), ('0.3',)] )
        oo.append( [('uvia_drill',), ('0.1',)] )
        for n in sorted(map(int,self.nets)):
            oo.append( [('add_net',), (self.nets[n],)])
        o.append( [('net_class',), ('Default',) ,('\"this is default net class\"',)] + oo )
        
        for p in self.packages:
            o.append( self.packages[p].to_sexp() )

        o = [('kicad_pcb',), [('version',), ('4',)], [('host',), ('libboard',), ('0.0.1',)]] +\
        [[('general',),
            [('links',), ('7',)],
            [('area',), ('7',)],
            [('thickness',), ('1.6',)],
            [('drawings',), ('4',)],
            [('tracks',), ('0',)],
            [('zones',), ('0',)],
            [('modules',), ('{}'.format(len(self.nets.values())),)],
            [('nets',), ('7',)],
            [('no_connects',), ('6',)]]] + sexp.parse("""(layers
    (0 F.Cu signal)""" + \
    '\n'.join(['({} In{}.Cu signal)'.format(i, i) for i in range(self.layer_count-2)]) + \
#    (1 In1.Cu signal)
#    (2 In2.Cu signal)
#    (3 In3.Cu signal)
#    (4 In4.Cu signal)
#    (5 In5.Cu signal)
#    (6 In6.Cu signal)
#    (7 In7.Cu signal)
#    (8 In8.Cu signal)
#    (9 In9.Cu signal)
#    (10 In10.Cu signal)
#    (11 In11.Cu signal)
#    (12 In12.Cu signal)
#    (13 In13.Cu signal)
#    (14 In14.Cu signal)
#    (15 In15.Cu signal)
#    (16 In16.Cu signal)
#    (17 In17.Cu signal)
#    (18 In18.Cu signal)
#    (19 In19.Cu signal)
#    (20 In20.Cu signal)
#    (21 In21.Cu signal)
#    (22 In22.Cu signal)
#    (23 In23.Cu signal)
#    (24 In24.Cu signal)
#    (25 In25.Cu signal)
#    (26 In26.Cu signal)
#    (27 In27.Cu signal)
#    (28 In28.Cu signal)
#    (29 In29.Cu signal)
#    (30 In30.Cu signal)
"""    (31 B.Cu signal)
    (32 B.Adhes user)
    (33 F.Adhes user)
    (34 B.Paste user)
    (35 F.Paste user)
    (36 B.SilkS user)
    (37 F.SilkS user)
    (38 B.Mask user)
    (39 F.Mask user)
    (40 Dwgs.User user)
    (41 Cmts.User user)
    (42 Eco1.User user)
    (43 Eco2.User user)
    (44 Edge.Cuts user)
    (45 Margin user)
    (46 B.CrtYd user)
    (47 F.CrtYd user)
    (48 B.Fab user)
    (49 F.Fab user)
)""") +  sexp.parse("""(page A4)
(setup
    (last_trace_width 0.25)
    (trace_clearance 0.2)
    (zone_clearance 0.508)
    (zone_45_only no)
    (trace_min 0.2)
    (segment_width 0.2)
    (edge_width 0.1)
    (via_size 0.6)
    (via_drill 0.4)
    (via_min_size 0.4)
    (via_min_drill 0.3)
    (uvia_size 0.3)
    (uvia_drill 0.1)
    (uvias_allowed no)
    (uvia_min_size 0.2)
    (uvia_min_drill 0.1)
    (pcb_text_width 0.3)
    (pcb_text_size 1.5 1.5)
    (mod_edge_width 0.15)
    (mod_text_size 1 1)
    (mod_text_width 0.15)
    (pad_size 1.5 1.5)
    (pad_drill 0.6)
    (pad_to_mask_clearance 0)
    (aux_axis_origin 0 0)
    (visible_elements FFFFFF7F)
    (pcbplotparams
      (layerselection 0x00030_80000001)
      (usegerberextensions false)
      (excludeedgelayer true)
      (linewidth 0.100000)
      (plotframeref false)
      (viasonmask false)
      (mode 1)
      (useauxorigin false)
      (hpglpennumber 1)
      (hpglpenspeed 20)
      (hpglpendiameter 15)
      (hpglpenoverlay 2)
      (psnegative false)
      (psa4output false)
      (plotreference true)
      (plotvalue true)
      (plotinvisibletext false)
      (padsonsilk false)
      (subtractmaskfromsilk false)
      (outputformat 1)
      (mirror false)
      (drillshape 1)
      (scaleselection 1)
      (outputdirectory "."))
  )""") + o

        return o

    def show(self):
        for p in self.packages:
            self.packages[p].show()

if __name__=="__main__":
    lib = BrdLoader()
    lib.import_dir('/home/mzatko/kicad_sources/library-repos/')
    b = Board(lib)
#    print lib.lookup('QFN-16')
    idx = 0
    from libschema import Schematic
    sch = Schematic()
    b.schema = sch
#    u=sch.add_component('STM32F050C4')
#    print 'U is',u
#    sch.connect_to_GND(u, '12')
#    sch.connect_to_GND(u, '11')
#    sch.connect_to_GND(u, '10')
#    sch.connect_to_GND(u, '13')
#    print 'PKG is "{}"'.format( sch.get_by_inst(u).element.footprint )
#    b.place_package(u, lib.lookup('QFN-16')[0])
#    idx += 1
    print
    print 'generating'
    for x in range(15):
        for y in range(15):
            idx += 1
            u = 'U{}'.format(idx)
            b.place_package(u, lib.lookup('QFN-48')[0], {'1': 'VCC', '2': 'GND'})
            b.packages[u].position = (30 + x * 10.0, 30 + y * 10.0)
#    b.place_package('U2', lib.lookup('QFN-16')[0], {'1': 'VCC', '17': 'GND'})
#    b.place_package('U3', lib.lookup('QFN-16')[0], {'1': 'VCC', '17': 'GND'})
#    b.place_package('U4', lib.lookup('QFN-16')[0], {'1': 'VCC', '17': 'GND'})
#    b.place_package('U5', lib.lookup('QFN-16')[0], {'1': 'VCC', '17': 'GND'})
#    b.place_package('U6', lib.lookup('QFN-16')[0], {'1': 'VCC', '17': 'GND'})
#    b.place_package('U7', lib.lookup('QFN-16')[0], {'1': 'VCC', '17': 'GND'})
#    b.place_package('U8', lib.lookup('QFN-16')[0], {'1': 'VCC', '17': 'GND'})
#    b.place_package('U9', lib.lookup('QFN-16')[0], {'1': 'VCC', '17': 'GND'})
#    b.place_package('U10', lib.lookup('QFN-16')[0], {'1': 'VCC', '17': 'GND'})
#    b.place_package('U11', lib.lookup('QFN-16')[0], {'1': 'VCC', '17': 'GND'})
#    b.place_package('U12', lib.lookup('QFN-16')[0], {'1': 'VCC', '17': 'GND'})
#    b.place_package('U13', lib.lookup('QFN-16')[0], {'1': 'VCC', '17': 'GND'})
#    b.place_package('U14', lib.lookup('QFN-16')[0], {'1': 'VCC', '17': 'GND'})
    #b.show()
    import sexp
    with open('lol.sexp', 'w+') as fout: fout.write(sexp.save(b.to_sexp()))
