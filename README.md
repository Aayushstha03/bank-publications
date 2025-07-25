# Bank Publications Search & Filter Pipeline

This project automates the discovery, filtering, and scoring of listing pages for central bank publications, reports, statistics, news, and research.


## Workflow Overview


1. **Search for Bank Listing Pages**
   - `1.search.py`: Reads bank information, generates targeted search queries for each bank, performs web searches, and saves the raw results to `data/search_results/`.

2. **Filter, Deduplicate, and Score URLs**
   - `2.filter_urls.py`: Deduplicates and filters the collected URLs, then uses Gemini LLM to score the likelihood that each URL is a relevant listing page. The scored results are saved to `data/final_output/`.

3. **Collect High-Confidence Listing URLs**
   - `3.collect_high_confidence_listing_urls.py`: Aggregates and saves high-confidence listing URLs for each bank based on previous filtering and scoring steps.

---

You can run the entire pipeline in sequence using `runall.py`, which executes all the main scripts in order.


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

