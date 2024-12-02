import fs from "fs";

const readFile = filePath => fs.readFileSync(filePath, "utf-8");

const readJsonFile = filePath => JSON.parse(readFile(filePath));

function exitOnError(error)
{
    console.error(error);

    // exit with an error code to indicate something went wrong
    process.exit(1);
}

export {
    readFile,
    readJsonFile,
    exitOnError
};