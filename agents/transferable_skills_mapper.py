"""
Transferable Skills Mapper - Maps skills across domains intelligently.
"""

from typing import Dict, List, Set


class TransferableSkillsMapper:
    """Maps transferable skills when there's a domain mismatch."""
    
    def __init__(self):
        # Define transferable skill mappings
        self.skill_mappings = {
            # Technical Writing transferable to Medical Writing
            'technical_writing': {
                'medical_writing': [
                    'reviewing documentation',
                    'editing content',
                    'ensuring technical accuracy',
                    'working with SMEs',
                    'stakeholder communication',
                    'mentoring team members',
                    'managing documentation projects',
                    'quality reviews',
                    'content governance',
                    'proofreading',
                    'maintaining quality standards'
                ]
            },
            
            # AI/Automation transferable to various domains
            'ai_automation': {
                'general': [
                    'process improvement',
                    'efficiency optimization',
                    'workflow automation',
                    'data analysis',
                    'problem solving',
                    'innovation'
                ]
            },
            
            # Content Development universal skills
            'content_development': {
                'general': [
                    'creating documentation',
                    'collaborating with stakeholders',
                    'managing priorities',
                    'meeting deadlines',
                    'ensuring accuracy',
                    'adapting content for audiences'
                ]
            },
            
            # Leadership universal skills
            'leadership': {
                'general': [
                    'cross-functional collaboration',
                    'team leadership',
                    'mentoring',
                    'stakeholder management',
                    'project management',
                    'change management'
                ]
            }
        }
    
    def detect_domain_mismatch(self, resume_text: str, job_analysis: Dict) -> Dict:
        """
        Detect if there's a domain mismatch between resume and job.
        
        Returns:
            {
                'has_mismatch': bool,
                'resume_domain': str,
                'job_domain': str,
                'transferable_skills': List[str]
            }
        """
        resume_lower = resume_text.lower()
        job_industry = job_analysis.get('industry', '').lower()
        target_role = job_analysis.get('target_role', '').lower()
        
        # Detect resume domain
        resume_domain = self._detect_resume_domain(resume_lower)
        
        # Detect job domain
        job_domain = self._detect_job_domain(target_role, job_industry)
        
        # Check for mismatch
        has_mismatch = resume_domain != job_domain and resume_domain != 'general' and job_domain != 'general'
        
        # Get transferable skills
        transferable = []
        if has_mismatch:
            transferable = self._get_transferable_skills(resume_domain, job_domain, resume_lower)
        
        return {
            'has_mismatch': has_mismatch,
            'resume_domain': resume_domain,
            'job_domain': job_domain,
            'transferable_skills': transferable
        }
    
    def _detect_resume_domain(self, resume_text: str) -> str:
        """Detect primary domain from resume."""
        
        domain_indicators = {
            'ai_automation': ['ai', 'machine learning', 'automation', 'llm', 'generative ai', 'prompt engineering'],
            'technical_writing': ['technical writing', 'documentation', 'dita', 'xml', 'content development'],
            'medical_writing': ['medical writing', 'clinical', 'regulatory', 'pharmaceutical'],
            'software_engineering': ['software engineer', 'developer', 'programming', 'coding'],
            'data_science': ['data scientist', 'analytics', 'statistical', 'modeling']
        }
        
        domain_scores = {}
        for domain, indicators in domain_indicators.items():
            score = sum(1 for indicator in indicators if indicator in resume_text)
            domain_scores[domain] = score
        
        # Return domain with highest score
        if max(domain_scores.values()) > 0:
            return max(domain_scores, key=domain_scores.get)
        
        return 'general'
    
    def _detect_job_domain(self, target_role: str, industry: str) -> str:
        """Detect job domain from role and industry."""
        
        combined = f"{target_role} {industry}".lower()
        
        # Check for specific medical/healthcare roles FIRST (most specific)
        if any(term in combined for term in ['medical writer', 'clinical writer', 'scientific writer', 'regulatory writer']):
            return 'medical_writing'
        
        # Check for medical/healthcare industry
        if any(term in combined for term in ['medical', 'clinical', 'pharmaceutical', 'life sciences', 'pharma', 'healthcare', 'biotech']):
            # Only return medical_writing if it's actually a writing role
            if any(term in combined for term in ['writer', 'writing', 'documentation', 'content']):
                return 'medical_writing'
        
        # Technical writing (aerospace, software, general tech)
        if any(term in combined for term in ['technical writer', 'technical publications', 'documentation specialist', 'content developer']):
            return 'technical_writing'
        
        # AI/ML roles
        if any(term in combined for term in ['ai', 'machine learning', 'data science']):
            return 'ai_automation'
        
        # Software engineering
        if any(term in combined for term in ['software engineer', 'developer', 'programmer']):
            return 'software_engineering'
        
        return 'general'
    
    def _get_transferable_skills(self, from_domain: str, to_domain: str, resume_text: str) -> List[str]:
        """Get transferable skills from one domain to another."""
        
        transferable = []
        
        # Check if we have a mapping
        if from_domain in self.skill_mappings:
            domain_map = self.skill_mappings[from_domain]
            
            # Try specific mapping first
            if to_domain in domain_map:
                transferable.extend(domain_map[to_domain])
            # Fall back to general
            elif 'general' in domain_map:
                transferable.extend(domain_map['general'])
        
        # Filter to only skills that are actually present in resume
        verified_transferable = []
        for skill in transferable:
            # Check if skill or related concept is in resume
            skill_keywords = skill.lower().split()
            if any(keyword in resume_text for keyword in skill_keywords):
                verified_transferable.append(skill)
        
        return verified_transferable
    
    def enhance_summary_with_transferable_skills(self, base_summary: str, 
                                                 transferable_skills: List[str],
                                                 years: int,
                                                 job_domain: str = None,
                                                 resume_text: str = "",
                                                 job_requirements: List[str] = None) -> str:
        """
        Enhance summary by emphasizing transferable skills.
        
        This is used when there's a domain mismatch.
        Creates specific, achievement-focused summary that surfaces relevant experience.
        """
        if not transferable_skills:
            return base_summary
        
        # Build domain-specific summary using actual resume content
        if job_domain == 'medical_writing':
            return self._build_medical_writing_summary(transferable_skills, years, resume_text, job_requirements or [], job_domain)
        else:
            return self._build_generic_transferable_summary(transferable_skills, years, resume_text, job_requirements or [])
    
    def _build_medical_writing_summary(self, transferable_skills: List[str], years: int, 
                                      resume_text: str = "", job_requirements: List[str] = None,
                                      job_domain: str = None) -> str:
        """
        Build summary specifically for medical writing roles using actual resume content.
        """
        resume_lower = resume_text.lower()
        
        # Extract actual background from resume
        background = "Technical Communication Professional"
        if 'senior' in resume_lower or 'lead' in resume_lower:
            background = "Senior Technical Communication Professional"
        elif 'principal' in resume_lower:
            background = "Principal Technical Communication Professional"
        
        # Detect actual work context from resume (what they ACTUALLY worked in)
        actual_context = None
        if 'aerospace' in resume_lower or 'aviation' in resume_lower:
            actual_context = "aerospace and technology"
        elif 'healthcare' in resume_lower or 'medical device' in resume_lower:
            actual_context = "healthcare and life sciences"
        elif 'software' in resume_lower or 'saas' in resume_lower:
            actual_context = "software and technology"
        elif 'enterprise' in resume_lower:
            actual_context = "enterprise technology"
        elif 'telecom' in resume_lower or 'telecommunications' in resume_lower:
            actual_context = "telecommunications"
        
        # Detect target domain from job
        target_domain = job_domain if job_domain else None
        
        # Build core competencies from transferable skills and job requirements
        core_competencies = []
        
        # Prioritize job requirements if available
        if job_requirements:
            for req in job_requirements[:3]:
                req_lower = req.lower()
                if any(term in req_lower for term in ['review', 'edit', 'quality', 'accuracy']):
                    core_competencies.append("reviewing and editing technical content")
                elif any(term in req_lower for term in ['sme', 'subject matter', 'stakeholder']):
                    core_competencies.append("collaborating with subject matter experts")
                elif any(term in req_lower for term in ['mentor', 'coach', 'lead', 'team']):
                    core_competencies.append("mentoring team members")
                elif any(term in req_lower for term in ['standard', 'governance', 'compliance']):
                    core_competencies.append("maintaining quality standards")
        
        # Add from transferable skills if not enough from requirements
        if len(core_competencies) < 3:
            for skill in transferable_skills[:5]:
                if skill not in core_competencies:
                    core_competencies.append(skill)
                if len(core_competencies) >= 4:
                    break
        
        # Build truthful summary - state actual experience and transferability
        if actual_context:
            # Has specific industry experience
            summary = (
                f"Experienced {background} with {years}+ years creating, reviewing, and managing "
                f"high-quality technical documentation in {actual_context}. "
            )
        else:
            # Generic technical documentation experience
            summary = (
                f"Experienced {background} with {years}+ years creating, reviewing, and managing "
                f"high-quality technical documentation. "
            )
        
        # Add transferability statement ONLY if targeting a truly different domain
        # Don't add transferability for same-domain or technical writing roles
        is_cross_domain = False
        if target_domain and actual_context:
            # Check if it's a real domain mismatch (not just tech writing to tech writing)
            if target_domain == 'medical_writing' and actual_context not in ['healthcare and life sciences', 'medical']:
                is_cross_domain = True
        
        if is_cross_domain:
            summary += (
                f"Core competencies in technical communication are directly transferable to {target_domain.replace('_', ' ')}, including "
            )
        else:
            summary += "Proven ability to "
        
        if core_competencies:
            summary += f"{', '.join(core_competencies[:2])}"
            if len(core_competencies) > 2:
                summary += f", and {core_competencies[2]}"
            summary += ". "
        
        # Add specializations based on resume content
        specializations = []
        if 'dita' in resume_lower or 'xml' in resume_lower or 'structured' in resume_lower:
            specializations.append("structured authoring")
        if 'process' in resume_lower and 'improve' in resume_lower:
            specializations.append("process improvement")
        if 'agile' in resume_lower or 'scrum' in resume_lower:
            specializations.append("agile methodologies")
        if 'api' in resume_lower or 'developer' in resume_lower:
            specializations.append("developer documentation")
        
        if specializations:
            summary += f"Strong background in {', '.join(specializations[:3])}, "
        else:
            summary += "Strong background in content governance, "
        
        summary += "delivering clear, consistent documentation in fast-paced environments."
        
        return summary
    
    def _build_generic_transferable_summary(self, transferable_skills: List[str], years: int,
                                           resume_text: str = "", job_requirements: List[str] = None) -> str:
        """Build generic transferable skills summary using actual resume content."""
        
        resume_lower = resume_text.lower()
        
        # Detect actual role/background from resume
        # IMPORTANT: Check writing/documentation roles FIRST since technical writers 
        # may have engineering background but their primary role is writing
        role = "Professional"
        if 'technical writer' in resume_lower or 'technical communication' in resume_lower or 'documentation specialist' in resume_lower:
            role = "Technical Communication Professional"
        elif 'writer' in resume_lower or 'documentation' in resume_lower:
            role = "Technical Communication Professional"
        elif 'engineer' in resume_lower:
            role = "Engineering Professional"
        elif 'manager' in resume_lower or 'director' in resume_lower:
            role = "Leadership Professional"
        elif 'analyst' in resume_lower:
            role = "Analyst"
        elif 'developer' in resume_lower:
            role = "Development Professional"
        
        # Detect seniority
        if 'senior' in resume_lower or 'lead' in resume_lower:
            role = f"Senior {role}"
        elif 'principal' in resume_lower:
            role = f"Principal {role}"
        
        # Group skills into categories
        core_skills = transferable_skills[:4]
        additional_skills = transferable_skills[4:6] if len(transferable_skills) > 4 else []
        
        # Build enhanced summary
        summary_parts = []
        
        # Opening focused on transferable experience
        summary_parts.append(
            f"{role} with {years}+ years of experience"
        )
        
        # Core transferable skills - prioritize job requirements
        skills_to_highlight = []
        if job_requirements:
            for req in job_requirements[:3]:
                if req.lower() in resume_lower:
                    skills_to_highlight.append(req.lower())
        
        # Add transferable skills
        for skill in core_skills:
            if len(skills_to_highlight) < 4:
                skills_to_highlight.append(skill)
        
        if skills_to_highlight:
            skills_text = ', '.join(skills_to_highlight[:3])
            if len(skills_to_highlight) > 3:
                skills_text += f", and {skills_to_highlight[3]}"
            summary_parts.append(skills_text)
        
        # Additional strengths based on resume content
        strengths = []
        if 'agile' in resume_lower or 'scrum' in resume_lower:
            strengths.append("agile methodologies")
        if 'lead' in resume_lower or 'mentor' in resume_lower:
            strengths.append("team leadership")
        if 'process' in resume_lower and 'improve' in resume_lower:
            strengths.append("process improvement")
        
        if not strengths and additional_skills:
            strengths = additional_skills
        
        if strengths:
            summary_parts.append(
                f"Strong background in {', '.join(strengths[:2])}"
            )
        
        # Value proposition
        summary_parts.append(
            "Recognized for driving process improvements, leading cross-functional initiatives, "
            "and delivering high-quality results"
        )
        
        return ". ".join(summary_parts) + "."
