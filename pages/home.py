import os
import base64
import pandas as pd
import dash             #(version 1.8.0)
from dash import html, dash_table, dcc
from .lib.network_data.network_functions import create_row

dash.register_page(__name__,
  path="/",
  order=0
)

# resolve path
this_dir, _ = os.path.split(__file__)
image_filename = os.path.join(this_dir, "lib/assets", "cccc_logo.jpeg")
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

# Hack fix for ensuring proper rendering for the page
df = pd.DataFrame()

#---------------------------------------------------------------
# Layout for Page

layout = html.Div([
  html.Div(
    dash_table.DataTable(
      columns=[
          {"name": i, "id": i, "deletable": False, "selectable": False} for i in df.columns
      ],
    ),
    style={'display': 'none'}
  ),
  create_row(
    html.Header([
        html.Div(
          html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()))
        ),
        html.Div([
          html.H2("SWR Citational Politics Dashboard"),
          html.P("For demonstration purposes only. Do NOT use for research or reporting. The original citation data has been combined with generated fake identity metrics across race and gender to imagine possible.",
            className="disclaimer"
          ),
          html.P(
            ""
          ),
        ], className="banner_copy_container"
      )], 
      className="index_banner",
      id="header_banner")
  ),

  create_row(
    html.Section([
      dcc.Markdown('''
## Quick Summary of the Data

- **Original Sample Size**: 33,464
- **Sample Size after Cleaning**: 65,650
    * *NOTE*: The sample size more than doubled, since the original structure of the data consolidated all authors separately from the first listed author in its own column. We chose to parse out the scholars within the additional author column, so we could achieve a more accurate picture of scholars citing each other, despite it being a multi-authored piece. To note, all citation sums for cited authors account for this structure.

## About the Data

Our team has created a data set that documents the authors published or cited in 11 Composition and Rhetoric journals listed below between 2012-2019. We chose many of these journals, since some of them do not report their citation statistics to indexing engines, such as Scopus and Web of Science. This meant that we needed to collect data manually.

- College Composition and Communication
- College English
- Community Literacy Journal
- Composition Studies
- Enculturation
- Journal of Basic Writing
- Peitho
- Rhetoric Review
- Writing Across Curriculum Journal
- Writing Center Journal
- Writing Program Administration Journal

We collected 65,650 data points on who is published and cited (and by whom). The data is both shocking and unsurprising. From a preliminary analysis of the over 98,636 terms used in both titles and citations, African American appeared only 77 times; Native American/Indigenous, 47 times. The analysis also demonstrated that out of the top 25 cited scholars, only 8 were scholars of color, four of whom are multiply marginalized. And these exclusions seem to occur despite inclusion of scholars of color on journal editorial boards. These summary results of the data confirm the repeated arguments made by scholars of color about the lack of equity, inclusion, and linguistic justice in the field's top journals.

### Provenance

Beginning in June of 2019, Steve Parks and Kevin Smith created a simple Google Sheets file to manually record citations. (We would learn later that this spreadsheet was not formatted correctly for the type of analysis we envisioned.) We started with a list of 17 journals. In consultation with the Studies in Writing and Rhetoric (SWR) Board, we reduced the list of 11 journals that we report on here. Over the course of the next two years, Parks hired a series of graduate and undergraduate research assistants to record all the citations for each article published between 2012 and 2019, producing 34,464 citation records. When [Chris Lindgren](https://clndgrn.com) joined the project in early 2021, he spent another few months using the Python programming language to reformat the structure and clean the data (standardizing capitalization, spelling, and other anomalies) to prepare it for analysis.
      '''),
    ],
    className="max_width__vw_70",
    id="")
  ),
])