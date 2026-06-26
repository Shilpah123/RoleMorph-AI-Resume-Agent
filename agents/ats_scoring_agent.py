"""
ATS Scoring Agent - Calculates weighted ATS score.
"""

from typing import Dict, List


class ATSScoringAgent:
    """Calculates comprehensive ATS score with semantic capability mapping."""
    
    def __init__(self):
        # Skill normalization map - maps resume skills to job requirement equivalents
        self.skill_map = {
            'technical documentation': ['medical writing', 'scientific writing', 'clinical writing', 'regulatory writing'],
            'technical writing': ['medical writing', 'scientific writing', 'clinical writing'],
            'content development': ['medical writing', 'scientific writing', 'content creation'],
            'documentation': ['writing', 'authoring', 'content creation'],
            'content review': ['editing', 'proofreading', 'reviewing', 'quality review'],
            'reviewing': ['editing', 'proofreading', 'quality control'],
            'ensuring accuracy': ['quality control', 'accuracy verification', 'validation'],
            'documentation accuracy': ['content accuracy', 'scientific accuracy', 'quality standards'],
            'stakeholder collaboration': ['working with SMEs', 'SME collaboration', 'cross-functional collaboration'],
            'cross-functional collaboration': ['working with SMEs', 'stakeholder engagement'],
            'documentation quality': ['publication quality', 'regulatory accuracy', 'quality standards'],
            'content governance': ['editorial standards', 'publication standards', 'quality control'],
            'structured authoring': ['DITA', 'XML', 'structured content', 'technical authoring'],
            'team leadership': ['mentoring', 'coaching', 'managing writers'],
            'mentoring': ['coaching', 'training', 'developing team members']
        }
        
        # Role adjacency map - similar roles that should get bonus
        self.role_adjacency = {
            'medical writer': ['technical writer', 'scientific writer', 'clinical writer', 'content developer', 'documentation specialist', 'technical communication'],
            'scientific writer': ['technical writer', 'medical writer', 'research writer', 'content developer'],
            'clinical writer': ['medical writer', 'scientific writer', 'technical writer'],
            'technical writer': ['medical writer', 'scientific writer', 'documentation specialist', 'content developer'],
            'content developer': ['technical writer', 'medical writer', 'documentation specialist'],
            'documentation specialist': ['technical writer', 'content developer', 'medical writer']
        }
    
    def calculate_score_strict(self, 
                       resume_text: str,
                       job_analysis: Dict,
                       gap_analysis: Dict) -> Dict:
        """
        Calculate ATS score with STRICT literal matching only (no semantic understanding).
        Used for before score to show improvement from customization.
        """
        resume_lower = resume_text.lower()
        
        # Calculate each component with STRICT matching
        keyword_score = self._calculate_keyword_match_strict(resume_lower, job_analysis)
        skills_score = self._calculate_skills_match(gap_analysis)
        experience_score = self._calculate_experience_match(resume_lower, job_analysis)
        title_score = self._calculate_title_alignment(resume_lower, job_analysis)
        education_score = self._calculate_education_match(resume_lower, job_analysis)
        
        # Weighted overall score
        overall = int(
            (keyword_score * 0.40) +
            (skills_score * 0.25) +
            (experience_score * 0.20) +
            (title_score * 0.10) +
            (education_score * 0.05)
        )
        
        # NO adjacency boost for strict scoring
        
        # Create breakdown text
        breakdown = self._create_breakdown(
            keyword_score, skills_score, experience_score,
            title_score, education_score
        )
        
        # Calculate confidence score
        confidence = self._calculate_confidence(job_analysis, resume_text)
        
        return {
            'overall_score': overall,
            'keyword_match': keyword_score,
            'skills_match': skills_score,
            'experience_match': experience_score,
            'title_alignment': title_score,
            'education_match': education_score,
            'breakdown': breakdown,
            'confidence': confidence
        }
    
    def calculate_score(self, 
                       resume_text: str,
                       job_analysis: Dict,
                       gap_analysis: Dict) -> Dict:
        """
        Calculate ATS score with weighted components.
        
        Scoring breakdown:
        - Keyword Match: 40%
        - Skills Match: 25%
        - Experience Match: 20%
        - Title Alignment: 10%
        - Education Match: 5%
        
        Returns:
            {
                'overall_score': int (0-100),
                'keyword_match': int,
                'skills_match': int,
                'experience_match': int,
                'title_alignment': int,
                'education_match': int,
                'breakdown': str
            }
        """
        resume_lower = resume_text.lower()
        
        # Calculate each component
        keyword_score = self._calculate_keyword_match(resume_lower, job_analysis)
        skills_score = self._calculate_skills_match(gap_analysis)
        experience_score = self._calculate_experience_match(resume_lower, job_analysis)
        title_score = self._calculate_title_alignment(resume_lower, job_analysis)
        education_score = self._calculate_education_match(resume_lower, job_analysis)
        
        # Weighted overall score
        overall = int(
            (keyword_score * 0.40) +
            (skills_score * 0.25) +
            (experience_score * 0.20) +
            (title_score * 0.10) +
            (education_score * 0.05)
        )
        
        # Add adjacency boost if roles are functionally adjacent
        if self._has_role_adjacency(resume_text, job_analysis):
            adjacency_boost = 10  # +10 points for adjacent roles
            overall = min(100, overall + adjacency_boost)
            print(f"  ✓ Role adjacency detected - adding +{adjacency_boost} point boost")
        
        # Create breakdown text
        breakdown = self._create_breakdown(
            keyword_score, skills_score, experience_score,
            title_score, education_score
        )
        
        # Calculate confidence score
        confidence = self._calculate_confidence(job_analysis, resume_text)
        
        return {
            'overall_score': overall,
            'keyword_match': keyword_score,
            'skills_match': skills_score,
            'experience_match': experience_score,
            'title_alignment': title_score,
            'education_match': education_score,
            'breakdown': breakdown,
            'confidence': confidence
        }
    
    def _calculate_keyword_match_strict(self, resume_text: str, job_analysis: Dict) -> int:
        """Calculate STRICT keyword match score - literal matches only, no semantic understanding."""
        
        required_skills = job_analysis.get('required_skills', [])
        preferred_skills = job_analysis.get('preferred_skills', [])
        tools = job_analysis.get('tools', [])
        
        # Weight keywords
        weights = {
            'required': 5,
            'preferred': 2,
            'tools': 1
        }
        
        total_weight = 0
        matched_weight = 0
        
        # Track matches for debug
        required_matched = []
        required_missing = []
        preferred_matched = []
        preferred_missing = []
        
        # Check required skills with LITERAL matching only
        for skill in required_skills:
            total_weight += weights['required']
            if skill.lower() in resume_text.lower():  # Literal match only
                matched_weight += weights['required']
                required_matched.append(skill)
            else:
                required_missing.append(skill)
        
        # Check preferred skills with LITERAL matching only
        for skill in preferred_skills:
            total_weight += weights['preferred']
            if skill.lower() in resume_text.lower():  # Literal match only
                matched_weight += weights['preferred']
                preferred_matched.append(skill)
            else:
                preferred_missing.append(skill)
        
        # Check tools (literal)
        for tool in tools:
            total_weight += weights['tools']
            if tool.lower() in resume_text.lower():
                matched_weight += weights['tools']
        
        if total_weight == 0:
            return 50  # Lower default for strict scoring
        
        score = int((matched_weight / total_weight) * 100)
        
        # DEBUG OUTPUT
        print(f"\n   🔍 STRICT SCORING DEBUG:")
        print(f"      Required matched: {len(required_matched)}/{len(required_skills)}")
        if required_matched[:5]:
            print(f"         ✓ {', '.join(required_matched[:5])}")
        if required_missing[:5]:
            print(f"         ✗ {', '.join(required_missing[:5])}")
        print(f"      Preferred matched: {len(preferred_matched)}/{len(preferred_skills)}")
        print(f"      Score: {score}/100")
        
        return score
    
    def _calculate_keyword_match(self, resume_text: str, job_analysis: Dict) -> int:
        """Calculate SEMANTIC keyword match score using skill normalization."""
        
        required_skills = job_analysis.get('required_skills', [])
        preferred_skills = job_analysis.get('preferred_skills', [])
        tools = job_analysis.get('tools', [])
        
        # Weight keywords
        weights = {
            'required': 5,
            'preferred': 2,
            'tools': 1
        }
        
        total_weight = 0
        matched_weight = 0
        
        # Check required skills with SEMANTIC matching
        for skill in required_skills:
            total_weight += weights['required']
            if self._semantic_match(skill.lower(), resume_text):
                matched_weight += weights['required']
        
        # Check preferred skills with SEMANTIC matching
        for skill in preferred_skills:
            total_weight += weights['preferred']
            if self._semantic_match(skill.lower(), resume_text):
                matched_weight += weights['preferred']
        
        # Check tools (still literal for tools)
        for tool in tools:
            total_weight += weights['tools']
            if tool.lower() in resume_text:
                matched_weight += weights['tools']
        
        if total_weight == 0:
            return 70  # Default higher for no keywords
        
        score = int((matched_weight / total_weight) * 100)
        
        # Boost score if we have strong semantic matches
        if score >= 50:
            score = min(100, score + 10)  # +10 bonus for semantic understanding
        
        return score
    
    def _semantic_match(self, job_skill: str, resume_text: str) -> bool:
        """Check if job skill matches resume using semantic equivalents and implied skills."""
        
        # Direct match
        if job_skill in resume_text:
            return True
        
        # CRITICAL: Check for IMPLIED skills
        # Communications is implied by documentation/editing/writing work
        if job_skill in ['communication', 'communications', 'communication skills']:
            if any(term in resume_text for term in ['documentation', 'editing', 'writing', 'content development', 'technical writer', 'content writer']):
                return True
        
        # Editing is implied by documentation/content work
        if job_skill in ['editing', 'edit', 'editorial']:
            if any(term in resume_text for term in ['documentation', 'content development', 'technical writer', 'content writer', 'reviewed', 'validated']):
                return True
        
        # Writing is implied by documentation/content work
        if job_skill in ['writing', 'write', 'written']:
            if any(term in resume_text for term in ['documentation', 'content development', 'technical writer', 'content writer', 'authored', 'created']):
                return True
        
        # Project Management is implied by team leadership/coordination
        if job_skill in ['project management', 'project coordination']:
            if any(term in resume_text for term in ['managed team', 'led team', 'coordinated', 'managed projects', 'project lead']):
                return True
        
        # Check skill normalization map
        for resume_skill, job_equivalents in self.skill_map.items():
            # If resume has this skill and it maps to the job skill
            if resume_skill in resume_text and job_skill in [eq.lower() for eq in job_equivalents]:
                return True
        
        # Check reverse mapping (job skill in resume maps to requirement)
        for resume_skill, job_equivalents in self.skill_map.items():
            if job_skill in resume_skill and resume_skill in resume_text:
                return True
        
        return False
    
    def _calculate_skills_match(self, gap_analysis: Dict) -> int:
        """Calculate skills match score - ONLY relevant skills."""
        
        strong_match = gap_analysis.get('strong_match', [])
        partial_match = gap_analysis.get('partial_match', [])
        transferable = gap_analysis.get('transferable_skills', [])
        missing = gap_analysis.get('missing_skills', [])
        
        # Filter out irrelevant technical skills (Python, CI/CD, etc.) from missing
        # These shouldn't penalize the score for a writing role
        irrelevant_tech = ['python', 'ci/cd', 'jenkins', 'docker', 'kubernetes', 'java', 'javascript']
        missing_relevant = [skill for skill in missing if not any(tech in skill.lower() for tech in irrelevant_tech)]
        
        total_skills = len(strong_match) + len(partial_match) + len(transferable) + len(missing_relevant)
        
        if total_skills == 0:
            return 70  # Default higher
        
        # Weight different match types - BOOST transferable skills
        score = (
            (len(strong_match) * 1.0) +
            (len(partial_match) * 0.7) +
            (len(transferable) * 0.6)  # Transferable skills are VALUABLE, not weak
        ) / total_skills
        
        return int(score * 100)
    
    def _calculate_experience_match(self, resume_text: str, job_analysis: Dict) -> int:
        """Calculate experience match score."""
        
        years_required = job_analysis.get('years_required', 0)
        
        if years_required == 0:
            return 100  # No specific requirement
        
        # Extract years from resume
        import re
        years_match = re.search(r'(\d+)\+?\s*years', resume_text)
        
        if not years_match:
            return 50  # Can't determine
        
        years_in_resume = int(years_match.group(1))
        
        # Score based on how well experience matches
        if years_in_resume >= years_required:
            # Meets or exceeds requirement
            if years_in_resume <= years_required + 5:
                return 100  # Perfect match
            else:
                return 95  # Overqualified but still good
        else:
            # Below requirement
            gap = years_required - years_in_resume
            if gap <= 2:
                return 80  # Close enough
            elif gap <= 5:
                return 60  # Moderate gap
            else:
                return 30  # Significant gap
    
    def _calculate_title_alignment(self, resume_text: str, job_analysis: Dict) -> int:
        """Calculate title alignment score with ROLE ADJACENCY bonus."""
        
        target_role = job_analysis.get('target_role', '').lower()
        
        if not target_role or target_role == 'not specified':
            return 100
        
        # Check for direct match first
        if target_role in resume_text:
            return 100
        
        # Check for role adjacency (similar roles) - MORE AGGRESSIVE
        for role, adjacent_roles in self.role_adjacency.items():
            if role in target_role:
                # Check if resume has any adjacent role
                for adj_role in adjacent_roles:
                    if adj_role in resume_text:
                        # Adjacent role match - give 65% base score
                        # This is functionally adjacent, not weakly related
                        return 65
        
        # Check reverse - if resume role has target as adjacent
        for role, adjacent_roles in self.role_adjacency.items():
            if role in resume_text:
                for adj_role in adjacent_roles:
                    if adj_role in target_role:
                        return 65  # Bidirectional adjacency
        
        # Check for functional similarity (writing roles)
        writing_indicators = ['writer', 'writing', 'documentation', 'content', 'communication', 'technical']
        resume_has_writing = any(ind in resume_text for ind in writing_indicators)
        job_has_writing = any(ind in target_role for ind in writing_indicators)
        
        if resume_has_writing and job_has_writing:
            # Both are writing-related roles, even if not exact match
            return 60  # Functional adjacency
        
        # Fallback to term matching
        role_terms = target_role.split()
        matches = sum(1 for term in role_terms if term in resume_text)
        
        if len(role_terms) == 0:
            return 100
        
        match_ratio = matches / len(role_terms)
        
        if match_ratio >= 0.8:
            return 100
        elif match_ratio >= 0.5:
            return 75
        elif match_ratio >= 0.3:
            return 60
        else:
            return 45  # Slightly boosted from 40
    
    def _calculate_education_match(self, resume_text: str, job_analysis: Dict) -> int:
        """Calculate education match score."""
        
        # Common degree terms
        degree_terms = ['bachelor', 'master', 'phd', 'doctorate', 'msc', 'bsc', 'mba']
        
        has_degree = any(term in resume_text for term in degree_terms)
        
        if has_degree:
            return 100
        else:
            return 50  # May have equivalent experience
    
    def _has_role_adjacency(self, resume_text: str, job_analysis: Dict) -> bool:
        """Check if resume role and job role are functionally adjacent."""
        
        target_role = job_analysis.get('target_role', '').lower()
        resume_lower = resume_text.lower()
        
        # Check role adjacency map
        for role, adjacent_roles in self.role_adjacency.items():
            if role in target_role:
                for adj_role in adjacent_roles:
                    if adj_role in resume_lower:
                        return True
        
        # Check reverse
        for role, adjacent_roles in self.role_adjacency.items():
            if role in resume_lower:
                for adj_role in adjacent_roles:
                    if adj_role in target_role:
                        return True
        
        return False
    
    def _calculate_confidence(self, job_analysis: Dict, resume_text: str) -> Dict:
        """Calculate confidence score based on data quality."""
        
        confidence_score = 100
        issues = []
        warnings = []
        
        # Check job completeness
        target_role = job_analysis.get('target_role', '').lower()
        if target_role in ['the role', 'not specified', '', 'none']:
            confidence_score -= 30
            issues.append("Job title not extracted")
        
        required_skills = job_analysis.get('required_skills', [])
        if not required_skills or len(required_skills) == 0:
            confidence_score -= 25
            issues.append("Job requirements not parsed")
        
        # CRITICAL: Detect sparse skill extraction (skill collapse bug)
        # If JD is long but only 1-3 skills extracted, likely parsing failure
        job_desc_length = len(job_analysis.get('_raw_jd', ''))  # Will add this
        if required_skills and len(required_skills) <= 3 and job_desc_length > 500:
            confidence_score -= 35
            issues.append("Skill extraction may be incomplete (only extracted " + str(len(required_skills)) + " skills from detailed JD)")
            warnings.append("CAUTION: Score may be inflated due to incomplete skill extraction")
        
        # Check resume completeness
        if len(resume_text) < 100:
            confidence_score -= 20
            issues.append("Resume appears incomplete")
        
        # Determine confidence level
        if confidence_score >= 80:
            level = "HIGH"
        elif confidence_score >= 50:
            level = "MEDIUM"
        else:
            level = "LOW"
        
        return {
            'level': level,
            'score': confidence_score,
            'issues': issues,
            'warnings': warnings
        }
    
    def _create_breakdown(self, keyword: int, skills: int, experience: int,
                         title: int, education: int) -> str:
        """Create detailed breakdown text."""
        
        breakdown = f"""
Keyword Match: {keyword}% (Weight: 40%)
Skills Match: {skills}% (Weight: 25%)
Experience Match: {experience}% (Weight: 20%)
Title Alignment: {title}% (Weight: 10%)
Education Match: {education}% (Weight: 5%)
"""
        return breakdown.strip()
