# About the Data

## Data Folder Structure

```
data
  |_cleaned
  |_network
  |_original
  |_summary-stats
```

## Original Folder

[data/original/swr-citation-data-rm-new-lines.csv](data/original/swr-citation-data-rm-new-lines.csv): This is the full data set at the per article level. It is the latest cleaned version. It differs from the `enter_data_swr_citations_cleaned.csv` cleaned full set in that the additional author columns are still intact. For development, use the aforementioned file instead.

## Cleaned Folder

[data/cleaned/20220307_swr_citations_cleaned.csv](data/cleaned/20220307_swr_citations_cleaned.csv): This is the latest cleaned version of the full data set. It is an output from the following Python Jupyter Notebook in the `swr-citation` repo: `notebooks/processing/general/clean-names-journals-and-output-net-files.ipynb`. The file still includes some idiosyncratic issues from the original Excel file, but it is the set to use for development. DO NOT use the file in the `original` folder.

[data/cleaned/20220214_swr_author_to_author_with_modules.csv](data/cleaned/20220214_swr_author_to_author_with_modules.csv): This data set reduces it to a network target-source structure. It includes the infomap score, number IDs, community module numbers, and is aggregated per Year. It is an output from the following Python Jupyter Notebook in the `swr-citation` repo: `notebooks/processing/network/ftree_module_processing_all_years_auth_to_auth.ipynb`.
