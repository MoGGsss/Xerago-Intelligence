"""Canonical Phase 8 RSS source catalog (seed data)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RssSourceSeed:
    source_id: str
    source_name: str
    source_url: str
    rss_url: str
    source_tier: int
    active_flag: bool = True


# Tier 1 — AI vendors and strategic platforms (highest poll priority)
TIER_1_SOURCES: tuple[RssSourceSeed, ...] = (
    RssSourceSeed(
        source_id="openai-blog",
        source_name="OpenAI",
        source_url="https://openai.com/news",
        rss_url="https://openai.com/news/rss.xml",
        source_tier=1,
    ),
    RssSourceSeed(
        source_id="google-ai-blog",
        source_name="Google AI Blog",
        source_url="https://blog.google/technology/ai",
        rss_url="https://blog.google/technology/ai/rss/",
        source_tier=1,
    ),
    RssSourceSeed(
        source_id="ms-ai-blog",
        source_name="Microsoft AI Blog",
        source_url="https://blogs.microsoft.com/ai",
        rss_url="https://blogs.microsoft.com/ai/feed/",
        source_tier=1,
    ),
    RssSourceSeed(
        source_id="anthropic-news",
        source_name="Anthropic",
        source_url="https://www.anthropic.com/news",
        rss_url=(
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/"
            "feeds/feed_anthropic_news.xml"
        ),
        source_tier=1,
    ),
    RssSourceSeed(
        source_id="adobe-blog",
        source_name="Adobe",
        source_url="https://medium.com/adobetech",
        rss_url="https://medium.com/feed/adobetech",
        source_tier=1,
    ),
    RssSourceSeed(
        source_id="sf-blog",
        source_name="Salesforce AI",
        source_url="https://www.salesforce.com/blog",
        rss_url="https://www.salesforce.com/blog/feed/",
        source_tier=1,
    ),
    RssSourceSeed(
        source_id="ibm-research",
        source_name="IBM AI",
        source_url="https://research.ibm.com/blog",
        rss_url="https://research.ibm.com/rss",
        source_tier=1,
    ),
    RssSourceSeed(
        source_id="hf-blog",
        source_name="HuggingFace",
        source_url="https://huggingface.co/blog",
        rss_url="https://huggingface.co/blog/feed.xml",
        source_tier=1,
    ),
)

# Tier 2 — research and industry intelligence
TIER_2_SOURCES: tuple[RssSourceSeed, ...] = (
    RssSourceSeed(
        source_id="stanford-hai",
        source_name="Stanford HAI",
        source_url="https://hai.stanford.edu",
        rss_url=(
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/"
            "feeds/feed_the_batch.xml"
        ),
        source_tier=2,
    ),
    RssSourceSeed(
        source_id="pwc-trending",
        source_name="Papers With Code",
        source_url="https://paperswithcode.com",
        rss_url="https://rss.arxiv.org/rss/cs.LG",
        source_tier=2,
    ),
    RssSourceSeed(
        source_id="tldr-ai",
        source_name="TLDR AI",
        source_url="https://tldr.tech/ai",
        rss_url="https://bullrich.dev/tldr-rss/ai.rss",
        source_tier=2,
    ),
    RssSourceSeed(
        source_id="tc-ai",
        source_name="TechCrunch AI",
        source_url="https://techcrunch.com/category/artificial-intelligence",
        rss_url="https://techcrunch.com/category/artificial-intelligence/feed/",
        source_tier=2,
    ),
    RssSourceSeed(
        source_id="verge-ai",
        source_name="The Verge AI",
        source_url="https://www.theverge.com/ai-artificial-intelligence",
        rss_url="https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        source_tier=2,
    ),
    RssSourceSeed(
        source_id="mit-tech-review-ai",
        source_name="MIT Technology Review AI",
        source_url="https://www.technologyreview.com/topic/artificial-intelligence",
        rss_url="https://www.technologyreview.com/topic/artificial-intelligence/feed/",
        source_tier=2,
    ),
)

# Tier 3 — partner ecosystem
TIER_3_SOURCES: tuple[RssSourceSeed, ...] = (
    RssSourceSeed(
        source_id="acquia-blog",
        source_name="Acquia",
        source_url="https://www.acquia.com/blog",
        rss_url="https://www.acquia.com/blog/rss.xml",
        source_tier=3,
    ),
    RssSourceSeed(
        source_id="sas-blog",
        source_name="SAS",
        source_url="https://blogs.sas.com",
        rss_url="https://blogs.sas.com/content/feed/?x=1",
        source_tier=3,
    ),
    RssSourceSeed(
        source_id="hcl-news",
        source_name="HCL",
        source_url="https://www.hcl-software.com/blog",
        rss_url="https://www.hcl-software.com/blog/feed",
        source_tier=3,
    ),
    RssSourceSeed(
        source_id="unica-hcl-blog",
        source_name="Unica",
        source_url="https://www.hcl-software.com/unica",
        rss_url="https://www.salesforce.com/blog/category/marketing/feed/",
        source_tier=3,
    ),
    RssSourceSeed(
        source_id="acoustic-blog",
        source_name="Acoustic",
        source_url="https://acoustic.com/blog",
        rss_url="https://www.tealium.com/blog/feed/",
        source_tier=3,
    ),
)

PHASE_8_RSS_SOURCES: tuple[RssSourceSeed, ...] = (
    *TIER_1_SOURCES,
    *TIER_2_SOURCES,
    *TIER_3_SOURCES,
)
