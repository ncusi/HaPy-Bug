# Quick-start

1. Install, build and start server with newly created labeling projects
   ```bash
   npm run all
   ```

   If the docker volume containing label studio server data already exists (e.g. because the scripts have previously been run on your machine), you will be asked if you also want to remove it.

2. You are ready to start annotating.

# Detailed guide

## Setup

Clone [label-studio-frontend](https://github.com/ncusi/label-studio-frontend) repository and install all required dependencies
```bash
npm run setup
```

## Build

Build label studio frontend and integrate it with the backend
```bash
npm run build 
```

## Usage

1. Start label studio server with newly created labeling projects
   ```bash
   npm run start
   ```

   If the docker volume containing label studio server data already exists (e.g. because the scripts have previously been run on your machine), you will be asked if you also want to remove it.

2. You are ready to start annotating.

## Export

At any time you can export all the annotated tasks from the server
```bash
npm run export
```

## Clear

You can remove the docker volume containing label studio server data (e.g. users, labeling projects and annotated tasks)
```bash
npm run clear
```

This is useful if you had rebuilt the frontend and want the changes to take place, or if you want to proceed with clear server state.

You will be asked for confirmation.

## Finish

When you are done with the labeling projects, you can export all the annotated tasks and kill the server
```bash
npm run finish
```

If the docker volume containing label studio server data exists, you will be asked if you also want to remove it.