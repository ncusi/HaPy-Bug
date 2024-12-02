import minimist from "minimist-lite";

import {readFile, readJsonFile} from "./util.js";
import {importTasksFromDatasets} from "./core/import-tasks.js";

const argv = minimist(process.argv.slice(2));

const labelConfig = readFile(argv["label-config"]);
const datasetEntriesDistribution = readJsonFile(argv.distribution);

importTasksFromDatasets(argv.host, argv.token, labelConfig, argv.datasets, datasetEntriesDistribution);