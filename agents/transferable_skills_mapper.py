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
        """Detect job domain from role and industry - AGGRESSIVE detection."""
        
        combined = f"{target_role} {industry}".lower()
        
        # AGGRESSIVE medical writing detection - catch all variations
        medical_terms = [
            'medical', 'clinical', 'pharmaceutical', 'life sciences', 'pharma',
            'healthcare', 'biotech', 'scientific writing', 'medical communications',
            'regulatory writing', 'medical writer', 'clinical writer', 'scientific writer',
            'health', 'drug', 'therapy', 'patient', 'physician', 'publication'
        ]
        
        if any(term in combined for term in medical_terms):
            return 'medical_writing'
        elif any(term in combined for term in ['technical writer', 'documentation', 'content']):
            return 'technical_writing'
        elif any(term in combined for term in ['ai', 'machine learning', 'data science']):
            return 'ai_automation'
        elif any(term in combined for term in ['software', 'engineer', 'developer']):
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
                                                 job_domain: str = None) -> str:
        """
        Enhance summary by emphasizing transferable skills.
        
        This is used when there's a domain mismatch.
        Creates specific, achievement-focused summary that surfaces relevant experience.
        """
        if not transferable_skills:
            return base_summary
        
        # Build domain-specific summary
        if job_domain == 'medical_writing':
            return self._build_medical_writing_summary(transferable_skills, years)
        else:
            return self._build_generic_transferable_summary(transferable_skills, years)
    
    def _build_medical_writing_summary(self, transferable_skills: List[str], years: int) -> str:
        """
        Build summary specifically for medical writing roles.
        
        This is the GOLD STANDARD - based on user feedback showing what good looks like.
        """
        
        # Use the exact structure from latest user feedback - emphasize content accuracy FIRST
        summary = (
            f"Experienced Technical Communication Professional with {years}+ years of experience "
            f"creating, reviewing, and managing high-quality technical documentation for global organizations. "
            f"Proven ability to ensure content accuracy, collaborate with cross-functional stakeholders and subject matter experts, "
            f"and maintain documentation quality standards. "
            f"Strong background in structured authoring, content governance, mentoring team members, "
            f"and delivering clear, consistent documentation in fast-paced environments."
        )
        
        return summary
    
    def _build_generic_transferable_summary(self, transferable_skills: List[str], years: int) -> str:
        """Build generic transferable skills summary."""
        
        # Group skills into categories
        core_skills = transferable_skills[:4]
        additional_skills = transferable_skills[4:6] if len(transferable_skills) > 4 else []
        
        # Build enhanced summary
        summary_parts = []
        
        # Opening focused on transferable experience
        summary_parts.append(
            f"Professional with {years}+ years of experience"
        )
        
        # Core transferable skills
        if core_skills:
            skills_text = ', '.join(core_skills[:3])
            if len(core_skills) > 3:
                skills_text += f", and {core_skills[3]}"
            summary_parts.append(skills_text)
        
        # Additional strengths
        if additional_skills:
            summary_parts.append(
                f"Strong background in {', '.join(additional_skills)}"
            )
        
        # Value proposition
        summary_parts.append(
            "Recognized for driving process improvements, leading cross-functional initiatives, "
            "and delivering high-quality results"
        )
        
        return ". ".join(summary_parts) + "."
