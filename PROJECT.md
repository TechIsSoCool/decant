# docx_pdf_to_md

## Goal
Create a containerized application which allows the user to drag and drop a `docx` or `pdf` file onto a landing component, converts that file to a markdown formatted file, and send the markdown file to the browser as a download.

## Context
Passing docx and pdf files to Claude requires tool use, toekn usage, and time when the goal is simply to impart the content. Passing markdown files is assumed to be more efficient. This tool helps prepare files for sharing with Claude.

## Functional Requirements
- The deployed application must be in a Docker container and be accessible from a web browser.
- The application must determine if the dropped file is docx, pdf, or neither format. 
   - If the file is not a pdf or docx file, then a message is displayed (toast maybe) saying the file type is not supported. The content is discarded. The application is ready for another file.
- Formatting in the orginal document and supported in markdown is preserved to extent possible. 
- Favor content integrity over formatting integrity.
- The download filename should be the same base name as the dropped document, with an `.md` extension.
- This is for local use only. Hardening for production, handling of potentially malicious files is not required

## Non-functional Requirements
- Can be implemented in Python or Node.js
