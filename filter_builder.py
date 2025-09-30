#!/usr/bin/env python3
"""Build Turbopuffer filters from query criteria."""

from typing import Dict, List, Any, Optional
import re


class FilterBuilder:
    """Build Turbopuffer filters from structured query criteria."""

    @staticmethod
    def parse_experience_years(years_str: str) -> Optional[str]:
        """
        Parse experience years like '3+', '5+' into bucket format.

        Args:
            years_str: String like '3+', '5+ years', etc.

        Returns:
            Bucket string like '3', '5', '10', or None
        """
        match = re.search(r'(\d+)\+?', years_str)
        if match:
            years = int(match.group(1))
            # Map to available buckets: "1", "3", "5", "10"
            if years >= 10:
                return "10"
            elif years >= 5:
                return "5"
            elif years >= 3:
                return "3"
            else:
                return "1"
        return None

    @staticmethod
    def build_degree_filter(degrees: List[str]) -> Dict[str, Any]:
        """
        Build filter for degree requirements.

        Args:
            degrees: List of degree types (e.g., ["jd", "master's"])

        Returns:
            Turbopuffer filter dict
        """
        # Normalize degree names to match schema
        normalized = []
        for deg in degrees:
            deg_lower = deg.lower().strip()
            if deg_lower in ["jd", "j.d.", "juris doctor"]:
                normalized.append("jd")
            elif deg_lower in ["master's", "masters", "master", "ms", "ma"]:
                normalized.append("master's")
            elif deg_lower in ["bachelor's", "bachelors", "bachelor", "bs", "ba"]:
                normalized.append("bachelor's")
            elif deg_lower in ["mba"]:
                normalized.append("mba")
            elif deg_lower in ["doctorate", "phd", "ph.d."]:
                normalized.append("doctorate")
            else:
                normalized.append(deg_lower)

        if len(normalized) == 1:
            return {"deg_degrees": ["Contains", normalized[0]]}
        else:
            # Multiple degrees - need OR logic
            return {"deg_degrees": ["In", normalized]}

    @staticmethod
    def build_field_of_study_filter(fields: List[str]) -> Dict[str, Any]:
        """
        Build filter for field of study.

        Args:
            fields: List of fields (e.g., ["law", "computer science"])

        Returns:
            Turbopuffer filter dict
        """
        if len(fields) == 1:
            return {"deg_fos": ["Contains", fields[0].lower()]}
        else:
            return {"deg_fos": ["In", [f.lower() for f in fields]]}

    @staticmethod
    def build_title_filter(titles: List[str]) -> Dict[str, Any]:
        """
        Build filter for job titles.

        Args:
            titles: List of job titles

        Returns:
            Turbopuffer filter dict
        """
        if len(titles) == 1:
            return {"exp_titles": ["Contains", titles[0].lower()]}
        else:
            return {"exp_titles": ["In", [t.lower() for t in titles]]}

    @staticmethod
    def build_company_filter(companies: List[str]) -> Dict[str, Any]:
        """
        Build filter for companies.

        Args:
            companies: List of company names

        Returns:
            Turbopuffer filter dict
        """
        if len(companies) == 1:
            return {"exp_companies": ["Contains", companies[0].lower()]}
        else:
            return {"exp_companies": ["In", [c.lower() for c in companies]]}

    @staticmethod
    def build_years_filter(min_years: str, field_type: str = "exp") -> Dict[str, Any]:
        """
        Build filter for years of experience or education.

        Args:
            min_years: Minimum years (e.g., "3+")
            field_type: "exp" for experience or "deg" for education

        Returns:
            Turbopuffer filter dict
        """
        bucket = FilterBuilder.parse_experience_years(min_years)
        if bucket:
            field_name = f"{field_type}_years"
            # Filter for bucket >= required bucket
            valid_buckets = []
            if bucket in ["1", "3", "5", "10"]:
                bucket_int = int(bucket)
                for b in ["1", "3", "5", "10"]:
                    if int(b) >= bucket_int:
                        valid_buckets.append(b)

            return {field_name: ["In", valid_buckets]}
        return {}

    @staticmethod
    def build_filters_from_criteria(hard_criteria: List[str]) -> Dict[str, Any]:
        """
        Build Turbopuffer filters from hard criteria list.

        Args:
            hard_criteria: List of hard criteria strings

        Returns:
            Combined filter dict
        """
        filters = []

        for criterion in hard_criteria:
            criterion_lower = criterion.lower()

            # Detect degree requirements
            if "jd" in criterion_lower or "juris doctor" in criterion_lower:
                filters.append(FilterBuilder.build_degree_filter(["jd"]))

            # Detect experience years
            if "year" in criterion_lower and ("experience" in criterion_lower or "practice" in criterion_lower):
                match = re.search(r'(\d+)\+?\s*years?', criterion_lower)
                if match:
                    filters.append(FilterBuilder.build_years_filter(f"{match.group(1)}+", "exp"))

            # Detect field of study
            if "law school" in criterion_lower or "field" in criterion_lower:
                # This is tricky - might need manual specification
                pass

        # Combine filters with AND logic
        if len(filters) == 0:
            return {}
        elif len(filters) == 1:
            return filters[0]
        else:
            return {"And": filters}


def test_filter_builder():
    """Test the filter builder."""
    print("Testing FilterBuilder...")

    # Test 1: Parse experience years
    print("\n1. Parse experience years:")
    print(f"  '3+ years' -> {FilterBuilder.parse_experience_years('3+ years')}")
    print(f"  '5+' -> {FilterBuilder.parse_experience_years('5+')}")
    print(f"  '10 years' -> {FilterBuilder.parse_experience_years('10 years')}")

    # Test 2: Build degree filter
    print("\n2. Build degree filter:")
    print(f"  JD: {FilterBuilder.build_degree_filter(['jd'])}")

    # Test 3: Build years filter
    print("\n3. Build years filter:")
    print(f"  3+ years exp: {FilterBuilder.build_years_filter('3+', 'exp')}")

    # Test 4: Build from tax lawyer criteria
    print("\n4. Tax lawyer hard criteria:")
    criteria = [
        "JD degree from an accredited U.S. law school",
        "3+ years of legal practice experience"
    ]
    filters = FilterBuilder.build_filters_from_criteria(criteria)
    print(f"  {filters}")


if __name__ == "__main__":
    test_filter_builder()
