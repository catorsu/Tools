import json
from typing import List, Dict, Any, Optional


class RedditReducer:
    """
    Processes raw Reddit JSON data to produce a simplified, structured version.
    """

    def process_json_string(self, json_string: str) -> Dict[str, Any]:
        """
        Parses a raw JSON string from Reddit and returns a simplified dictionary.

        Args:
            json_string: The raw JSON string from a Reddit thread URL.

        Returns:
            A dictionary with 'post' and 'comments' keys.

        Raises:
            ValueError: If the JSON is invalid or has an unexpected structure.
        """
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

        if not isinstance(data, list) or len(data) < 2:
            raise ValueError(
                "Invalid Reddit JSON structure. Expected a list with at least two elements."
            )

        # 1. Extract Post
        post_data = data[0].get("data", {}).get("children", [{}])[0].get("data", {})
        simplified_post = {
            "title": post_data.get("title", "N/A"),
            "text": post_data.get("selftext", ""),
            "url": post_data.get("url", "N/A"),  # Added the URL field
        }

        # 2. Extract and Process Comments
        comments_data = data[1].get("data", {}).get("children", [])
        simplified_comments = []
        for comment_node in comments_data:
            processed_comment = self._process_comment_node(comment_node)
            if processed_comment:
                simplified_comments.append(processed_comment)

        # 3. Assemble final structure
        return {"post": simplified_post, "comments": simplified_comments}

    def _process_comment_node(self, node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Recursively processes a single comment node, applying filters and
        simplifying its structure.

        Args:
            node: A comment node from the raw Reddit JSON.

        Returns:
            A simplified comment dictionary if it passes filters, otherwise None.
        """
        # Ignore non-comment nodes (like 'more' links)
        if node.get("kind") != "t1":
            return None

        data = node.get("data", {})

        # Filter based on score and body content
        score = data.get("score")
        body = data.get("body")

        if score is None or score < 1:
            return None
        if body in ["[deleted]", "[removed]"] or not body:
            return None

        # Process replies recursively
        replies_data = data.get("replies", {})
        simplified_replies = []
        if (
            isinstance(replies_data, dict)
            and "data" in replies_data
            and "children" in replies_data["data"]
        ):
            for reply_node in replies_data["data"]["children"]:
                processed_reply = self._process_comment_node(reply_node)
                if processed_reply:
                    simplified_replies.append(processed_reply)

        # Build the simplified comment dictionary
        simplified_comment = {
            "author": data.get("author", "N/A"),
            "score": score,
            "body": body,
            "replies": simplified_replies,
        }

        return simplified_comment
