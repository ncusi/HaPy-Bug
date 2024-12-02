import {createRatedFiles} from "./d2h-hook/main.js";

import {Diff2HtmlUI} from "diff2html/lib/ui/js/diff2html-ui.js";

function createGitCommitMessageContainer(commitMessage)
{
    const CLASS_NAME = "git-commit-message";

    let container = document.createElement("div");
    container.className = `${CLASS_NAME}-container`;

    let span = document.createElement("span");
    span.className = CLASS_NAME;
    span.innerText = commitMessage;

    container.appendChild(span);

    return container;
}

function createGitDiffContainer(diff)
{
    let container = document.createElement("div");

    const diff2htmlUi = new Diff2HtmlUI(container, diff,
    {
        matching: "lines",
        outputFormat: "side-by-side"
    });
    
    diff2htmlUi.draw();
    
    return container;
}

function fillGitCommitsContainer(container, gitCommits, diffsCategorizedFiles)
{
    if(gitCommits.length !== diffsCategorizedFiles.length)
        throw new Error(`There must be one commit for each array of categorized files (got: ${gitCommits.length} commits and: ${diffsCategorizedFiles.length} arrays)`);

    let diffsRatedFiles = gitCommits.map((commit, i) =>
    {
        let gitDiffContainer = createGitDiffContainer(commit.diff);

        let ratedFiles = createRatedFiles(gitDiffContainer, diffsCategorizedFiles[i]);

        let gitCommitContainer = document.createElement("div");
        container.appendChild(gitCommitContainer);

        gitCommitContainer.appendChild(createGitCommitMessageContainer(commit.message));
        gitCommitContainer.appendChild(gitDiffContainer);

        return ratedFiles;
    });

    return diffsRatedFiles;
}

export {
    fillGitCommitsContainer
};