import {createFileCategories} from "./d2h-hook/file-category.js";
import {createLineCategories} from "./d2h-hook/line-category.js";

let fileCategories =
[
    ["programming",   "red"],
    ["documentation", "orange"],
    ["test",          "lightskyblue"],
    ["project",       "#C4B454"],
    ["data",          "lime"],
    ["markup",        "yellow"],
    ["other",         "orchid"]
];

let lineCategories =
[
    [["bug(fix)",                "B/F"], "red"],
    [["bug(fix) + refactoring", "BF+R"], "red"],
    [["documentation",           "doc"], "orange"],
    ["test",                             "lightskyblue"],
    [["test + refactoring",      "T+R"], "lightskyblue"],
    [["refactoring",           "R-ing"], "yellow"],
    [["other",                   "oth"], "orchid"]
];

function createCategories()
{
    fileCategories = createFileCategories(fileCategories);
    lineCategories = createLineCategories(lineCategories);
}

export {
    fileCategories,
    lineCategories,
    createCategories
};