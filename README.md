# Bank Publications Search & Filter Pipeline

This project automates the discovery, filtering, and scoring of listing pages for central bank publications, reports, statistics, news, and research.

## Workflow Overview

1. **Generate Queries & Search**
   - `search_and_save.py`: Reads bank info, generates search queries, runs searches, and saves results to `data/search_results/`.

2. **Filter & Score Listing Pages**
   - `filter_and_llm_listing.py`: Deduplicates and filters URLs, then uses Gemini LLM to score listing page probability. Results are saved to `data/final_output/`.

3. **Find Banks with Few Results**
   - `find_banks_with_few_results.py`: Identifies banks with 5 or fewer total search results and saves the list to `data/banks_with_few_results.json`.

## Directory Structure

```
data/
  search_results/      # Raw search results per bank
  final_output/        # LLM-scored listing pages per bank
  banks_with_few_results.json
```

## Notes

- All intermediate and final results are stored in the `data/` directory.
- LLM scoring uses Gemini 2.5 Flash.
