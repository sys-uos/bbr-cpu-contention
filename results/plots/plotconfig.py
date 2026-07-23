import matplotlib as mpl
from math import sqrt

pgf_with_rc_fonts = {"pgf.texsystem": "lualatex"}
mpl.rcParams.update(pgf_with_rc_fonts)

def cm2inch(value):
    return value/2.54

def pt2inch(value):
    return 0.01384*value
    
def golden_mean():
    return (sqrt(5)-1.0)/2.0    

tight_layout = True

MARKERS=["X", "s", "P", "p", "v", "^", "d", "o", "<", ">"]
LINESTYLES=["-","--", "-.", ":", " ", "", None, None]
COLORS = [u'#006ba5', u'#f26c64',  u'#88d279', u'#7f7f7f', u'#8c564b', u'#17becf',  u'#e377c2', u'#ffcc99',  u'#ffff99', u'#984ea3',u'#bcbd22',]
ownrcParams = {}

ownrcParams['legend.framelinewidth'] = mpl.rcParams['axes.linewidth']
ownrcParams['legend.handlelinewidth'] = mpl.rcParams['axes.linewidth']
ownrcParams['boxplot.meanprops.markeredgewidth'] = mpl.rcParams['axes.linewidth'] / 2.0


orig_axes_ldg = mpl.axes.Axes.legend
def hpl_legend(self, *args, **kwargs):
    lobj = orig_axes_ldg(self, *args, **kwargs) 
    lobj.get_frame().set_linewidth(ownrcParams['legend.framelinewidth'])
    return lobj

mpl.axes.Axes.legend = hpl_legend


COLUMN_WIDTH=0
TEXT_WIDTH=0
FONT_SIZE=8
FS=0

def __setup_common(fs):
    global FS
    
    FS = fs
    
    mpl.rcParams['axes.axisbelow'] = True
    mpl.rcParams['axes.grid'] = False
    mpl.rcParams['axes.grid.axis'] = "both"
    mpl.rcParams['axes.grid.which'] = "major"
    
    mpl.rcParams['grid.linestyle'] = "dotted"
    
    mpl.rcParams['axes.labelpad'] = 1.0
    
    mpl.rcParams['axes.linewidth'] = 0.5
    mpl.rcParams['grid.linewidth'] = 0.5
    
    
    mpl.rcParams['xtick.major.width'] = mpl.rcParams['axes.linewidth']
    mpl.rcParams['xtick.minor.width'] = mpl.rcParams['axes.linewidth']
    mpl.rcParams['xtick.major.size'] = 2.5
    mpl.rcParams['xtick.minor.size'] = mpl.rcParams['xtick.major.size']*0.65
    mpl.rcParams['xtick.major.pad'] = 0.5
    
    mpl.rcParams['ytick.major.width'] = mpl.rcParams['axes.linewidth']
    mpl.rcParams['ytick.minor.width'] = mpl.rcParams['axes.linewidth']
    mpl.rcParams['ytick.major.size'] = 2.5
    mpl.rcParams['ytick.minor.size'] = mpl.rcParams['ytick.major.size']*0.65
    
    mpl.rcParams['ytick.major.pad'] = 0.5
    
    mpl.rcParams['axes.prop_cycle'] = mpl.cycler(u'color', COLORS)
    
    # Font sizes
    mpl.rcParams['font.size'] = fs
    mpl.rcParams['axes.labelsize'] = fs
    mpl.rcParams['axes.titlesize'] = fs
    mpl.rcParams['xtick.labelsize'] = fs-1
    mpl.rcParams['ytick.labelsize'] = fs-1
    
    mpl.rcParams['legend.fontsize'] = fs-1
    
    
    mpl.rcParams['legend.borderpad'] = 0.125
    mpl.rcParams['legend.labelspacing'] = 0.05
    mpl.rcParams['legend.handlelength'] = 1.5
    mpl.rcParams['legend.handleheight'] = mpl.rcParams['legend.handlelength']*golden_mean()
    mpl.rcParams['legend.handletextpad'] = mpl.rcParams['axes.linewidth'] / 2.0
    mpl.rcParams['legend.borderaxespad'] = 0.2
    mpl.rcParams['legend.columnspacing'] = mpl.rcParams['legend.handlelength']
    mpl.rcParams['legend.framealpha'] = 1.0
    mpl.rcParams['legend.edgecolor'] = 'black'
    
    
    ownrcParams['legend.framelinewidth'] = mpl.rcParams['axes.linewidth'] / 2.0
    
    mpl.rcParams['hatch.linewidth'] = mpl.rcParams['axes.linewidth']
    mpl.rcParams['hatch.color'] = "black"
    mpl.rcParams['errorbar.capsize'] = mpl.rcParams['axes.linewidth']
    mpl.rcParams['lines.linewidth'] = mpl.rcParams['axes.linewidth'] 
    mpl.rcParams['lines.markeredgewidth'] = mpl.rcParams['axes.linewidth'] / 2.0
    
    # Boxplot configuration
    mpl.rcParams['boxplot.patchartist'] = True
    mpl.rcParams['boxplot.flierprops.marker'] = '+'
    mpl.rcParams['boxplot.flierprops.markersize'] = mpl.rcParams['axes.linewidth'] / 2.0
    mpl.rcParams['boxplot.flierprops.linewidth'] = mpl.rcParams['axes.linewidth'] / 2.0
    
    mpl.rcParams['boxplot.boxprops.color'] = 'black'
    mpl.rcParams['boxplot.boxprops.linewidth'] = mpl.rcParams['axes.linewidth'] / 2.0
    
    mpl.rcParams['boxplot.whiskerprops.color'] = 'black'
    mpl.rcParams['boxplot.whiskerprops.linewidth'] = mpl.rcParams['axes.linewidth'] / 2.0
    mpl.rcParams['boxplot.whiskerprops.linestyle'] = '--' #(5, [1,1,1,1,1,1])
    
    mpl.rcParams['boxplot.capprops.color'] = 'black'
    mpl.rcParams['boxplot.capprops.linewidth'] = mpl.rcParams['axes.linewidth']
    mpl.rcParams['boxplot.capprops.linestyle'] = '-'
    
    mpl.rcParams['boxplot.medianprops.color'] = 'red'
    mpl.rcParams['boxplot.medianprops.linewidth']  = mpl.rcParams['axes.linewidth']
    
    mpl.rcParams['boxplot.meanprops.color'] = 'red'
    mpl.rcParams['boxplot.meanprops.marker'] = 's'
    mpl.rcParams['boxplot.meanprops.markerfacecolor'] = 'red'
    mpl.rcParams['boxplot.meanprops.markeredgecolor'] = 'black'
    ownrcParams['boxplot.meanprops.markeredgewidth'] = mpl.rcParams['axes.linewidth'] / 2.0
    mpl.rcParams['boxplot.meanprops.markersize'] = 1.5
    mpl.rcParams['boxplot.meanprops.linewidth'] = mpl.rcParams['axes.linewidth'] / 2.0


def configure_conext(use_tex=True, fs=9):
    global TEXT_WIDTH, COLUMN_WIDTH, FONT_SIZE, error_kw, kw_annotation_boxes
    TEXT_WIDTH=395.8225
    COLUMN_WIDTH=395.8225
    FONT_SIZE = 9

    __setup_common(fs)
    mpl.rc('text', usetex=use_tex)

    mpl.rcParams['lines.linewidth'] = 1.5

    mpl.rc('text.latex', preamble="\\usepackage[T1]{fontenc}\\usepackage{lmodern}\\usepackage[cm]{sfmath}")
    mpl.rc('font',**{'family':'sans-serif','sans-serif':['cm','Computer Modern Sans serif']})

    error_kw = dict(elinewidth=0.25,ecolor='black',capsize=0.5, capthick=0.25)
    kw_annotation_boxes = dict(boxstyle="Round,pad=.1", linewidth=mpl.rcParams['axes.linewidth'], fc='0.95')