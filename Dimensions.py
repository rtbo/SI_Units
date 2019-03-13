
import sys
import os
import argparse
import json
from jinja2 import Environment

unit_defs = {}

class Dim:
    @staticmethod
    def build_from_dict(dim_dict):
        dim = Dim()
        dim.M = dim_dict["M"]
        dim.L = dim_dict["L"]
        dim.T = dim_dict["T"]
        dim.I = dim_dict["I"]
        dim.Th = dim_dict["Th"]
        dim.N = dim_dict["N"]
        dim.J = dim_dict["J"]
        return dim

    @staticmethod
    def subtract(lhs, rhs):
        dim = Dim()
        dim.M = lhs.M - rhs.M
        dim.L = lhs.L - rhs.L
        dim.T = lhs.T - rhs.T
        dim.I = lhs.I - rhs.I
        dim.Th = lhs.Th - rhs.Th
        dim.N = lhs.N - rhs.N
        dim.J = lhs.J - rhs.J
        return dim

# a single unit definition such as meter or volt
class UnitDef:
    @staticmethod
    def build_from_dict(dim, dict):
        ud = UnitDef()
        ud.dim = dim
        ud.name = dict["name"]
        ud.symbol = dict["symbol"]
        ud.unicode = dict["unicode"]
        unit_defs[ud.name] = ud

# a general unit definition such as meter, volt,
# or joule per mole.kelvin
class Unit:

    class Comp:
        def __init__(self, order, unit_def):
            self.order = order
            self.unit_def = unit_def

    def __init__(self):
        self.pos_comps = []
        self.neg_comps = []
        self.name = ""
        self.symbol = ""
        self.unicode = ""

    def check_add_comp(self, order, name):
        if order > 0:
            self.pos_comps.append(self.Comp(order, unit_defs[name]))
        elif order < 0:
            self.neg_comps.append(self.Comp(order, unit_defs[name]))

    def add_dim_comps(self, dim):
        self.check_add_comp(dim.M, "kilogram")
        self.check_add_comp(dim.L, "meter")
        self.check_add_comp(dim.T, "second")
        self.check_add_comp(dim.I, "ampere")
        self.check_add_comp(dim.Th, "kelvin")
        self.check_add_comp(dim.N, "mole")
        self.check_add_comp(dim.J, "candela")

    def compose(self):

        def add_order(order):
            if order < 0:
                self.unicode += "\\u207B" # exp minus
            if abs(order) == 3:
                self.name += "3"
                self.symbol += "3"
                self.unicode += "\\u00B3" # exp 3
            elif abs(order) == 2:
                self.name += "2"
                self.symbol += "2"
                self.unicode += "\\u00B2" # exp 2
            elif order == -1:
                self.unicode += "\\u207B\\u00B9" # exp minus 1

        def add_comp(comp):
            if len(self.name):
                self.name += "_"
                self.unicode += "."
            self.name += comp.unit_def.name
            self.symbol += comp.unit_def.symbol
            self.unicode += comp.unit_def.unicode
            add_order(comp.order)

        for c in self.pos_comps:
            add_comp(c)
        if len(self.neg_comps):
            if len(self.pos_comps):
                self.name += "_"
            self.name += "per"
        for c in self.neg_comps:
            add_comp(c)


    @staticmethod
    def build_from_single_def(unit_def):
        unit = Unit()
        unit.name = unit_def.name
        unit.symbol = unit_def.symbol
        unit.unicode = unit_def.unicode
        unit.pos_comps.append(Unit.Comp(1, unit_def))
        return unit

    @staticmethod
    def build_from_dim(dim):
        unit = Unit()
        unit.add_dim_comps(dim)
        unit.compose()
        return unit

    @staticmethod
    def build_from_dim_and_foreign(dim, foreign):
        unit = Unit()
        unit.check_add_comp(1, foreign)
        foreign_def = unit_defs[foreign]
        dim = Dim.subtract(foreign_def.dim, dim)
        unit.add_dim_comps(dim)
        unit.compose()
        return unit


def check_unit_def(dim_dict):
    if "unit_def" in dim_dict:
        def_dict = dim_dict["unit_def"]
        dim = Dim.build_from_dict(dim_dict)
        UnitDef.build_from_dict(dim, def_dict)


def complete_dim(dim_dict):
    dim_dict["units"] = []
    if "unit_def" in dim_dict:
        dim_dict["units"].append(Unit.build_from_single_def(
            unit_defs[dim_dict["unit_def"]["name"]]
        ))
    elif "foreign_unit" in dim_dict:
        dim_dict["units"].append(Unit.build_from_dim_and_foreign(
            Dim.build_from_dict(dim_dict), dim_dict["foreign_unit"]
        ))
    else:
        dim_dict["units"].append(Unit.build_from_dim(Dim.build_from_dict(dim_dict)))
    pass


if __name__ == '__main__':

    ap = argparse.ArgumentParser(description="Physics dimensions code generator")
    ap.add_argument("--input", nargs='?', type=argparse.FileType('r'),
            default=sys.stdin, help="Input template to be used")
    ap.add_argument("--output", nargs='?', type=argparse.FileType('w'),
            default=sys.stdout, help="Output file")
    ap.add_argument("--print-dims", dest="print_dims", action="store_true", default=False,
            help="print the list of dimensions (one per line) and exit")
    ap.add_argument("--dim", help="The dimension to generate code for. Toggles to single dimension mode.")
    # todo - exclusion/inclusion
    args = ap.parse_args()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    datafile = os.path.join(dir_path, "Dimensions.json")

    with open(datafile, "r") as df:
        dims = json.load(df)

    for dim in dims:
        check_unit_def(dim)

    if args.print_dims:
        for dim in dims:
            args.output.write(dim["name"] + ";")
        sys.exit(0)


    tplt = Environment(trim_blocks=True).from_string(args.input.read())

    if len(args.dim):
        dim = [dim for dim in dims if dim["name"] == args.dim][0]
        complete_dim(dim)
        args.output.write(tplt.render(dim=dim))
    else:
        for dim in dims:
            complete_dim(dim)
        args.output.write(tplt.render(dims=dims))
