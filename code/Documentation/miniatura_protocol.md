# Protocol for Manual Software Bug Annotation in Python:

* For each bug we have a description of what was the bug 
  * commit message,
  * CVE info/issue description.

Additionally we will have information about dataset, this can help to identyfie the project.

* Bugs will be related to security issues (ie. CVE, security software bugs, etc), ie. any bug that makes software vulnerable.
* Following datasets will be used
  * WEB crawled commits assosciated with CVE 
  * Commits from CVE database
  * Bugs in py isolated bugs in python projects (Only project name).
* User will have to annotate a diff that will include a fix to specific bug.

Where task for annotators are as follows.

## 1. Assign each file into one of categories:

Primary categories:

* project - any project managment files (Warning: can be source code, markup, txt) 
* programming - source code
* tests - any files used for tests
* documentation - any form of documentation

Secondary categories:

* data - data used in the project
* markup - markup files like html or xml used as part of the project
* other - anything not matching

Automatic annotation will be available, but it needs to be checked and fixed (if needed).
Where multiple categories can be assigned, the primary category takes precedence over the secondary.


## 2. Manually annotate rest of the lines as:

**Types of annotations:**

   * bug(fix) (line with a bug or line fixing a bug)
   * bug(fix) + refactoring (line fixing the bug along with code refactoring)

   * documentation
     * e.g. there is multi-line documentation in the line (`"""apostrophes"""` or in `/* */`) and it is not possible to annotate it automatically,
     * the line is documentation but has been mislabeled,
     * the file type and its contents where incorrectly annotated.

   * test (adding a new one, fixing or removing an old test that supports error checking)
   * test + refactoring (adding a new one, repairing or removing an old test along with code refactoring)
  
   * refactoring (refactoring changes that do not affect the overall operation of the system, improve the readability or structure of the code)
 
   * other (other bug entry, new functionality, changes not falling into the above categories)
     * update of library/application version (to be released) which will include fix in the future


## 3. Projects type 
Annotate type of project where bug in software was found
a) Bug in core python or core python library
Bug found in core python implementation (any python implementation).

Examples: 

* urllib is part of python standard library
  * https://nvd.nist.gov/vuln/detail/CVE-2019-9948
  * https://nvd.nist.gov/vuln/detail/CVE-2021-3733

b) Bug in this python application/library 
Bug in application/library. Main functionality is in Python or is intendent for Python/

Examples: 
 * ansible is a python application 
   * https://nvd.nist.gov/vuln/detail/CVE-2016-8647
 * CairoSvg is a python library
   * https://nvd.nist.gov/vuln/detail/CVE-2021-21236

c) Other

For example:
* python project that fixes dependencies (bug is in other project): eg. changes in requirments.txt
* projects writen mainly in other languages that have python interface: eg. spark
* project has some python scripts inside and this fix is mainly for this script 

4. Reviewer Confidence Level

* Confident reviewer: YES / NO
* Problematic: YES / NO

# Examples

Model annotations can be found in **model annotations** project.
These annotations were established by 3 experts. In the first run, the experts annotated independently. In the second run, the annotations were compared, lines with diverging annotations were discussed, and one version was chosen by consensus.

