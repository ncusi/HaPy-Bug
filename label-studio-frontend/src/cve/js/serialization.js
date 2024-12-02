const getSelectedCategory = dropDownList => dropDownList.value;

const serializeRatedLine = ratedLine =>
({
    lineNumber: ratedLine.lineNumber,
    category: getSelectedCategory(ratedLine.dropDownList)
});

const serializeRatedFile = ratedFile =>
({
    fileName: ratedFile.fileName,
    category: getSelectedCategory(ratedFile.dropDownList),
    lines:
    {
        afterChange: ratedFile.ratedLinesAfterChange.map(serializeRatedLine),
        beforeChange: ratedFile.ratedLinesBeforeChange.map(serializeRatedLine)
    }
});

const serializeLabeledHyperlink = labeledHyperlink =>
({
    url: labeledHyperlink.url,
    dates: labeledHyperlink.dates,
    labels: labeledHyperlink.labels
});

const CVE_ANNOTATION_RESULT_TYPE_NAME = "cve";

const serializeCVEAnnotation = cve =>
({
    type: CVE_ANNOTATION_RESULT_TYPE_NAME,
    value:
    {
        hyperlinks: cve.labeledHyperlinks.map(serializeLabeledHyperlink),
        diffsFiles: cve.diffsRatedFiles.map(ratedFiles => ratedFiles.map(serializeRatedFile))
    }
});

export {
    CVE_ANNOTATION_RESULT_TYPE_NAME,
    serializeCVEAnnotation
};