import path from "path";
import moment from "moment";
import minimist from "minimist-lite";

import {exitOnError} from "./util.js";
import exportTasks from "./core/export-tasks.js";
import listProjects from "./core/list-projects.js";

function getPaddingSize(projects)
{
    let maxTitleLength = projects.map(project => project.title).reduce((a, b) => a.length > b.length ? a : b).length;

    // https://stackoverflow.com/questions/14879691/get-number-of-digits-with-javascript
    let digitsCount = Math.log(projects.length) * Math.LOG10E + 1 | 0;

    // we display current project id and total projects count so `digitsCount * 2`,
    // then +1 to account for slash between those numbers,
    // another +1 to account for a space between projects count and title
    // and finally add the length of the longest title
    return digitsCount * 2 + 2 + maxTitleLength;
}

const argv = minimist(process.argv.slice(2));

const host = argv.host;
const token = argv.token;
const outputDirPath = argv.output;

listProjects(host, token)
.then(projects =>
{
    if(!projects.length)
    {
        console.log("There are no labeling projects!");

        return;
    }

    const projectsCount = projects.length;

    const paddingSize = getPaddingSize(projects);

    const formattedTime = moment().format("YYYY-MM-DD_HHmmss");

    projects.forEach((project, i) =>
    {
        const projectId = project.id;
        const projectTitle = project.title;

        let fileName = `${projectTitle}_${projectId}`;

        let outputPath = path.join(outputDirPath, formattedTime, `${fileName}.json`);

        let head = `${i+1}/${projectsCount} ${projectTitle}`.padEnd(paddingSize);

        console.log(`-> ${head} | exporting to: ${outputPath}`);

        exportTasks(host, token, projectId, outputPath);
    });
})
.catch(exitOnError);