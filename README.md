<h1> Repository for the Final project of the Data Science and Advanced Python Course </h1>

By Don Enrico Esteve (P9550217B) and Elizabeth Vaisman (318775277) 

<h3> Directory Structure </h3>

```
 |-DS_Python_Paper.pdf
 |-requirements.txt
 |-README.md
 |-DS_Python_Project.code-workspace
 |-Implementation
 | |-pyproject.toml
 | |-__init__.py
 | |-src
 | |-tests
 | |-SUBS_DIR (Subjects' data must be manually downloaded and placed in corresponding folders here) 
 | |-README_Implementation.md
 | |-test_csd_report.html
 |-DS_Python_Presentation.pptx
 |-Replication
 | |-tests
 | |-README_Replication.md
 | |-data (Must be manually downloaded and placed here)
 | |-src
 ```

<h3> Rationale and Objectives </h3>
The project consists of two parts: pipeline replication and pipeline implementation. While this project aims to reproduce published results, after all, the article aims to outline
the full implementation of oscillatory activity and functional connectivity analyses. As such, we aim to translate their proposed pipeline to a MEG dataset obtained from the MEG-BIU lab (food dataset).

<h3> Assumptions and Hypotheses </h3>
Given the extensive pipeline, it is assumed that differences between the original and replicated results arise. Similarly, during pipeline implementation, it is hypothesized that differences in time-frequency representations between image categories and between presentations arise.

<h3> Pipeline Replication </h3>

Pipeline replication entails reproducing all the results of the selected article "Analysis of Functional Connectivity and Oscillatory Power Using DICS: From Raw MEG Data to Group-Level Statistics in Python" (van Vliet et al., 2018). The link for this article is: https://doi.org/10.3389/fnins.2018.00586

The Python scripts present here are not meant to be used standalone. It depends on running all numbered (00-12) Python scripts provided by van Vliet et al. (2018) in their repository: https://github.com/AaltoImagingLanguage/conpy/tree/master/scripts

For proprietary reasons, no data has been uploaded to this section. Instead, perform "00_fetch_data.py" found in the link above.

Read the Replication/README_Replication.md for a detailed methodology of how the replication was performed.

<h3> Pipeline Implementation </h3>

Pipeline implementation entails applying the pipeline of van Vliet et al. (2018) to our MEG food dataset, obtained from the MEG-BIU Laboratory.

Read the Replication/README.md for a detailed methodology of how the implementation was performed.

<h3> Submittables </h3>
Two files are available alongside the respective directories for pipeline replication and implementation: (1) "DS_Python_Paper.pdf" serves as the report for this project in IMRAD format, and (2) "DS_Python_Presentation.pptx" was used for presenting the project last 01/30/2025. 

Within each directory, the following can be found: "README.md", "src" (containing main.py), and "tests" are found.

<h3> MUST READ: Other files </h3>
The "requirements.txt" file contains all necessary modules and packages for the pipeline replication and implementation. This should be downloaded by 


pip install -r requirements.txt


The "DSC_Python_pyproject.toml" and "DSC_Python_Project.code-workspace" files are included for completion.

<h3> Important Note! </h3>
To install conpy for the replication part run: 
    pip install https://github.com/aaltoimaginglanguage/conpy/zipball/master
