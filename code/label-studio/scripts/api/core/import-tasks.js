import path from "path";
import {glob} from "glob";
import moment from "moment";
import {existsSync} from "fs";

import makeApiRequest from "./api-request.js";
import createProject from "./create-project.js";
import {readFile, readJsonFile, exitOnError} from "../util.js";

const createPrediction = () =>
({
    result: [],
    model_version: "initial_annotation"
});

const createTask = (taskData, initialAnnotation) =>
({
    data:
    {
        ...taskData,
        initialAnnotation: initialAnnotation
    },
    predictions:
    [
        createPrediction()
    ]
});

const getFormattedDate = timestamp => moment(new Date(timestamp)).format("DD-MM-YYYY");

function getTaskData(datasetName, projectName, cve, gitCommits)
{
    const stringMissing = "<missing>";

    return {
        datasetName: datasetName,
        projectName: projectName || stringMissing,
        cve:
        {
            id: cve.id || stringMissing,
            publicationDate: cve.Published ? getFormattedDate(cve.Published) : stringMissing,
            severityScore: cve.cvss ? cve.cvss.toString() : stringMissing,
            summary: cve.summary || stringMissing    
        },
        gitCommits: gitCommits
    };
}

const getInitialAnnotation = (diffsFiles, hyperlinks) =>
({
    diffsFiles: diffsFiles,
    hyperlinks: hyperlinks
});

const getLabeledHyperlinks = hyperlinks => Object.entries(hyperlinks).map(([url, data]) =>
{
    let content = data.content;

    return {
        url: url,
        labels: data.labels,
        dates:
        {
            min: content.min,
            max: content.max
        }
    };
});

class DatasetDescriptor
{
    static keys = ["cve", "hyperlinks", "projectName"];

    constructor(name, path, includedData = {})
    {
        this.name = name;
        this.path = path;

        this.constructor.keys.forEach(key => includedData[key] = Boolean(includedData[key]));

        this.includedData = includedData;
    }
}

const CVE_DATASET_DESCRIPTOR = new DatasetDescriptor("cve", "data", {cve: true, hyperlinks: true});
const CRAWL_DATASET_DESCRIPTOR = new DatasetDescriptor("crawl", "crawl-dataset-copy", {cve: true});
const BUGS_IN_PY_DATASET_DESCRIPTOR = new DatasetDescriptor("bugs-in-py", "bugsinpy-dataset", {projectName: true});

function getDatasetDescriptor(datasetEntryName)
{
    if(datasetEntryName.startsWith("CVE-"))
        return CVE_DATASET_DESCRIPTOR;

    if(datasetEntryName.startsWith("CRAWL-CVE-"))
        return CRAWL_DATASET_DESCRIPTOR;

    return BUGS_IN_PY_DATASET_DESCRIPTOR;
}

const mapCategorizedLine = (categorizedLine) =>
({
    category: categorizedLine.type,
    lineNumber: categorizedLine.id
});

const getCategorizedFile = (fileName, fileCategory, categorizedLinesBeforeChange, categorizedLinesAfterChange) =>
({
    fileName: fileName,
    category: fileCategory,
    lines:
    {
        beforeChange: categorizedLinesBeforeChange.map(mapCategorizedLine),
        afterChange: categorizedLinesAfterChange.map(mapCategorizedLine)
    }
});

function getCommit(datasetEntryPath, commitId)
{
    let patchesPath = path.join(datasetEntryPath, "patches");

    let commitPathPrefix = path.join(patchesPath, commitId + ".");

    let descFileSuffix = "desc";

    // message file can have either ".desc" or ".message" suffix, so if
    // there's no ".desc" file then read ".message"
    let hasDesc = existsSync(commitPathPrefix + descFileSuffix);

    let messagePath = commitPathPrefix + (hasDesc ? descFileSuffix : "message");

    let message = readFile(messagePath);

    let diff = readFile(commitPathPrefix + "diff");

    return {
        diff: diff,
        message: message
    };
}

function getTaskFromDatasetEntry(datasetDescriptor, datasetEntryPath)
{
    let commits = [];

    let diffsFiles = [];

    let annotationsPath = path.join(datasetEntryPath, "annotation");

    // loop over all commits
    glob.globSync(path.join(annotationsPath, "*.json")).forEach(annotationFilePath =>
    {
        let commitId = path.basename(annotationFilePath, ".json");

        let commit = getCommit(datasetEntryPath, commitId);

        commits.push(commit);

        let filesAnnotations = readJsonFile(annotationFilePath);

        let diffFiles = Object.entries(filesAnnotations).map(([fileName, annotation]) => getCategorizedFile(fileName, annotation.purpose, annotation["-"], annotation["+"]));

        diffsFiles.push(diffFiles);
    });

    let datasetName = datasetDescriptor.name;

    let projectName = datasetDescriptor.includedData.projectName ? path.basename(datasetEntryPath) : null;

    let cve = datasetDescriptor.includedData.cve ? readJsonFile(path.join(datasetEntryPath, "info.json")) : {};

    let hyperlinks = datasetDescriptor.includedData.hyperlinks ? getLabeledHyperlinks(readJsonFile(path.join(datasetEntryPath, "likely.json"))) : [];

    let initialAnnotation = getInitialAnnotation(diffsFiles, hyperlinks);

    let taskData = getTaskData(datasetName, projectName, cve, commits);

    let task = createTask(taskData, initialAnnotation);

    return task;
}

const getArrayRightHalf = array => array.slice(Math.floor(array.length / 2), array.length);

// map with substring to turn e.g. "pA", "pB" into just "A", "B",
// then add "_" + <package id (+ 1)> to get the entire project name
const getProjectName = projectDistribution => `${projectDistribution[0].substring(1)}_${projectDistribution[1] + 1}`;

const importTasks = (host, authenticationToken, projectId, tasks) => makeApiRequest("POST", host, authenticationToken, `projects/${projectId}/import`, tasks);

async function importTasksFromDatasets(host, authenticationToken, labelConfig, datasetsPath, datasetEntriesDistribution)
{
    datasetEntriesDistribution = Object.entries(datasetEntriesDistribution);

    // get all possible project names
    let projectNames = datasetEntriesDistribution.flatMap(([_, distribution]) => getArrayRightHalf(Object.entries(distribution)).map(getProjectName));

    // remove duplicates and sort the array
    //
    // names are sorted in the reverse order because
    // projects are displayed from the last to the first
    // (we need this order only when creating projects;
    // it doesn't matter elsewhere)
    projectNames = [...new Set(projectNames)].sort().reverse();

    let tasksForProjects = Object.fromEntries(projectNames.map(projectName => [projectName, []]));

    datasetEntriesDistribution.forEach(([datasetEntryName, distribution], i) =>
    {
        let datasetDescriptor = getDatasetDescriptor(datasetEntryName);

        let datasetEntryPath = path.join(datasetsPath, datasetDescriptor.path, datasetEntryName);

        distribution = Object.entries(distribution);

        // filter projects where its corresponding reviewer field equals 0
        let taskProjectNames = getArrayRightHalf(distribution).filter((_, i) => distribution[i][1] !== 0).map(getProjectName);

        let task = getTaskFromDatasetEntry(datasetDescriptor, datasetEntryPath);

        // add the tasks to the corresponding projects
        taskProjectNames.forEach(projectName => tasksForProjects[projectName].push(task));

        if(++i % 100 === 0)
            console.log(`Read ${i}/${datasetEntriesDistribution.length} tasks...`);
    });

    console.log("Importing tasks...");

    tasksForProjects = Object.entries(tasksForProjects);

    // create the projects and import the tasks
    for(let [projectName, tasks] of tasksForProjects)
    {
        // skip if there are no tasks for this project (improbable but possible)
        if(!tasks.length)
            continue;

        let response = await createProject(host, authenticationToken, projectName, labelConfig).catch(exitOnError);

        await importTasks(host, authenticationToken, response.id, tasks).catch(exitOnError);
    }
}

export {
    importTasks,
    importTasksFromDatasets
};