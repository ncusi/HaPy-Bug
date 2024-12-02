import axios from "axios";

function makeApiRequest(method, host, authorizationToken, path, data = null)
{
    const config =
    {
        method: method,
        url: `http://${host}/api/${path}`,
        headers:
        {
            Authorization: `Token ${authorizationToken}`
        }
    };

    if(data)
        method === "GET" ? config.params = data : config.data = data;
    
    return axios(config)
            .then(response => Promise.resolve(response.data))
            .catch(error =>
            {
                // The request was made and the server responded with a status code
                // that falls out of the range of 2xx
                if(error.response)
                    error =
                    {
                        headers: error.response.headers,
                        status: error.response.status,
                        errorResponse: error.response.data
                    };
                // The request was made but no response was received
                // `error.request` is an instance of http.ClientRequest in node.js
                else if(error.request)
                    error =
                    {
                        errorRequest: error.request
                    };
                // Something happened in setting up the request that triggered an Error
                else
                    error =
                    {
                        error: error.message
                    };
                
                return Promise.reject(error);
            });
}

export default makeApiRequest;