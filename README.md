# AI-Subdivision-Plan-Review-FastAPI-React

A subdivision plan reviewing tool that incorporates AI to help city engineers quickly review basic information of subdivision plans to make sure major plan issues are resolved.  This project uses FastAPI for the backend, ReactJS and TailWindCSS for the front-end, and PostgreSQL for the database.

## Features

- Allow engineers to upload PDFs for analysis and store those files with the results
- Allow the tool to parse and analyze uploaded PDFs
- Implement authentication/authorization
- Calls external APIs or implement CRUD actions for zoning law data
- Also implement CRUD actions on uploaded plan files

## Database Design/Structure

**Users**

- ID (UUID primary key)
- First Name (string)
- Last Name (string)
- Username (string)
- Email (string)
- Password (string)
- Status (enum (engineer or admin))

**Plans**

- ID (UUID primary key)
- User ID (UUID foreign key)
- Title (string)
- File (PDF)
- AI review notes (either text or JSON)