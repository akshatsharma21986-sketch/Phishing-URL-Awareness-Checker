"""
=============================================================================
Project Name  : Smart Lost & Found Campus Intelligence System
Module        : matcher.py
Description   : Intelligent multi-factor matching engine utilizing Natural
                Language Processing (NLP), token weighting, category compatibility,
                spatial location overlap, and temporal proximity decay.
=============================================================================
"""

import re
import math
from datetime import datetime
from typing import List, Dict, Set, Tuple, Optional
from models import Item, MatchResult


# Common English stop-words to filter out during text similarity computation
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "did", "do", "does", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers",
    "him", "his", "how", "i", "if", "in", "into", "is", "isn't", "it", "its", "itself",
    "let's", "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off",
    "on", "once", "only", "or", "other", "ought", "our", "ours", "out", "over", "own",
    "same", "she", "should", "so", "some", "such", "than", "that", "the", "their",
    "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "were", "weren't", "what", "when", "where", "which", "while", "who", "whom",
    "why", "with", "won't", "would", "you", "your", "yours", "yourself", "yourselves"
}

# High-value discriminative keyword vocabulary (colors, brands, materials, hardware)
DISTINCTIVE_KEYWORDS = {
    # Brands
    "apple", "samsung", "hp", "dell", "lenovo", "asus", "sony", "bose", "casio",
    "nike", "adidas", "titan", "fastrack", "boat", "logitech", "anker", "wildcraft",
    # Colors
    "black", "blue", "red", "green", "silver", "gold", "white", "grey", "gray",
    "yellow", "purple", "pink", "brown", "navy", "maroon", "transparent",
    # Device / Object Types
    "airpods", "earbuds", "headphones", "laptop", "phone", "iphone", "charger",
    "mouse", "keyboard", "calculator", "wallet", "purse", "backpack", "bottle",
    "flask", "keys", "id", "card", "spectacles", "glasses", "ring", "watch"
}


def tokenize(text: str) -> List[str]:
    """Tokenizes text into cleaned lowercase alphanumeric terms."""
    if not text:
        return []
    words = re.findall(r"\b[a-zA-Z0-9_]{2,}\b", text.lower())
    return [w for w in words if w not in STOP_WORDS]


def compute_text_similarity(item1: Item, item2: Item) -> Tuple[float, List[str]]:
    """
    Computes text similarity using weighted token intersection and Jaccard index.
    Gives extra weight to matching distinctive terms (brands, colors, object types).
    Returns (score_0_to_100, matching_keywords).
    """
    # Combine title (given 2x weight) and description
    tokens1_title = tokenize(item1.title) * 2
    tokens1_desc = tokenize(item1.description)
    tokens1 = set(tokens1_title + tokens1_desc)

    tokens2_title = tokenize(item2.title) * 2
    tokens2_desc = tokenize(item2.description)
    tokens2 = set(tokens2_title + tokens2_desc)

    if not tokens1 or not tokens2:
        return 0.0, []

    common_tokens = tokens1.intersection(tokens2)
    if not common_tokens:
        return 0.0, []

    # Calculate weighted intersection score
    total_weight = 0.0
    common_weight = 0.0
    all_tokens = tokens1.union(tokens2)

    for token in all_tokens:
        weight = 3.0 if token in DISTINCTIVE_KEYWORDS else 1.0
        total_weight += weight
        if token in common_tokens:
            common_weight += weight

    jaccard_weighted = (common_weight / total_weight) if total_weight > 0 else 0.0
    
    # Scale score with non-linear boost for strong token matches
    raw_score = jaccard_weighted * 100.0
    scaled_score = min(100.0, raw_score * 1.8)

    matching_keywords = sorted(list(common_tokens), key=lambda x: (x in DISTINCTIVE_KEYWORDS, len(x)), reverse=True)
    return round(scaled_score, 1), matching_keywords[:6]


def compute_category_similarity(cat1: str, cat2: str) -> float:
    """Returns 100 for exact match, partial for 'Other', 0 otherwise."""
    if cat1 == cat2:
        return 100.0
    if cat1 == "Other" or cat2 == "Other":
        return 35.0
    return 0.0


def compute_location_similarity(loc1: str, loc2: str) -> float:
    """
    Computes spatial similarity based on campus location token overlaps.
    E.g., 'Central Library 2nd Floor' vs 'Library Reading Room'.
    """
    tokens1 = set(tokenize(loc1))
    tokens2 = set(tokenize(loc2))
    if not tokens1 or not tokens2:
        return 20.0  # Neutral baseline if location missing

    intersection = tokens1.intersection(tokens2)
    if not intersection:
        return 0.0

    overlap_ratio = len(intersection) / min(len(tokens1), len(tokens2))
    return min(100.0, overlap_ratio * 100.0)


def compute_date_proximity(date_lost_str: str, date_found_str: str) -> float:
    """
    Calculates temporal proximity score.
    Items found within 0 to 7 days of being lost receive full 100% score.
    Older gaps decay gradually. Found before lost by > 2 days is penalized.
    """
    try:
        d_lost = datetime.strptime(date_lost_str, "%Y-%m-%d")
        d_found = datetime.strptime(date_found_str, "%Y-%m-%d")
        diff_days = (d_found - d_lost).days

        if 0 <= diff_days <= 5:
            return 100.0
        elif 6 <= diff_days <= 14:
            return 85.0
        elif 15 <= diff_days <= 30:
            return 60.0
        elif diff_days > 30:
            return max(15.0, 60.0 - (diff_days - 30) * 0.8)
        else:
            # Found date is before lost date (small leeway for reporting errors)
            if diff_days >= -2:
                return 70.0
            return 20.0
    except Exception:
        return 50.0  # Default fallback if dates unparseable


def calculate_match(lost_item: Item, found_item: Item) -> MatchResult:
    """
    Evaluates the comprehensive multi-factor similarity between a Lost and a Found item.
    Weights:
      - Text / Description (40%)
      - Category Compatibility (25%)
      - Location Proximity (20%)
      - Date Proximity (15%)
    """
    text_score, keywords = compute_text_similarity(lost_item, found_item)
    category_score = compute_category_similarity(lost_item.category, found_item.category)
    location_score = compute_location_similarity(lost_item.location, found_item.location)
    date_score = compute_date_proximity(lost_item.date_event, found_item.date_event)

    # Weighted overall confidence formula
    overall = (
        (0.40 * text_score) +
        (0.25 * category_score) +
        (0.20 * location_score) +
        (0.15 * date_score)
    )

    # Hard filter: if categories completely mismatch, penalize heavily
    if category_score == 0.0:
        overall = overall * 0.40

    return MatchResult(
        lost_item=lost_item,
        found_item=found_item,
        confidence_score=round(min(100.0, max(0.0, overall)), 1),
        text_score=round(text_score, 1),
        category_score=round(category_score, 1),
        location_score=round(location_score, 1),
        date_score=round(date_score, 1),
        matching_keywords=keywords
    )


def find_all_matches(
    lost_items: List[Item],
    found_items: List[Item],
    min_confidence: float = 35.0
) -> List[MatchResult]:
    """
    Scans all active Lost items against active Found items,
    returning candidate matches sorted by highest confidence score.
    """
    results: List[MatchResult] = []
    for lost in lost_items:
        for found in found_items:
            match = calculate_match(lost, found)
            if match.confidence_score >= min_confidence:
                results.append(match)

    results.sort(key=lambda m: m.confidence_score, reverse=True)
    return results
