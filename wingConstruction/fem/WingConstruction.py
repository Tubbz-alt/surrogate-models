__author__ = "Juri Bieler"
__version__ = "0.0.1"
__status__ = "Development"

# ==============================================================================
# description     :interface to Calculix and solver-input-file generation
# author          :Juri Bieler
# date            :2018-07-13
# notes           :
# python_version  :3.6
# ==============================================================================


class WingConstruction:

    def __init__(self, project_path, half_span, box_depth, box_height, n_ribs, box_overhang=0.):
        self.projectPath = project_path
        self.halfSpan = half_span
        self.boxDepth = box_depth
        self.boxHeight = box_height
        self.nRibs = n_ribs
        self.boxOverhang = box_overhang
        self.elementSize = 0.1
        print('done')

    def calc_span_division(self, length):
        div = int(length / self.elementSize)
        if self.nRibs <= 1:
            return self.calc_division(length)
        while div % (self.nRibs-1) > 0 or div % 2 > 0:
            div += 1
        return div

    # the division shouldn't be odd or 0
    def calc_division(self, length):
        div = int(length / self.elementSize)
        if div == 0:
            div = 2
        if div % 2 > 0:
            div += 1
        return div

    def generate_wing(self, force_top, force_but, element_size, element_type='qu4'):
        #elemType = 'qu8'
        #elemType = 'qu4'
        #force in N at wingtip
        #force = -0.5*(77000. * 9.81)
        # outer geometry in m
        #overhang = 0.5
        #height = 1.
        #halfSpan = 17.
        #boxDepth = 2.
        #elementSize = 0.25
        self.elementSize = element_size
        outLines = []
        outLines.append('# draw flat T as lines')
        outLines.append('# top right corner')
        outLines.append('pnt pc 0 0 0')
        outLines.append('seta pc all')
        outLines.append('swep pc new tra 0 0 {:f} {:d}'.format(self.boxHeight, self.calc_division(self.boxHeight)))
        outLines.append('swep pc new tra 0 {:f} 0 {:d}'.format(self.boxDepth, self.calc_division((self.boxDepth))))
        outLines.append('swep pc new tra 0 {:f} 0 {:d}'.format(-1*self.boxOverhang, self.calc_division(self.boxOverhang)))
        outLines.append('')
        outLines.append('# top left corner')
        outLines.append('pnt pc2 0 {:f} 0'.format(self.boxDepth))
        outLines.append('seta pc2 pc2')
        outLines.append('swep pc2 new tra 0 0 {:f} {:d}'.format(self.boxHeight, self.calc_division(self.boxHeight)))
        outLines.append('swep pc2 new tra 0 {:f} 0 {:d}'.format(self.boxOverhang, self.calc_division(self.boxOverhang)))
        outLines.append('')
        outLines.append('# lower right corner')
        outLines.append('pnt pc3 0 0 {:f}'.format(self.boxHeight))
        outLines.append('seta pc3 pc3')
        outLines.append('swep pc3 new tra 0 {:f} 0 {:d}'.format(-1*self.boxOverhang, self.calc_division(self.boxOverhang)))
        outLines.append('swep pc3 new tra 0 {:f} 0 {:d}'.format(self.boxDepth, self.calc_division((self.boxDepth))))
        outLines.append('')
        outLines.append('# lower left corner')
        outLines.append('pnt pc4 0 {:f} {:f}'.format(self.boxDepth, self.boxHeight))
        outLines.append('seta pc4 pc4')
        outLines.append('swep pc4 new tra 0 {:f} 0 {:d}'.format(self.boxOverhang, self.calc_division(self.boxOverhang)))
        outLines.append('')
        outLines.append('seta II2d all')
        outLines.append('')

        outLines.append('# extrude the II')
        spanDiv = self.calc_span_division(self.halfSpan)
        outLines.append('swep II2d II2dOppo tra {:f} 0 0 {:d}'.format(self.halfSpan, spanDiv))
        outLines.append('# make surfaces face outside')
        outLines.append('seta toflip s A002 A005 A006')
        outLines.append('flip toflip')
        outLines.append('# new set for II beam')
        outLines.append('seta II all')
        outLines.append('')
        outLines.append('# define top and buttom shell for load')
        outLines.append('seta loadTop s A002')
        outLines.append('comp loadTop d')
        outLines.append('seta loadBut s A007')
        outLines.append('comp loadBut d')

        for i in range(0, self.nRibs):
            if self.nRibs <= 1:
                spanPos = 0
            else:
                spanPos = i * (self.halfSpan / (self.nRibs-1))
            prName = 'rp{:d}'.format(i)
            ribName = 'rib{:d}'.format(i)
            outLines.append('')
            outLines.append('# generate a rib{:d}'.format(i))
            outLines.append('seta prevAll all')
            outLines.append('pnt '+prName+' {:f} 0 0'.format(spanPos))
            outLines.append('seta '+prName+' p '+prName+'')
            outLines.append('swep '+prName+' new tra 0 0 {:f} {:d}'.format(self.boxHeight, self.calc_division((self.boxHeight))))
            outLines.append('seta '+ribName+' l all')
            outLines.append('setr '+ribName+' l prevAll')
            outLines.append('swep '+ribName+' '+ribName+' tra 0 {:f} 0 {:d} a'.format(self.boxDepth, self.calc_division(self.boxDepth)))
            outLines.append('comp '+ribName+' u')

        outLines.append('')
        outLines.append('# mesh it')
        outLines.append('elty all '+element_type)
        outLines.append('mesh all')
        outLines.append('')

        outLines.append('# merge all nodes to get one big body')
        outLines.append('seta nodes n all')
        outLines.append('merg n nodes')
        outLines.append('')

        outLines.append('# write msh file')
        outLines.append('seta nodes n all')
        outLines.append('enq nodes bc rec 0 _ _')
        outLines.append('send bc abq nam')
        outLines.append('send all abq')
        outLines.append('')

        nodeCount = (self.calc_span_division(self.halfSpan)+1) * (self.calc_division(self.boxDepth)+1)
        if element_type == 'qu8':
            nodeCount -= 0.5*self.calc_span_division(self.halfSpan) * 0.5*self.calc_division(self.boxDepth)
        noadLoadTop = force_top/nodeCount
        noadLoadBut = force_but / nodeCount
        outLines.append('# load application')
        outLines.append('# top')

        outLines.append('seta nodes n all')
        outLines.append('enq nodes bc1 rec {:f} 0 0 0.01'.format(self.halfSpan))
        outLines.append('enq nodes bc2 rec {:f} {:f} 0 0.01'.format(self.halfSpan, self.boxDepth))
        outLines.append('seta load bc1 bc2')
        outLines.append('send load abq force 0 0 {:f}'.format((force_top+force_but)/2.))

        outLines.append('#send loadTop abq force 0 0 {:f}'.format(noadLoadTop))
        outLines.append('# buttom')
        outLines.append('#send loadBut abq force 0 0 {:f}'.format(noadLoadBut))
        outLines.append('')
        outLines.append('# plot it')
        outLines.append('rot -y')
        outLines.append('rot r 110')
        outLines.append('rot u 20')
        outLines.append('seta ! all')
        outLines.append('frame')
        outLines.append('zoom 2')
        outLines.append('view elem')
        outLines.append('plus n loadTop g')
        outLines.append('plus n loadBut y')
        outLines.append('plus n bc r')
        outLines.append('plus n II2dOppo b')
        outLines.append('hcpy png')
        outLines.append('sys mv hcpy_1.png mesh.png')
        outLines.append('')
        outLines.append('quit')
        f = open(self.projectPath + '/wingGeo.fbl', 'w')
        f.writelines(line + '\n' for line in outLines)
        f.close()

    def generate_inp(self, shell_thickness):
        material_young = 69000000000.
        material_poisson = 0.32
        outLines = []
        outLines.append('** load mesh- and bc-file')
        outLines.append('*include, input=all.msh')
        outLines.append('*include, input=bc.nam')
        outLines.append('')
        outLines.append('** constraints')
        outLines.append('*boundary')
        outLines.append('Nbc,1,3')
        outLines.append('')
        outLines.append('** material definition')
        outLines.append('*MATERIAL,NAME=alu')
        outLines.append('*ELASTIC')
        outLines.append('{:f}, {:f}'.format(material_young, material_poisson))
        outLines.append('')
        outLines.append('** define surfaces')
        outLines.append('*shell section, elset=Eall, material=alu')
        outLines.append('{:f}'.format(shell_thickness))
        outLines.append('')
        outLines.append('** step')
        outLines.append('*step')
        outLines.append('*static')
        outLines.append('')
        outLines.append('** load')
        outLines.append('*cload')
        outLines.append('*include, input=load.frc')
        #outLines.append('*include, input=loadTop.frc')
        #outLines.append('*include, input=loadBut.frc')
        outLines.append('')
        outLines.append('*node file')
        outLines.append('U')
        outLines.append('*el file')
        outLines.append('S')
        outLines.append('*end step')
        outLines.append('')
        f = open(self.projectPath + '/wingRun.inp', 'w')
        f.writelines(line + '\n' for line in outLines)
        f.close()


if __name__ == '__main__':
    geo = WingConstruction()
    geo.generate_wing('../dataOut/test01/test', 5, 0.1, 0.1, 0.1)
    geo.generate_inp('../dataOut/test01/test', 2.)