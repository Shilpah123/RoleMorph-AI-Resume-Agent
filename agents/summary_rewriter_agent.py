"""
Summary Rewriter Agent - Always generates a new, tailored professional summary.
Now with quality scoring and transferable skills mapping.
"""

from typing import Dict, List


class SummaryRewriterAgent:
    """Rewrites professional summary to align with target role."""
    
    def rewrite(self, 
                years_experience: int,
                current_background: str,
                job_analysis: Dict,
                gap_analysis: Dict,
                achievements: List[str] = None,
                original_summary: str = None,
                resume_text: str = None) -> str:
        """
        Generate a completely new professional summary.
        
        Args:
            years_experience: Years of experience from resume
            current_background: Current role/background extracted from resume
            job_analysis: Output from JobAnalysisAgent
            gap_analysis: Output from GapAnalysisAgent
            achievements: List of key achievements (optional)
        
        Returns:
            New professional summary (max 120 words)
        """
        target_role = job_analysis.get('target_role', 'professional')
        seniority = job_analysis.get('seniority', 'experienced')
        required_skills = job_analysis.get('required_skills', [])
        strong_match = gap_analysis.get('strong_match', [])
        
        # Build summary components
        parts = []
        
        # Opening statement - role-focused
        opening = self._create_opening(
            years_experience, 
            current_background, 
            target_role, 
            seniority
        )
        parts.append(opening)
        
        # Core competencies - focus on matched skills
        if strong_match:
            competencies = self._create_competencies(strong_match, required_skills)
            parts.append(competencies)
        
        # Value proposition - what you bring
        value_prop = self._create_value_proposition(
            job_analysis, 
            gap_analysis
        )
        parts.append(value_prop)
        
        # Combine and limit to 120 words
        summary = " ".join(parts)
        words = summary.split()
        if len(words) > 120:
            summary = " ".join(words[:120]) + "."
        
        return summary
    
    def _create_opening(self, years: int, background: str, target_role: str, seniority: str) -> str:
        """Create opening statement aligned with target role."""
        
        # Extract key terms from target role
        role_lower = target_role.lower()
        
        # AI/Tech roles
        if any(term in role_lower for term in ['ai', 'ml', 'data science', 'automation']):
            return f"AI-focused {background} with {years}+ years of experience driving digital transformation, automation initiatives, and AI adoption across enterprise organizations."
        
        # Leadership roles
        elif any(term in role_lower for term in ['director', 'head', 'lead', 'manager']):
            return f"{seniority}-level {background} with {years}+ years leading cross-functional teams, driving strategic initiatives, and delivering measurable business impact."
        
        # Technical Writing/Content roles
        elif any(term in role_lower for term in ['writer', 'content', 'documentation', 'communication']):
            return f"Strategic {background} with {years}+ years creating high-impact content, documentation, and communication materials for global organizations."
        
        # Engineering/Technical roles
        elif any(term in role_lower for term in ['engineer', 'developer', 'architect']):
            return f"Results-driven {background} with {years}+ years designing and implementing scalable solutions, driving technical excellence, and delivering innovative products."
        
        # Generic fallback
        else:
            return f"Experienced {background} with {years}+ years delivering results in dynamic, fast-paced environments."
    
    def _create_competencies(self, strong_match: List[str], required_skills: List[str]) -> str:
        """Create competencies statement focusing on matched skills."""
        
        # Prioritize required skills that are matched
        priority_skills = [s for s in strong_match if s in required_skills]
        other_skills = [s for s in strong_match if s not in required_skills]
        
        # Take top 6 skills (4 priority + 2 other)
        top_skills = (priority_skills[:4] + other_skills[:2])[:6]
        
        if len(top_skills) <= 3:
            return f"Expertise in {', '.join(top_skills)}."
        else:
            return f"Core competencies include {', '.join(top_skills[:3])}, and {', '.join(top_skills[3:])}."
    
    def _create_value_proposition(self, job_analysis: Dict, gap_analysis: Dict) -> str:
        """Create value proposition statement."""
        
        leadership_req = job_analysis.get('leadership_requirements', [])
        match_pct = gap_analysis.get('match_percentage', 0)
        
        # High match - emphasize proven track record
        if match_pct >= 80:
            if leadership_req:
                return "Proven track record of leading cross-functional teams, driving organizational change, and delivering strategic initiatives that improve operational efficiency and business outcomes."
            else:
                return "Proven ability to deliver high-quality results, collaborate effectively with stakeholders, and drive continuous improvement in fast-paced environments."
        
        # Moderate match - emphasize transferable skills
        elif match_pct >= 60:
            return "Strong foundation in technical execution combined with excellent communication skills, adaptability, and a track record of quickly mastering new technologies and methodologies."
        
        # Lower match - emphasize learning and adaptability
        else:
            return "Quick learner with strong analytical skills, proven ability to adapt to new domains, and a track record of delivering results through collaboration and continuous improvement."
