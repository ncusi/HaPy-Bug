const DATALIST_HYPERLINK_LABELS_ID = "hyperlink-labels";

const getHyperlinkLabelsDatalist = () => document.getElementById(DATALIST_HYPERLINK_LABELS_ID);

function createDatalistOption(text)
{
    let option = document.createElement("option");
    option.value = text;

    return option;
}

const getDatalistOptions = datalist => Array.from(datalist.children);

function createLabel(container, text, hyperlinkLabels, isNew)
{
    let label = document.createElement("span");
    label.innerText = text;
    label.className = "hyperlink-label";
    label.onclick = () =>
    {
        // remove the label from annotation result, datalist and the label's container
        let index = hyperlinkLabels.indexOf(text);

        hyperlinkLabels.splice(index, 1);

        container.removeChild(label);
    };

    let datalist = getHyperlinkLabelsDatalist();

    // only append to the datalist if it's a newly created label
    // (created by the user for the first time)
    // and such label doesn't exist yet
    // (maybe in another hyperlink labels container)
    if(isNew && !getDatalistOptions(datalist).some(option => option.value === text))
        datalist.appendChild(createDatalistOption(text))

    container.appendChild(label);
}

function createHyperlinkUrlContainer(url)
{
    let container = document.createElement("div");
    container.className = "hyperlink-url-container";

    let hyperlink = document.createElement("a");
    hyperlink.href = url;
    hyperlink.innerText = url;
    // open hyperlink in new tab
    hyperlink.target = "_blank";

    container.appendChild(hyperlink);

    return container;
}

const capitalizeFirstLetter = string => string.charAt(0).toUpperCase() + string.slice(1);

function createAddLabelContainer(labelsContainer, labels)
{
    let container = document.createElement("div");
    container.className = "hyperlink-add-label-container";

    let input = document.createElement("input");
    input.type = "search";
    input.placeholder = "New label...";
    input.setAttribute("list", DATALIST_HYPERLINK_LABELS_ID);
    
    let button = document.createElement("button");
    button.innerText = "Add label";
    button.onclick = () =>
    {
        let text = input.value.trim();

        // if nothing has been typed then don't create an empty label
        if(!text.length)
            return;
        
        // if such label already exists (can have varying case) then don't create a copy of it
        if(labels.map(label => label.toLowerCase()).includes(text.toLowerCase()))
            return;

        text = capitalizeFirstLetter(text);

        labels.push(text);

        createLabel(labelsContainer, text, labels, true);
    };
    
    container.appendChild(input);
    container.appendChild(button);

    return container;
}

const createLabels = (container, labels) => labels.forEach(label => createLabel(container, label, labels, false));

function createHyperlinkDatePickersContainer(dates)
{
    let labels = Object.entries(dates).map(([name, date]) =>
    {
        let label = document.createElement("label");
        label.innerText = `${capitalizeFirstLetter(name)} date found at the site:`;

        let input = document.createElement("input");
        input.value = date;
        input.type = "date";
        input.onchange = () => dates[name] = input.value;

        label.appendChild(input);

        return label;
    });
    
    let container = document.createElement("div");
    container.className = "hyperlink-date-pickers-container";
    container.append(...labels);

    return container;
}

function fillHyperlinkLabelingContainer(container, labeledHyperlink)
{
    let labelsContainer = document.createElement("div");
    labelsContainer.className = "hyperlink-labels-container";

    createLabels(labelsContainer, labeledHyperlink.labels);

    container.append
    (
        createHyperlinkUrlContainer(labeledHyperlink.url),
        createHyperlinkDatePickersContainer(labeledHyperlink.dates),
        createAddLabelContainer(labelsContainer, labeledHyperlink.labels),
        labelsContainer
    );
}

// create <datalist> used for hinting "Add label" <input> tag.
// it should contain initial labels for current task and labels defined by the user
function createHyperlinkLabelsDatalist(labeledHyperlinks, initialAnnotationHyperlinks)
{
    let labels = labeledHyperlinks.flatMap(hyperlink => hyperlink.labels);
    let initialLabels = initialAnnotationHyperlinks.flatMap(hyperlink => hyperlink.labels);

    labels = initialLabels.concat(labels);

    // remove duplicate labels
    labels = [...new Set(labels)];

    let datalist = getHyperlinkLabelsDatalist();

    // create the datalist only if it hasn't been created yet
    // or if contains different labels (that means another annotation has been selected)
    if(!datalist)
    {
        datalist = document.createElement("datalist");
        datalist.id = DATALIST_HYPERLINK_LABELS_ID;

        document.head.appendChild(datalist);
    }
    else
    {
        let options = getDatalistOptions(datalist);

        // if the datalist labels are equal then don't do anything
        if(options.length === labels.length && options.every((option, i) => option.value === labels[i]))
            return;
        
        // remove all current labels
        // if this datalist is different than the previous one
        datalist.replaceChildren();
    }

    // create datalist options from labels (as search hints) and append them
    datalist.append(...labels.map(createDatalistOption));
}

function createHyperlinkLabelingContainer(hyperlink)
{
    let container = document.createElement("div");
    container.className = "hyperlink-labeling-container";

    fillHyperlinkLabelingContainer(container, hyperlink);

    return container;
}

function fillHyperlinksContainer(container, labeledHyperlinks, initialAnnotationHyperlinks)
{
    createHyperlinkLabelsDatalist(labeledHyperlinks, initialAnnotationHyperlinks);

    // create containers for every hyperlink
    labeledHyperlinks.forEach(hyperlink => container.appendChild(createHyperlinkLabelingContainer(hyperlink)));
}

export {
    fillHyperlinksContainer
};