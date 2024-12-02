import fs from "fs";
import {dirname} from "path";

import makeApiRequest from "./api-request.js";

function exportTasks(host, authorizationToken, projectId, outputFilePath)
{
    return makeApiRequest("GET", host, authorizationToken, `projects/${projectId}/export`,
    {
        exportType: "JSON"
    }).then(data =>
    {
        let dirPath = dirname(outputFilePath);

        // create the directory (and its parents) if it doesn't exist
        if(!fs.existsSync(dirPath))
            fs.mkdirSync(dirPath, {recursive: true});
        
        fs.writeFileSync(outputFilePath, JSON.stringify(data));
    });
}

export default exportTasks;