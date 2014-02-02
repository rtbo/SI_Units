#! /usr/bin/env python

# Copyright (C) 2013-2014 Remi Thebault
# All rights reserved.
#
# This program and its source code are distributed under the
# terms of the BSD-style license, that can be found in the
# License.txt file at project root.


import sys
import os.path, time
import json
from jinja2 import Environment, FileSystemLoader



def fileMustBeWritten(templateFile, outFile):
    if not os.path.exists(outFile): return True
    if os.path.getmtime(__file__) > os.path.getmtime(outFile):
        return True
    if not os.path.exists(templateFile):
        raise ValueError(templateFile+" do not exist")
    return os.path.getmtime(templateFile) > os.path.getmtime(outFile)




def titleStr(s):
    # return a copy of the string s with first character uppercased,
    # and all other characters untouched
    if len(s) == 0:
        return s;
    ts = s[0].upper()
    if len(s) > 1:
        ts = ts + s[1:]
    return ts




if __name__ == '__main__':

    with open("PhysicsData.json", "r") as data_file:
        PhysicsItems = json.load(data_file)


    env = Environment(trim_blocks=True, loader=FileSystemLoader('templates'))


    globTemplates = [
        {
            "input": "FwdDecl.hpp.template",
            "output": "include/physics/FwdDecl.hpp",
        },
        {
            "input": "_IncludeAll.hpp.template",
            "output": "include/physics/_IncludeAll.hpp",
        },
        {
            "input": "Literals.hpp.template",
            "output": "include/physics/Literals.hpp",
        },
        {
            "input": "QPhysics/QPhysics.hpp.template",
            "output": "QPhysics/include/QPhysics.hpp",
        },
        {
            "input": "QPhysics/QPhysics.cpp.template",
            "output": "QPhysics/QPhysics.cpp",
        },
        {
            "input": "QPhysicsUI/src.pri.template",
            "output": "QPhysicsUI/src.pri",
        },
        {
            "input": "QPhysicsDesigner/QPhysicsDesignerPlugin.hpp.template",
            "output": "QPhysicsDesigner/QPhysicsDesignerPlugin.hpp",
        },
        {
            "input": "QPhysicsDesigner/QPhysicsDesignerPlugin.cpp.template",
            "output": "QPhysicsDesigner/QPhysicsDesignerPlugin.cpp",
        }
    ]

    itemTemplates = [
        {
            "input": "Item.hpp.template",
            "output": "include/physics/{}.hpp",
        },
        {
            "input": "QPhysicsUI/QItemSpinBox.hpp.template",
            "output": "QPhysicsUI/include/Q{}SpinBox.hpp",
        },
        {
            "input": "QPhysicsUI/QItemSpinBox.cpp.template",
            "output": "QPhysicsUI/Q{}SpinBox.cpp",
        }
    ]


    # completing items
    for pi in PhysicsItems:
        pi["titleName"] = titleStr(pi["name"])
        pi["titleDefaultUnit"] = titleStr(pi["defaultUnit"])
        for u in pi["units"]:
            u["titleName"] = titleStr(u["name"])
            if not "litName" in u:
                u["litName"] = u["name"]
            if not "wcharSeq" in u:
                u["wcharSeq"] = u["name"]


    inputFiles = []
    for gt in globTemplates:
        inputFiles.append(gt["output"])

    for it in itemTemplates:
        for pi in PhysicsItems:
            inputFiles.append(it["output"].format(pi['titleName']))


    if len(sys.argv) > 1 and sys.argv[1] == 'clear':
        # clear mode

        for inF in inputFiles:
            if os.path.exists(inF):
                print ("removing " + inF)
                os.remove(inF)


    elif len(sys.argv) > 1 and sys.argv[1] == 'ignorefile':

        ignoreFName = ".gitignore"
        if len(sys.argv) > 2: ignoreFName = sys.argv[2]

        if os.path.exists(ignoreFName):
            with open(ignoreFName) as ignoreF:
                content = ignoreF.readlines()
        else:
            content = []


        marker = "## Lines generated by PhysicsGenerator.py ##"

        # removing line between the 2 markers
        with open(ignoreFName, "w") as ignoreF:
            skipping = False
            for line in content:
                if marker in line:
                    skipping = not skipping
                else:
                    if not skipping: ignoreF.write(line)

        # updating file with the updated data
        with open(ignoreFName, "a") as ignoreF:
            ignoreF.write(marker+"\n")
            for inF in inputFiles:
                ignoreF.write(inF+"\n")
            ignoreF.write(marker+"\n")


    else:

        # starting generation
        for gt in globTemplates:
            if fileMustBeWritten(os.path.join("templates", gt["input"]), gt["output"]):
                tplt = env.get_template(gt["input"])
                content = tplt.render(items=PhysicsItems)
                print("writing " + gt["output"])
                os.makedirs(os.path.dirname(gt["output"]), exist_ok=True)
                with open(gt["output"], "w") as outF:
                    outF.write(content)

        for it in itemTemplates:
            tplt = None
            for pi in PhysicsItems:
                outFName = it["output"].format(pi['titleName'])
                if fileMustBeWritten(os.path.join("templates", it["input"]), outFName):
                    if tplt is None: tplt = env.get_template(it["input"])
                    content = tplt.render(item=pi)
                    print("writing " + outFName)
                    os.makedirs(os.path.dirname(outFName), exist_ok=True)
                    with open(outFName, "w") as outF:
                        outF.write(content)

    sys.exit(0)

