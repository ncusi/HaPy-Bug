import {removeWhitespaces} from "./util.js";

class FileCategory
{
    constructor(name, color)
    {
        this.name = name;
        this.color = color;
    }
}

const FILE_CATEGORY_CLASS_NAME_PREFIX = "file-category-";

// fileCategoryName may contain whitespaces, which are not allowed in css class name
const getFileCategoryClassName = fileCategoryName => FILE_CATEGORY_CLASS_NAME_PREFIX + removeWhitespaces(fileCategoryName);

function createFileCategoryCssClasses(fileCategories)
{
    let style = document.createElement("style");

    fileCategories.forEach(fileCategory =>
    {
        // class name in css must be escaped, but not in js
        style.innerHTML +=
        `
        .${CSS.escape(getFileCategoryClassName(fileCategory.name))}
        {
            color: ${fileCategory.color};
        }
        `;
    });

    document.head.appendChild(style);
}

function createFileCategories(namesColorsArray)
{
    let categories = namesColorsArray.map(([name, color]) => new FileCategory(name, color));
    
    createFileCategoryCssClasses(categories);
    
    return categories;
}

export {
    createFileCategories,
    getFileCategoryClassName
};