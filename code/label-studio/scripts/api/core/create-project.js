import makeApiRequest from "./api-request.js";

function createProject(host, authorizationToken, projectTitle, labelConfig)
{
    return makeApiRequest("POST", host, authorizationToken, "projects",
    {
        title: projectTitle,
        label_config: labelConfig
    });
}

export default createProject;