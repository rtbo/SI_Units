import qbs
import qbs.FileInfo
import qbs.TextFile

import 'phcgfuncs.js' as PhCgFuncs

Module {

    Depends { name:"cpp" }

    property path script
    property path data

    additionalProductFileTags: ["generated_glob", "generated_item"]

    FileTagger {
        // Physics global templates
        patterns: ["*.ph_gt"]
        fileTags: ["ph_glob_template"]
    }

    FileTagger {
        // Physics global templates
        patterns: ["*.ph_it"]
        fileTags: ["ph_item_template"]
    }

    Rule {
        inputs: ["ph_glob_template"]

        Artifact {
            fileTags: ["generated_glob", "hpp", "cpp"]
            filePath: {
                var rp = PhCgFuncs.getSrcRelativePath(product, FileInfo.path(input.filePath));
                return FileInfo.joinPaths(rp, input.completeBaseName);
            }
        }

        prepare: {
            var script = product.moduleProperty("phcg", "script");
            var data = product.moduleProperty("phcg", "data");
            var cmd = new Command("python", [
                script, "--mode", "glob", "--datafile", data,
                "--input", input.filePath, "--output", output.filePath
            ]);
            cmd.highlight = "codegen";
            cmd.description = "generating " + output.fileName;
            return cmd;
        }
    }

    Rule {
        inputs: ["ph_item_template"]

        outputFileTags: ["generated_item", "hpp", "cpp"]

        outputArtifacts: {
            var dp = product.moduleProperty("phcg", "data");
            var items = PhCgFuncs.getItems(dp);
            var oa = [];
            for (var i=0; i<items.length; ++i) {
                var item = items[i];
                var of = PhCgFuncs.outputItemPath(product, input, item);
                oa.push({
                    filePath: of
                });
            }
            return oa;
        }

        prepare: {
            var script = product.moduleProperty("phcg", "script");
            var dataPath = product.moduleProperty("phcg", "data");
            var items = PhCgFuncs.getItems(dataPath);
            var cmds = [];
            for (var i=0; i<items.length; ++i) {
                var item = items[i];
                var of = PhCgFuncs.outputItemPath(product, input, item);
                var cmd = new Command("python", [ script, "--help"]);
                var cmd = new Command("python", [
                    script, "--mode", "item", "--datafile", dataPath, "--item", item.name,
                    "--input", input.filePath,
                    "--output", FileInfo.joinPaths(product.buildDirectory, of)
                ]);
                cmd.highlight = "codegen";
                cmd.description = "generating "+FileInfo.fileName(of);
                cmds.push(cmd);
            }
            return cmds;
        }
    }
}
