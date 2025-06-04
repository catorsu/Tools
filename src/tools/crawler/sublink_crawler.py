"""
Sublink Crawler - Core crawling functionality
"""

import requests
from bs4 import BeautifulSoup
import time
import threading
from urllib.parse import urljoin, urlparse
from ...utils.url_utils import (
    normalize_url,
    is_valid_url,
    resolve_relative_url,
    url_matches_prefix,
    clean_url_for_display,
)


class SublinkCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.crawled_urls = set()
        self.found_links = set()
        self.is_running = False
        self.is_paused = False
        self.progress_callback = None
        self.error_callback = None

    def set_user_agent(self, user_agent):
        """Set custom user agent"""
        self.session.headers.update({"User-Agent": user_agent})

    def set_progress_callback(self, callback):
        """Set callback function for progress updates"""
        self.progress_callback = callback

    def set_error_callback(self, callback):
        """Set callback function for error messages"""
        self.error_callback = callback

    def _log_progress(self, message):
        """Send progress update to callback"""
        if self.progress_callback:
            self.progress_callback(message)

    def _log_error(self, message):
        """Send error message to callback"""
        if self.error_callback:
            self.error_callback(message)

    def _get_links_from_page(self, url):
        """Extract all links from a single page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            links = set()

            # Find all <a> tags with href attributes
            for link_tag in soup.find_all("a", href=True):
                href = link_tag["href"].strip()
                if href:
                    # Resolve relative URLs
                    absolute_url = resolve_relative_url(url, href)
                    normalized_url = normalize_url(absolute_url)
                    if is_valid_url(normalized_url):
                        links.add(normalized_url)

            return links

        except requests.RequestException as e:
            self._log_error(f"Error fetching {url}: {str(e)}")
            return set()
        except Exception as e:
            self._log_error(f"Error parsing {url}: {str(e)}")
            return set()

    def crawl(
        self,
        start_url,
        url_prefix=None,
        max_depth=2,
        max_pages=100,
        request_delay=1.0,
        user_agent=None,
    ):
        """
        Main crawling function

        Args:
            start_url: Starting URL for crawling
            url_prefix: Prefix pattern for filtering links (defaults to start_url path)
            max_depth: Maximum crawl depth
            max_pages: Maximum number of pages to crawl
            request_delay: Delay between requests in seconds
            user_agent: Custom user agent string
        """
        self.is_running = True
        self.crawled_urls.clear()
        self.found_links.clear()

        # Set user agent if provided
        if user_agent:
            self.set_user_agent(user_agent)
        else:
            self.set_user_agent(
                "Crawler Toolbox/1.0 (+https://github.com/crawler-toolbox)"
            )

        # Use start_url as prefix if none provided
        if url_prefix is None:
            url_prefix = start_url

        # Normalize start URL
        start_url = normalize_url(start_url)

        if not is_valid_url(start_url):
            self._log_error("Invalid start URL provided")
            self.is_running = False
            return []

        self._log_progress(f"Starting crawl from: {start_url}")
        self._log_progress(f"URL prefix filter: {url_prefix}")

        # Initialize crawling queue with (url, depth) tuples
        crawl_queue = [(start_url, 0)]
        pages_crawled = 0

        while crawl_queue and self.is_running and pages_crawled < max_pages:
            # Handle pause
            while self.is_paused and self.is_running:
                time.sleep(0.1)

            if not self.is_running:
                break

            current_url, current_depth = crawl_queue.pop(0)

            # Skip if already crawled
            if current_url in self.crawled_urls:
                continue

            # Skip if depth exceeded
            if current_depth > max_depth:
                continue

            self.crawled_urls.add(current_url)
            pages_crawled += 1

            self._log_progress(
                f"Crawling [{pages_crawled}/{max_pages}] depth {current_depth}: {current_url[:60]}..."
            )

            # Get links from current page
            page_links = self._get_links_from_page(current_url)

            # Process found links
            for link in page_links:
                if url_matches_prefix(link, url_prefix):
                    self.found_links.add(link)

                    # Add to crawl queue if within depth limit
                    if current_depth < max_depth and link not in self.crawled_urls:
                        crawl_queue.append((link, current_depth + 1))

            # Respectful delay between requests
            if request_delay > 0 and self.is_running:
                time.sleep(request_delay)

        if self.is_running:
            self._log_progress(
                f"Crawl completed. Found {len(self.found_links)} unique links."
            )
        else:
            self._log_progress("Crawl stopped by user.")

        self.is_running = False
        return sorted(list(self.found_links))

    def stop_crawl(self):
        """Stop the crawling process"""
        self.is_running = False
        self._log_progress("Stopping crawl...")

    def pause_crawl(self):
        """Pause the crawling process"""
        self.is_paused = True
        self._log_progress("Crawl paused...")

    def resume_crawl(self):
        """Resume the crawling process"""
        self.is_paused = False
        self._log_progress("Crawl resumed...")

    def export_links_to_file(self, links, filename):
        """Export found links to a text file in the new bracket format"""
        try:
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# Sublinks found by Crawler Toolbox\n")
                f.write(f"# Generated on: {timestamp}\n")
                f.write(f"# Total links: {len(links)}\n\n")

                # Write links in bracket format
                for link in links:
                    f.write(f"[{link}]\n")

                # Add summary if there are many links
                if len(links) > 3:
                    f.write(f"\n(Total: {len(links)} links)")

            return True
        except Exception as e:
            self._log_error(f"Error exporting to file: {str(e)}")
            return False