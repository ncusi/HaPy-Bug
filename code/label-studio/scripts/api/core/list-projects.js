import makeApiRequest from "./api-request.js";

function listProjects(host, authorizationToken)
{
     return makeApiRequest("GET", host, authorizationToken, "projects",
     {
          ordering: "id"
     }).then(data => Promise.resolve(data.results));
}

export default listProjects;