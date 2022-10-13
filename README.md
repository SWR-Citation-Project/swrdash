# SWR Prototype Dashboard: Tracking DEI Scholarship in Writing &amp; Rhetoric

Repo for a prototype dashboard that will help Writing and Rhetoric track and assess citational issues, politics, and exemplars in diversity, equity, and inclusion practices.

## Contributors

- [@lingeringcode](https://github.com/lingeringcode/)

## Quick Startup

### Development server

In the root folder, `swrdash`, open a terminal and run `python app.py` or `python3 app.py`. A development version of the dashboard will run automatically on a localhost port `8050`: [http://localhost:8050/](http://localhost:8050/).

### Production

We are currently using Google Cloud services. The workflow includes deploying new changes with the following Google Cloud CLI command:

```
gcloud app deploy 
```

See Google's documentation about how to setup the Cloud CLI: (https://cloud.google.com/sdk/gcloud/)[https://cloud.google.com/sdk/gcloud/]. Here is a helpful article about how to use prepare your Dash project for deployment with Google Cloud's CLI: (https://datasciencecampus.github.io/deploy-dash-with-gcp/)[https://datasciencecampus.github.io/deploy-dash-with-gcp/].

To review the logs, use:

```
gcloud app logs tail -s default
```

## Project Management

We will use Github's [Project Tracker Board](https://github.com/orgs/SWR-Citation-Project/projects/1/views/1) to monitor progress.

## Dependencies

The main dependencies include the following Python libraries:

1. `dash`
2. `pandas`
3. `plotly`

### Dash

Review Dash's documentation to get started: [https://dash.plotly.com/introduction](https://dash.plotly.com/introduction). Broadly, three technologies constitute the core of Dash:

1. `Flask` supplies the web server functionality.
2. `React.js` renders the user interface of the web page.
3. `Plotly.js` generates the charts used in your application.

Check out the Dash app gallery for inspiration: [https://dash.gallery/Portal/](https://dash.gallery/Portal/).

## Data

See the [DATA_GUIDE.md](DATA_GUIDE.md) file.

## App

[general overview]

### Resources

- [Python Dash](https://dash.plotly.com/introduction): Code library by the folks that produced Plotly, which provides a relatively easy and quick web app architecture for data dashboards.
- [Charming Data](https://www.youtube.com/c/CharmingData/search?query=python%20dash): Originally, the code herein has been modified from the [Charming Data](https://www.youtube.com/c/CharmingData/search?query=python%20dash) series for initial learning and piloting a quick way to test and deploy a prototype dashboard.