"""
Summary Quality Scorer - Evaluates summary quality to preserve strong original content.
"""

import re
from typing import Dict


class SummaryQualityScorer:
    """Scores summary quality to determine if original should be preserved."""
    
    def score_summary(self, summary: str, job_desc: str = None) -> Dict:
        """
        Score summary quality on multiple dimensions.
        
        Returns:
            {
                'overall_score': int (0-100),
                'specificity': int,
                'achievements': int,
                'measurable_impact': int,
                'seniority_indicators': int,
                'keyword_relevance': int
            }
        """
        specificity = self._score_specificity(summary)
        achievements = self._score_achievements(summary)
        measurable_impact = self._score_measurable_impact(summary)
        seniority = self._score_seniority_indicators(summary)
        keyword_relevance = self._score_keyword_relevance(summary, job_desc) if job_desc else 50
        
        # Weighted overall score
        overall = int(
            (specificity * 0.25) +
            (achievements * 0.20) +
            (measurable_impact * 0.20) +
            (seniority * 0.15) +
            (keyword_relevance * 0.20)
        )
        
        return {
            'overall_score': overall,
            'specificity': specificity,
            'achievements': achievements,
            'measurable_impact': measurable_impact,
            'seniority_indicators': seniority,
            'keyword_relevance': keyword_relevance
        }
    
    def _score_specificity(self, summary: str) -> int:
        """Score how specific vs generic the summary is."""
        summary_lower = summary.lower()
        
        # Generic phrases reduce score
        generic_phrases = [
            'experienced professional',
            'delivering results',
            'dynamic environment',
            'fast-paced environment',
            'team player',
            'hard worker',
            'detail-oriented'
        ]
        
        generic_count = sum(1 for phrase in generic_phrases if phrase in summary_lower)
        
        # Specific indicators increase score
        specific_indicators = [
            r'\d+\+?\s*years',  # Years of experience
            r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Professional|Specialist|Expert|Leader)',  # Specific titles
            r'(?:AI|ML|DITA|XML|Python|automation|transformation)',  # Specific technologies
        ]
        
        specific_count = sum(1 for pattern in specific_indicators if re.search(pattern, summary))
        
        # Calculate score
        base_score = 50
        base_score += (specific_count * 15)  # +15 per specific indicator
        base_score -= (generic_count * 20)   # -20 per generic phrase
        
        return max(0, min(100, base_score))
    
    def _score_achievements(self, summary: str) -> int:
        """Score presence of achievements and accomplishments."""
        summary_lower = summary.lower()
        
        achievement_indicators = [
            'led', 'drove', 'delivered', 'achieved', 'established',
            'spearheaded', 'launched', 'implemented', 'transformed',
            'recognized', 'awarded', 'proven track record', 'proven success'
        ]
        
        count = sum(1 for indicator in achievement_indicators if indicator in summary_lower)
        
        # Score based on count
        if count >= 4:
            return 100
        elif count >= 3:
            return 80
        elif count >= 2:
            return 60
        elif count >= 1:
            return 40
        else:
            return 20
    
    def _score_measurable_impact(self, summary: str) -> int:
        """Score presence of measurable/quantifiable impact."""
        
        # Look for numbers, percentages, scale indicators
        measurable_patterns = [
            r'\d+\+?\s*years',
            r'\d+%',
            r'\$\d+',
            r'enterprise[- ]scale',
            r'global',
            r'cross[- ]functional',
            r'large[- ]scale',
            r'multi[- ]million'
        ]
        
        count = sum(1 for pattern in measurable_patterns if re.search(pattern, summary, re.IGNORECASE))
        
        if count >= 3:
            return 100
        elif count >= 2:
            return 75
        elif count >= 1:
            return 50
        else:
            return 25
    
    def _score_seniority_indicators(self, summary: str) -> int:
        """Score seniority level indicators."""
        summary_lower = summary.lower()
        
        # Senior indicators
        senior_indicators = [
            'senior', 'lead', 'principal', 'director', 'head of',
            'strategic', 'executive', 'vp', 'chief'
        ]
        
        # Mid indicators
        mid_indicators = [
            'professional', 'specialist', 'expert', 'consultant'
        ]
        
        # Junior indicators (negative)
        junior_indicators = [
            'junior', 'entry', 'associate', 'assistant'
        ]
        
        senior_count = sum(1 for indicator in senior_indicators if indicator in summary_lower)
        mid_count = sum(1 for indicator in mid_indicators if indicator in summary_lower)
        junior_count = sum(1 for indicator in junior_indicators if indicator in summary_lower)
        
        if senior_count >= 2:
            return 100
        elif senior_count >= 1:
            return 80
        elif mid_count >= 1:
            return 60
        elif junior_count >= 1:
            return 30
        else:
            return 50
    
    def _score_keyword_relevance(self, summary: str, job_desc: str) -> int:
        """Score keyword relevance to job description."""
        if not job_desc:
            return 50
        
        summary_lower = summary.lower()
        job_lower = job_desc.lower()
        
        # Extract key terms from job description (simple approach)
        job_words = set(re.findall(r'\b\w{4,}\b', job_lower))
        summary_words = set(re.findall(r'\b\w{4,}\b', summary_lower))
        
        # Common words to ignore
        stop_words = {'with', 'have', 'this', 'that', 'from', 'will', 'your', 'been',
                     'were', 'their', 'what', 'which', 'when', 'where', 'about'}
        
        job_words -= stop_words
        summary_words -= stop_words
        
        # Calculate overlap
        if not job_words:
            return 50
        
        overlap = len(job_words & summary_words)
        overlap_ratio = overlap / min(len(job_words), 20)  # Cap at 20 key terms
        
        return int(overlap_ratio * 100)
    
    def should_preserve_original(self, original_summary: str, new_summary: str, 
                                job_desc: str = None, threshold: int = 10) -> bool:
        """
        Determine if original summary should be preserved.
        
        Args:
            original_summary: Original summary text
            new_summary: AI-generated summary
            job_desc: Job description (optional)
            threshold: Score difference threshold (default 10)
        
        Returns:
            True if original should be preserved, False otherwise
        """
        original_score = self.score_summary(original_summary, job_desc)
        new_score = self.score_summary(new_summary, job_desc)
        
        # Preserve original if it scores significantly better
        return original_score['overall_score'] > (new_score['overall_score'] + threshold)
