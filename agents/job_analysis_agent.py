"""
Job Analysis Agent - Extracts structured information from job descriptions.
"""

import re
from typing import Dict, List, Set


class JobAnalysisAgent:
    """Analyzes job descriptions to extract structured requirements."""
    
    def analyze(self, job_desc: str) -> Dict:
        """
        Analyze job description and extract structured information.
        
        Returns:
            {
                'target_role': str,
                'seniority': str,
                'industry': str,
                'required_skills': List[str],
                'preferred_skills': List[str],
                'years_required': int,
                'leadership_requirements': List[str],
                'certifications': List[str],
                'tools': List[str]
            }
        """
        return {
            'target_role': self._extract_role(job_desc),
            'seniority': self._extract_seniority(job_desc),
            'industry': self._extract_industry(job_desc),
            'required_skills': self._extract_required_skills(job_desc),
            'preferred_skills': self._extract_preferred_skills(job_desc),
            'years_required': self._extract_years(job_desc),
            'leadership_requirements': self._extract_leadership(job_desc),
            'certifications': self._extract_certifications(job_desc),
            'tools': self._extract_tools(job_desc),
            '_raw_jd': job_desc  # Store for confidence calculation
        }
    
    def _extract_role(self, job_desc: str) -> str:
        """Extract target role/job title."""
        lines = job_desc.split('\n')
        
        # Pattern 1: Look for explicit role/title/position labels
        patterns = [
            r'(?:position|role|title|job title):\s*([A-Z][^\n]{5,80})',
            r'(?:As|as)\s+(?:a|an)?\s*([A-Z][^\n,]{10,80}),',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, job_desc, re.MULTILINE | re.IGNORECASE)
            if match:
                role = match.group(1).strip()
                if role.lower() not in ['about the role', 'the role', 'overview', 'job summary', 'job description']:
                    return role
        
        # Pattern 2: Look for role after 'Job Summary' or similar headers
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if line_lower in ['job summary', 'position summary', 'role summary']:
                # Next non-empty line is likely the role
                for j in range(i+1, min(i+5, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and len(next_line) > 5:
                        # Check if it looks like a role title (starts with capital, reasonable length)
                        if next_line[0].isupper() and 5 < len(next_line) < 100:
                            # Skip if it's a generic description starter
                            if not any(next_line.lower().startswith(word) for word in ['the main', 'this role', 'we are', 'the position']):
                                return next_line
                        # If it starts with "The main role of the X is...", extract X
                        role_match = re.search(r'(?:main role|role|position) of (?:the|a|an)\s+([A-Z][\w\s]{5,50})\s+is', next_line, re.IGNORECASE)
                        if role_match:
                            return role_match.group(1).strip()
        
        # Pattern 3: First substantial line (fallback)
        for line in lines[:10]:
            line = line.strip()
            if line and 10 < len(line) < 100 and line[0].isupper():
                if line.lower() not in ['job summary', 'job description', 'about the role', 'overview', 'the role']:
                    return line
        
        return "Not specified"
    
    def _extract_seniority(self, job_desc: str) -> str:
        """Extract seniority level."""
        job_lower = job_desc.lower()
        
        if any(term in job_lower for term in ['senior', 'sr.', 'lead', 'principal', 'staff']):
            return "Senior"
        elif any(term in job_lower for term in ['director', 'head of', 'vp', 'chief']):
            return "Director/Executive"
        elif any(term in job_lower for term in ['junior', 'jr.', 'entry', 'associate']):
            return "Junior"
        else:
            return "Mid-level"
    
    def _extract_industry(self, job_desc: str) -> str:
        """Extract industry/domain."""
        job_lower = job_desc.lower()
        
        industries = {
            'healthcare': ['healthcare', 'medical', 'pharma', 'clinical'],
            'finance': ['finance', 'banking', 'fintech', 'investment'],
            'technology': ['software', 'saas', 'tech', 'ai', 'ml'],
            'manufacturing': ['manufacturing', 'industrial', 'automotive'],
            'telecom': ['telecom', 'telecommunications', 'network']
        }
        
        for industry, keywords in industries.items():
            if any(kw in job_lower for kw in keywords):
                return industry.title()
        
        return "General"
    
    def _extract_required_skills(self, job_desc: str) -> List[str]:
        """Extract required/must-have skills from various JD formats."""
        required_skills = set()
        
        # Look for common requirement sections (expanded list)
        requirement_sections = [
            'required', 'must have', 'qualifications', 'requirements',
            'about you', 'you have', 'your background', 'what you bring',
            'ideal candidate', 'responsibilities', 'key focus'
        ]
        
        required_section = self._extract_section(job_desc, requirement_sections)
        
        if required_section:
            # Extract skills from required section
            skills = self._extract_skills_from_text(required_section)
            required_skills.update(skills)
        
        # If no section found, extract from entire JD
        if not required_skills:
            skills = self._extract_skills_from_text(job_desc)
            required_skills.update(skills)
        
        return sorted(list(required_skills))[:20]  # Increased limit
    
    def _extract_preferred_skills(self, job_desc: str) -> List[str]:
        """Extract preferred/nice-to-have skills."""
        preferred_skills = set()
        
        # Look for "preferred" section
        preferred_section = self._extract_section(job_desc, ['preferred', 'nice to have', 'bonus', 'plus'])
        
        if preferred_section:
            skills = self._extract_skills_from_text(preferred_section)
            preferred_skills.update(skills)
        
        return sorted(list(preferred_skills))[:10]
    
    def _extract_years(self, job_desc: str) -> int:
        """Extract years of experience required."""
        patterns = [
            r'minimum\s+of\s+(?:five|six|seven|eight|nine|ten)?\s*\(?(\d+)\)?\s*years?',  # 'minimum of five (5) years'
            r'at\s+least\s+(\d+)\s*years?',
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'(\d+)\s*to\s*\d+\s*years',
            r'(\d+)\+?\s*years',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, job_desc, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return 0
    
    def _extract_leadership(self, job_desc: str) -> List[str]:
        """Extract leadership requirements."""
        leadership_terms = []
        job_lower = job_desc.lower()
        
        leadership_keywords = [
            'lead teams', 'manage teams', 'cross-functional leadership',
            'stakeholder management', 'change management', 'team leadership',
            'mentoring', 'coaching', 'strategic planning'
        ]
        
        for keyword in leadership_keywords:
            if keyword in job_lower:
                leadership_terms.append(keyword.title())
        
        return leadership_terms
    
    def _extract_certifications(self, job_desc: str) -> List[str]:
        """Extract certification requirements."""
        certs = set()
        
        cert_patterns = [
            r'\b(PMP|CISSP|AWS|Azure|GCP|ITIL|Six Sigma|Scrum Master|CSM)\b',
            r'certification in ([A-Z][^\n]{5,30})',
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, job_desc, re.IGNORECASE)
            certs.update([m if isinstance(m, str) else m[0] for m in matches])
        
        return sorted(list(certs))
    
    def _extract_tools(self, job_desc: str) -> List[str]:
        """Extract tools and technologies."""
        tools = set()
        
        common_tools = [
            'Python', 'Java', 'JavaScript', 'SQL', 'AWS', 'Azure', 'GCP',
            'Docker', 'Kubernetes', 'Git', 'JIRA', 'Confluence',
            'LangChain', 'LangGraph', 'CrewAI', 'AutoGen',
            'DITA', 'XML', 'Markdown', 'Arbortext'
        ]
        
        job_lower = job_desc.lower()
        for tool in common_tools:
            if tool.lower() in job_lower:
                tools.add(tool)
        
        return sorted(list(tools))
    
    def _extract_section(self, text: str, keywords: List[str]) -> str:
        """Extract text section based on keywords."""
        text_lower = text.lower()
        
        for keyword in keywords:
            if keyword in text_lower:
                start_idx = text_lower.find(keyword)
                # Get next 500 characters or until next section
                end_idx = min(start_idx + 500, len(text))
                return text[start_idx:end_idx]
        
        return ""
    
    def _extract_skills_from_text(self, text: str) -> Set[str]:
        """Extract skills from a text block using word boundary matching."""
        import re
        skills = set()
        
        # Common skill patterns - expanded for communications, PR, marketing
        skill_keywords = [
            # Technical skills
            'python', 'java', 'ai', 'machine learning', 'ml', 'llm',
            'prompt engineering', 'rag', 'langchain', 'automation',
            
            # Writing & Documentation
            'technical writing', 'documentation', 'content development',
            'writing', 'editing', 'proofreading', 'copywriting',
            
            # Communications & PR
            'communications', 'strategic communications', 'corporate communications',
            'public relations', 'media relations', 'press releases',
            'executive communications', 'internal communications',
            
            # Marketing & Product
            'product marketing', 'product communications', 'product launches',
            'marketing', 'b2b marketing', 'saas marketing', 'enterprise marketing',
            'messaging', 'positioning', 'go-to-market',
            
            # Content & Storytelling
            'storytelling', 'customer storytelling', 'content strategy',
            'thought leadership', 'executive content', 'bylines',
            
            # Media & Industry
            'media engagement', 'media strategy', 'industry engagement',
            'analyst relations', 'influencer relations',
            
            # Management
            'agile', 'scrum', 'project management', 'stakeholder management',
            'cross-functional collaboration', 'team leadership'
        ]
        
        text_lower = text.lower()
        for skill in skill_keywords:
            # Use word boundary matching to avoid false matches
            # e.g., 'pr' won't match 'project' or 'proven'
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                skills.add(skill.title())
        
        return skills
