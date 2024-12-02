import yesno from "yesno";
import minimist from "minimist-lite";
import child_process from "child_process";

function spawnProcess(command)
{
    let args = command.split(" ");

    let ret = child_process.spawnSync(args.shift(), args);

    // return true if process suceeded, else false
    return ret.status === 0;
}

async function main(volumeName)
{
    // if the volume doesn't exist then return - nothing to remove
    if(!spawnProcess(`docker volume inspect ${volumeName}`))
        return;

    // ask for removal confirmation
    const ok = await yesno
    ({
        question:
            "Found an existing docker volume containing label studio server state data.\n\n" +
            "Are you sure you want to remove the volume? " +
            "WARNING: This will remove all label studio server state data " +
            "(e.g. users, labeling projects and annotated tasks) and cannot be undone; " +
            "specifically, you might want to export all the annotated tasks from the server first. " +
            "[y/N]",
        defaultValue: false
    });

    // exit if the answer was "no"
    if(!ok)
        return;

    // if the container existed then kill the server first,
    // otherwise "docker volume rm" would surely fail
    if(!spawnProcess("npm run server:kill") || !spawnProcess(`docker volume rm ${volumeName}`))
        process.exit(1);
}

const argv = minimist(process.argv.slice(2));

await main(argv.name);