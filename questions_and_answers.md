### Q1. We run scrapes continuously, both on the same websites as data changes over time and on new websites that we find interesting. How would you monitor the activity of the scrapers to make sure they were functioning and functioning correctly? 

There’s no fundamental difference between monitoring a scraper and monitoring any other critical system - it comes down to visibility, resilience, and control.

The first step is to define what “healthy” behavior looks like, and log any deviations from that baseline. This means implementing structured error logging to capture issues such as missing selectors, failed connections, or unexpected data formats. Over time, these logs provide insight into recurring issues or signs of upstream changes (e.g. layout updates on the source website), enabling proactive maintenance.

Another key principle is fault tolerance. The pipeline should degrade gracefully when encountering partial failures. Rather than crashing the whole process when a few fields are missing, the system should flag those records e.g. as “partial” or “failed,” and continue ingesting what it can. This enables business stakeholders to decide how to handle corrupted records - ignore, impute, exclude - based on downstream needs. These data quality flags are an integral part of monitoring, not just data processing.

To complement logs and flags, data quality dashboards can provide a real-time overview of scraper health - e.g. percentage of complete records, rate of extraction failures per field, or time since last successful run. These help prioritize maintenance and spot anomalies at a glance.

Finally, for time-sensitive or mission-critical pipelines, it's worth integrating alerts into communication tools (e.g. Slack, email) so issues don’t rely solely on someone manually reviewing logs or dashboards.

In short, healthy monitoring blends automated logging, graceful error handling, clear status indicators, and alerting - all with business-context awareness baked in.

### Q2. We join data from lots of sources and this can lead to sparsity in the data, often it’s a case of identifying when we are missing data and differentiating that from when data simply isn’t available. How could you determine missing data in a scalable way?

This challenge has two layers: (1) identifying whether data is truly missing vs. simply unavailable, and (2) deciding how to handle these cases at scale.

From a scraping perspective, we benefit from the structural consistency of HTML layouts - most pages under a domain or template share the same format. That makes it easier to define “expected structure” and recognize when it’s violated.

Broadly, we can categorize scraped values into:

Valid data - e.g. a correctly parsed percentage like 45.65%.

Empty values - where the field exists but has no data (e.g. -- or "").

Missing fields - where the expected HTML tag or container is absent entirely.

Invalid values - where the data format is syntactically present but semantically off (e.g. 4565 instead of a percentage).

To handle this at scale, the key is to build a consistent data validation layer into ingestion pipeline. This involves classifying each field into categories such e.g. “present,” “empty,” “missing,” or “malformed.” That distinction enables downstream systems to respond accordingly - for example, surfacing alerts, imputing values, or excluding records depending on business logic.

Automation is essential. Rules for identifying missing vs. unavailable data should be embedded directly into parsing and normalization routines so the process is consistent across all sources. Additionally, attaching lightweight metadata - such as completeness flags or lists of missing fields - allows aggregated monitoring and reporting without inspecting each record manually.

Ultimately, once these indicators are in place, it's a business decision how to act on them. Some use cases may tolerate sparse data, others may require full completeness.

### Q3. We release data on a weekly cadence, as time goes on we query more data and it can take longer to scrape and process the data we need. How would you scale the system to do more work within a shorter period of time?

Scaling is not just a technical decision - it’s a strategic one. It starts with asking not just where you want to be, but realistically where you expect to be in 3, 6, or 12 months. That difference guides whether you scale up (e.g. more compute) or out (e.g. redesigning for concurrency, distribution, and resilience).

For scrapers and ETL pipelines running on regular cadence, scaling can take several practical forms:

 - Concurrency: Introduce multithreading or multiprocessing to run scrapes in parallel across multiple sites or data points.

- Incremental work: Implement delta logic - only reprocess what has changed since the last run.

- Pipeline balance: Ensure that scaling the scrape step doesn’t bottleneck the transformation or load phase (or vice versa). Scaling must be end-to-end.

- Batching and queuing: Use queueing systems or batch workers (e.g. Celery, Airflow, Dagster) to manage and monitor load distribution.

- Storage optimization: Choose data stores aligned to the read/write patterns (e.g. OLAP systems like ClickHouse, or caching layers for intermediate stages).

Ultimately, the goal isn’t just more scraping faster, but doing it intelligently and sustainably, aligned with how frequently data changes and how urgently it’s needed.

### Q4. A recent change to the codebase has caused a feature to begin failing, the failure has made it’s way to production and needs to be resolved. What would you do to get the system back on track and reduce these sorts of incidents happening in future?

The first priority is recovery - quickly restore functionality and minimize disruption. That typically means rolling back to the last known good state. It’s not glamorous, but it’s pragmatic. Better to pause forward progress and make one step back than to keep moving forward and break production with a loose shoelace.

Once stable, it’s time to investigate. What changed? Why did the change pass through unnoticed? This involves tracing the failure to a specific commit, config, or assumption. From there, we can pinpoint which process failed - or where no process existed.

Then comes prevention. Based on the root cause, that might involve:

- Strengthening the UAT process (e.g. testing against more diverse HTML examples)

- Expanding the scope of integration tests

- Adding validation layers before loading data into downstream systems

- Introducing CI/CD gates (e.g. requiring logs to be clean or test coverage thresholds met)

Failures happen - what matters is the system’s ability to contain them, and the team’s discipline in learning from them.