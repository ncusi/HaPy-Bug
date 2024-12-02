// import styles for webpack MiniCssExtractPlugin plugin
import "./styles.js";

import {createCategories} from "./diff-categorization/categories.js";

import {fillGitCommitsContainer} from "./diff-categorization/main.js";
import {fillHyperlinksContainer} from "./hyperlink-labeling/main.js";

import {CVE_ANNOTATION_RESULT_TYPE_NAME, serializeCVEAnnotation} from "./serialization.js";

const HYPERLINKS_CONTAINER_ID = "hyperlinks-container";
const GIT_COMMITS_CONTAINER_ID = "git-commits-container";

const GIT_COMMITS_CONTAINER_CVE_PROPERTY_NAME = "gitCommitsContainer";
const HYPERLINKS_CONTAINER_CVE_PROPERTY_NAME = "hyperlinksContainer";

// before any label studio instance has been created it's set to null
// but there can be many subsequent instances (e.g. when joining and
// leaving annotation panel)
let currentLabelStudio = null;

// task.data is a string here
const getTaskData = () => JSON.parse(currentLabelStudio.task.data);

const getInitialAnnotation = () => getTaskData().initialAnnotation;

function createContainer(id)
{
    let container = document.createElement("div");
    container.id = id;

    return container;
}

function createHyperlinksContainer(cve)
{
    // make a deep clone of the initial annotation data
    // because we want to add/remove labels later
    // and we obviously don't want to modify the same reference
    const labeledHyperlinks = structuredClone(cve.annotation.hyperlinks);

    const hyperlinksContainer = createContainer(HYPERLINKS_CONTAINER_ID);

    fillHyperlinksContainer(hyperlinksContainer, labeledHyperlinks, getInitialAnnotation().hyperlinks);
    
    cve.labeledHyperlinks = labeledHyperlinks;
    cve[HYPERLINKS_CONTAINER_CVE_PROPERTY_NAME] = hyperlinksContainer;
}

function createGitCommitsContainer(cve)
{
    const gitCommitsContainer = createContainer(GIT_COMMITS_CONTAINER_ID);

    let diffsRatedFiles = fillGitCommitsContainer(gitCommitsContainer, getTaskData().gitCommits, cve.annotation.diffsFiles);

    cve.diffsRatedFiles = diffsRatedFiles;
    cve[GIT_COMMITS_CONTAINER_CVE_PROPERTY_NAME] = gitCommitsContainer;
}

// annotation is loaded for the first time
// (it's supposed to contain either previously saved categorization
// or initial categorization gained in some other way, e.g. using a heuristic).
// this function creates all custom containers because if only one got loaded,
// the other one's data would be undefined when serializing the annotation,
// so we need to create all at once if only one gets created.
// also here `annotation.serializeAnnotation` gets hooked
function onAnnotationLoaded(annotation)
{
    const cve = annotation.cve;

    const originalSerializeAnnotation = annotation.serializeAnnotation.bind(annotation);

    annotation.serializeAnnotation = options =>
    {
        let serialized = originalSerializeAnnotation(options);

        serialized.push(serializeCVEAnnotation(cve));
        
        return serialized;
    };

    // create the custom containers
    createGitCommitsContainer(cve);
    createHyperlinksContainer(cve);
}

function getSelectedAnnotation()
{
    const labelStudio = currentLabelStudio;

    const annotation = labelStudio.annotationStore.selected;
    
    // sometimes (e.g. when viewing a prediction)
    // the annotation is displayed without being selected first so
    // it has to be set up here
    if(!annotation.cve)
        annotation.cve = {};

    // when creating a new annotation it's been selected (so annotation.cve is equal to {})
    // but it hasn't been deserialized so it has to be set up here
    if(!annotation.cve.annotation)
        annotation.cve.annotation = getInitialAnnotation();

    return annotation;
}

function unfoldedContainerCollapseTag(target, containerId, containerCvePropertyName)
{
    let container = document.getElementById(containerId);

    // if the container doesn't exist then its Collapse tag
    // surely wasn't unfolded
    if(!container)
        return false;
    
    // if this unfolded Collapse tag didn't contain the container
    // then it wasn't the tag we were looking for
    if(!target.contains(container))
        return false;
    
    const annotation = getSelectedAnnotation();

    const cve = annotation.cve;
    
    // when not opening back a previously created annotation
    if(!cve[containerCvePropertyName])
        onAnnotationLoaded(annotation);

    container.replaceWith(cve[containerCvePropertyName]);

    return true;
}

function onUnfoldedCollapseTag(target)
{
    const containerDescriptors =
    [
        [GIT_COMMITS_CONTAINER_ID, GIT_COMMITS_CONTAINER_CVE_PROPERTY_NAME],
        [HYPERLINKS_CONTAINER_ID, HYPERLINKS_CONTAINER_CVE_PROPERTY_NAME]
    ];

    return containerDescriptors.some(descriptor => unfoldedContainerCollapseTag(target, ...descriptor));
}

function createMutationObserver()
{
    const observer = new MutationObserver(mutationList =>
    {
        // if the mutation wasn't about unfolding Collapse tag then skip it
        if(mutationList.length > 1)
            return;
        
        let target = mutationList[0].target;

        // same check as above
        if(!target.classList.contains("ant-collapse-item"))
            return;
        
        onUnfoldedCollapseTag(target);
    });

    observer.observe(document.body,
    {
        childList: true,
        subtree: true
    });
}

// in production build the properties we need to modify are read-only
// so disable creating read-only properties before they're created
function disableCreatingReadOnlyProperties()
{
    const originalDefineProperty = Object.defineProperty;

    Object.defineProperty = (object, property, attributes) =>
    {
        if(attributes && attributes.writable === false)
            attributes.writable = true;

        return originalDefineProperty(object, property, attributes);
    };
}

function onHookFirstCall()
{
    createCategories();

    createMutationObserver();
    
    disableCreatingReadOnlyProperties();
}

function hookDeserializeResults(annotation)
{
    const originalDeserializeResults = annotation.deserializeResults.bind(annotation);

    annotation.deserializeResults = (results, options) =>
    {                
        originalDeserializeResults(results, options);

        // find our annotation result (there's only 1 at most)
        let cveAnnotationResult = results.find(result => result.type === CVE_ANNOTATION_RESULT_TYPE_NAME);

        // if there's no cve annotation result then it's likely this annotation has been loaded from a prediction
        // (which contains only dates), so we need to get categorization data from task data
        let cveAnnotation = cveAnnotationResult ? cveAnnotationResult.value : getInitialAnnotation();
        
        annotation.cve.annotation = cveAnnotation;

        // _initialAnnotationObj is used when copying annotations.
        // `originalDeserializeResults` removes "broken" results
        // (e.g. those without valid from_name and to_name fields)
        // so we need to update it with the cve results here
        // if we want annotation copying to work correctly.
        // if we don't set it here then initial annotation will be copied and used
        if(cveAnnotationResult)
            annotation._initialAnnotationObj.push(cveAnnotationResult);
        
        // hook `serializeAnnotation` here so that when no container Collapse tag is unfolded
        // and the user presses "Update" for the annotation, the correct results are
        // saved (instead of default, initial annotation, which causes all annotations to be lost)
        onAnnotationLoaded(annotation);
    };
}

function onLabelStudioConstructor(labelStudio)
{
    // create categories and mutation observer only the first time the hook code is called
    if(!currentLabelStudio)
        onHookFirstCall();
    
    labelStudio.options.interfaces = 
    [
        "panel",
        "topbar",
        "update",
        "submit",
        "controls",
        "instruction",
        "side-column",
        "edit-history",
        "topbar:prevnext",
        "annotations:tabs",
        "annotations:delete",
        "annotations:add-new",
        "annotations:history",
        "predictions:menu",
        "predictions:tabs"
    ];

    const events = labelStudio.events;

    // labelStudio obtained here is different than the one we already have
    // (the one whose constructor we hooked)
    // and we need this one
    events.on("labelStudioLoad", labelStudio =>
    {
        currentLabelStudio = labelStudio;

        events.on("selectAnnotation", annotation =>
        {
            // if this annotation has already been set up before then skip modifying its properties
            if(annotation.cve)
                return;

            annotation.cve = {};

            hookDeserializeResults(annotation);
        });
    });
}

export {
    onLabelStudioConstructor
};
