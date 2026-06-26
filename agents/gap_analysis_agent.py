"""
Gap Analysis Agent - Identifies skill gaps and matches between resume and job.
"""

from typing import Dict, List, Set


class GapAnalysisAgent:
    """Analyzes gaps between resume and job requirements."""
    
    def analyze(self, resume_text: str, job_analysis: Dict) -> Dict:
        """
        Analyze gaps between resume and job requirements.
        
        Returns:
            {
                'strong_match': List[str],
                'partial_match': List[str],
                'transferable_skills': List[str],
                'missing_skills': List[str],
                'match_percentage': int
            }
        """
        resume_lower = resume_text.lower()
        
        required_skills = job_analysis.get('required_skills', [])
        preferred_skills = job_analysis.get('preferred_skills', [])
        tools = job_analysis.get('tools', [])
        
        all_job_requirements = set(required_skills + preferred_skills + tools)
        
        strong_match = []
        partial_match = []
        transferable_skills = []
        missing_skills = []
        
        # Analyze each requirement
        for skill in all_job_requirements:
            match_type = self._analyze_skill_match(skill, resume_lower)
            
            if match_type == 'strong':
                strong_match.append(skill)
            elif match_type == 'partial':
                partial_match.append(skill)
            elif match_type == 'transferable':
                transferable_skills.append(skill)
            else:
                missing_skills.append(skill)
        
        # Calculate match percentage
        total_requirements = len(all_job_requirements)
        matched = len(strong_match) + (len(partial_match) * 0.5) + (len(transferable_skills) * 0.3)
        match_percentage = int((matched / total_requirements * 100)) if total_requirements > 0 else 0
        
        # Generate skill match explanation
        explanation = self._generate_skill_explanation(
            strong_match, partial_match, transferable_skills, missing_skills
        )
        
        return {
            'strong_match': strong_match,
            'partial_match': partial_match,
            'transferable_skills': transferable_skills,
            'missing_skills': missing_skills,
            'match_percentage': match_percentage,
            'skill_explanation': explanation
        }
    
    def _analyze_skill_match(self, skill: str, resume_text: str) -> str:
        """
        Analyze how well a skill matches the resume.
        
        Returns: 'strong', 'partial', 'transferable', or 'missing'
        """
        import re
        skill_lower = skill.lower()
        
        # Strong match - exact or very close match with word boundaries
        # Prevents 'pr' from matching 'project' or 'proven'
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, resume_text):
            return 'strong'
        
        # CRITICAL: Check for IMPLIED skills
        # Communications is IMPLIED by documentation/editing/writing work
        if skill_lower in ['communication', 'communications', 'communication skills']:
            if any(term in resume_text for term in ['documentation', 'editing', 'writing', 'content development', 'technical writer', 'content writer']):
                return 'strong'  # Treat as strong match since it's clearly implied
        
        # Editing is IMPLIED by documentation/content work
        if skill_lower in ['editing', 'edit', 'editorial']:
            if any(term in resume_text for term in ['documentation', 'content development', 'technical writer', 'content writer', 'reviewed', 'validated']):
                return 'strong'  # Treat as strong match since it's clearly implied
        
        # Writing is IMPLIED by documentation/content work
        if skill_lower in ['writing', 'write', 'written']:
            if any(term in resume_text for term in ['documentation', 'content development', 'technical writer', 'content writer', 'authored', 'created']):
                return 'strong'  # Treat as strong match since it's clearly implied
        
        # Project Management is IMPLIED by team leadership/coordination
        if skill_lower in ['project management', 'project coordination']:
            if any(term in resume_text for term in ['managed team', 'led team', 'coordinated', 'managed projects', 'project lead']):
                return 'strong'  # Treat as strong match since it's clearly implied
        
        # Check for related/similar skills
        related_skills = self._get_related_skills(skill_lower)
        for related in related_skills:
            if related in resume_text:
                return 'partial'
        
        # Check for transferable skills
        transferable = self._get_transferable_skills(skill_lower)
        for trans in transferable:
            if trans in resume_text:
                return 'transferable'
        
        return 'missing'
    
    def _get_related_skills(self, skill: str) -> List[str]:
        """Get related/similar skills."""
        related_map = {
            'python': ['scripting', 'automation', 'programming'],
            'ai': ['artificial intelligence', 'machine learning', 'ml'],
            'llm': ['large language model', 'gpt', 'generative ai'],
            'prompt engineering': ['prompt design', 'prompt optimization'],
            'langchain': ['langraph', 'llm framework'],
            'crewai': ['autogen', 'agentic framework', 'multi-agent'],
            'technical writing': ['documentation', 'content development'],
            'agile': ['scrum', 'sprint', 'iterative development'],
            'leadership': ['team management', 'people management', 'mentoring'],
            'project management': ['program management', 'delivery management'],
            'communications': ['communication', 'stakeholder engagement', 'collaboration'],
            'communication': ['communications', 'written communication', 'verbal communication']
        }
        
        return related_map.get(skill, [])
    
    def _get_transferable_skills(self, skill: str) -> List[str]:
        """Get transferable skills that could apply."""
        transferable_map = {
            'langchain': ['python', 'ai', 'automation'],
            'crewai': ['python', 'ai', 'workflow automation'],
            'prompt engineering': ['technical writing', 'ai', 'content development'],
            'rag': ['information retrieval', 'search', 'knowledge management'],
            'aws': ['cloud', 'azure', 'gcp'],
            'docker': ['containerization', 'kubernetes', 'devops'],
            'medical writing': ['technical writing', 'documentation', 'regulatory']
        }
        
        return transferable_map.get(skill, [])
    
    def _generate_skill_explanation(self, strong: List[str], partial: List[str], 
                                   transferable: List[str], missing: List[str]) -> str:
        """Generate detailed explanation of skill matches."""
        
        explanation_parts = []
        
        # Strong matches
        if strong:
            explanation_parts.append("✓ Strong Matches:")
            for skill in strong[:5]:
                explanation_parts.append(f"  • {skill} (direct match)")
        
        # Partial matches
        if partial:
            explanation_parts.append("\n◐ Partial Matches:")
            for skill in partial[:5]:
                related = self._get_related_skills(skill.lower())
                if related:
                    explanation_parts.append(f"  • {skill} → {related[0]} (related)")
                else:
                    explanation_parts.append(f"  • {skill} (partial)")
        
        # Transferable skills
        if transferable:
            explanation_parts.append("\n⟳ Transferable Skills:")
            for skill in transferable[:5]:
                trans = self._get_transferable_skills(skill.lower())
                if trans:
                    explanation_parts.append(f"  • {skill} ← {trans[0]} (transferable)")
                else:
                    explanation_parts.append(f"  • {skill} (transferable)")
        
        # Missing skills (filtered)
        if missing:
            irrelevant = ['python', 'java', 'javascript', 'ci/cd', 'docker', 'kubernetes']
            relevant_missing = [s for s in missing if not any(tech in s.lower() for tech in irrelevant)]
            
            if relevant_missing:
                explanation_parts.append("\n✗ Missing Skills:")
                for skill in relevant_missing[:5]:
                    explanation_parts.append(f"  • {skill}")
        
        if explanation_parts:
            return "\n".join(explanation_parts)
        else:
            # ALWAYS provide reasoning, even if empty
            return """No skill matches detected.

Possible reasons:
  • Job requirements could not be automatically extracted
    (The system looks for sections like 'Requirements', 'About You', 'Qualifications')
  • Resume skills not detected in text
  • Significant domain mismatch between resume and job
  • Job description uses non-standard format

Note: Even with a detailed job description, automatic extraction may fail
if the format doesn't match expected patterns. This doesn't mean your JD
is incomplete - it means the parser needs improvement."""
