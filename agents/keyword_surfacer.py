"""
Keyword Surfacer - Identifies what employer wants and surfaces relevant existing experience.
"""

import re
from typing import Dict, List, Set


class KeywordSurfacer:
    """
    Surfaces relevant keywords from existing experience based on job requirements.
    
    Philosophy: Don't just rewrite sentences - identify what employer wants,
    then surface the most relevant existing experience.
    """
    
    def __init__(self):
        # Map job keywords to resume equivalents
        self.keyword_mappings = {
            # Medical Writing keywords
            'reviewing': ['validated', 'reviewed', 'ensured accuracy', 'quality control', 'verified'],
            'editing': ['edited', 'refined', 'revised', 'updated', 'improved'],
            'proofreading': ['validated', 'reviewed', 'ensured accuracy', 'quality checked'],
            'quality': ['quality', 'accuracy', 'standards', 'excellence', 'high-quality'],
            'content development': ['created', 'developed', 'authored', 'wrote', 'produced'],
            'subject matter experts': ['SMEs', 'experts', 'stakeholders', 'technical teams', 'product teams'],
            'mentoring': ['mentored', 'coached', 'trained', 'guided', 'led team'],
            'prioritization': ['managed priorities', 'prioritized', 'coordinated', 'balanced'],
            'scientific communication': ['technical communication', 'documentation', 'content'],
            
            # General transferable keywords
            'collaboration': ['collaborated', 'worked with', 'partnered', 'coordinated'],
            'stakeholder': ['stakeholder', 'client', 'customer', 'business'],
            'documentation': ['documentation', 'content', 'materials', 'guides'],
            'accuracy': ['accuracy', 'precision', 'correctness', 'quality'],
            'standards': ['standards', 'guidelines', 'best practices', 'processes']
        }
    
    def identify_job_priorities(self, job_desc: str, job_analysis: Dict) -> List[str]:
        """
        Identify what the employer really wants based on frequency and emphasis.
        
        Returns list of priority keywords in order of importance.
        """
        job_lower = job_desc.lower()
        
        # Count keyword frequency
        keyword_freq = {}
        
        # Check required skills
        required_skills = job_analysis.get('required_skills', [])
        for skill in required_skills:
            skill_lower = skill.lower()
            # Count occurrences
            count = job_lower.count(skill_lower)
            if count > 0:
                keyword_freq[skill_lower] = count * 3  # Weight required skills higher
        
        # Check for emphasis keywords
        emphasis_patterns = [
            (r'must\s+(?:have|be|demonstrate)\s+(\w+(?:\s+\w+){0,3})', 5),  # "must have X"
            (r'strong\s+(\w+(?:\s+\w+){0,2})', 3),  # "strong X"
            (r'proven\s+(\w+(?:\s+\w+){0,2})', 3),  # "proven X"
            (r'experience\s+(?:in|with)\s+(\w+(?:\s+\w+){0,3})', 2),  # "experience in X"
        ]
        
        for pattern, weight in emphasis_patterns:
            matches = re.findall(pattern, job_lower)
            for match in matches:
                keyword_freq[match] = keyword_freq.get(match, 0) + weight
        
        # Sort by frequency/weight
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Return top keywords
        return [kw for kw, freq in sorted_keywords[:15]]
    
    def surface_relevant_experience(self, bullet: str, priority_keywords: List[str]) -> str:
        """
        Surface relevant experience by replacing generic terms with job-relevant ones.
        
        Example:
        Input: "Validated product installations and ensured documentation accuracy"
        Priority: ['reviewing', 'quality', 'accuracy']
        Output: "Reviewed product installations for accuracy and ensured documentation quality standards"
        """
        bullet_lower = bullet.lower()
        enhanced = bullet
        
        # Check which priority keywords are relevant
        for priority_kw in priority_keywords:
            if priority_kw not in self.keyword_mappings:
                continue
            
            equivalents = self.keyword_mappings[priority_kw]
            
            # Check if any equivalent is in the bullet
            for equiv in equivalents:
                if equiv.lower() in bullet_lower:
                    # Surface the priority keyword
                    enhanced = self._replace_with_priority(enhanced, equiv, priority_kw)
                    break
        
        return enhanced
    
    def _replace_with_priority(self, bullet: str, equivalent: str, priority_keyword: str) -> str:
        """Replace equivalent term with priority keyword naturally."""
        
        replacements = {
            # Reviewing/Quality
            ('validated', 'reviewing'): 'reviewed',
            ('validated', 'quality'): 'validated for quality',
            ('ensured accuracy', 'reviewing'): 'reviewed for accuracy',
            ('ensured accuracy', 'quality'): 'ensured quality standards',
            
            # Collaboration
            ('worked with', 'subject matter experts'): 'collaborated with subject matter experts',
            ('coordinated', 'stakeholder'): 'coordinated with stakeholders',
            
            # Leadership
            ('led team', 'mentoring'): 'led and mentored team',
            ('managed team', 'mentoring'): 'managed team, mentoring members',
            
            # Content
            ('created', 'content development'): 'developed content',
            ('wrote', 'content development'): 'developed content',
        }
        
        # Check for direct replacement
        key = (equivalent.lower(), priority_keyword.lower())
        if key in replacements:
            # Case-insensitive replacement
            pattern = re.compile(re.escape(equivalent), re.IGNORECASE)
            return pattern.sub(replacements[key], bullet, count=1)
        
        return bullet
    
    def enhance_bullet_with_surfacing(self, bullet: str, priority_keywords: List[str], missing_skills: List[str] = None) -> str:
        """
        AGGRESSIVELY enhance bullet by surfacing relevant keywords and transforming structure.
        
        Goal: Make customization OBVIOUS and VISIBLE and IMPROVE ATS SCORE.
        """
        original = bullet
        
        # First, apply aggressive transformations
        enhanced = self._apply_aggressive_transformations(bullet, priority_keywords)
        if enhanced != original:
            print(f"         → Aggressive transformation applied")
        
        # Then, add relevant context
        enhanced = self._add_relevant_context(enhanced, priority_keywords)
        if enhanced != original:
            print(f"         → Relevant context added")
        
        # CRITICAL: Add missing skills to improve ATS score
        if missing_skills:
            enhanced = self._inject_missing_skills(enhanced, missing_skills, priority_keywords)
            if enhanced != original:
                print(f"         → Missing skills injected for ATS improvement")
        
        # Finally, surface any remaining keywords
        enhanced = self.surface_relevant_experience(enhanced, priority_keywords)
        if enhanced != original:
            print(f"         → Keywords surfaced")
        
        if enhanced == original:
            print(f"         ℹ No transformations matched this bullet")
        
        return enhanced
    
    def _apply_aggressive_transformations(self, bullet: str, priority_keywords: List[str]) -> str:
        """
        Apply AGGRESSIVE transformations to make customization OBVIOUS.
        
        Goal: Every relevant bullet should be visibly enhanced.
        """
        
        bullet_lower = bullet.lower()
        transformed = bullet
        
        # Pattern 1: Team management + reviewing/mentoring priorities
        if 'managed' in bullet_lower or 'led' in bullet_lower:
            if any(kw in priority_keywords for kw in ['reviewing', 'mentoring', 'quality']):
                # Specific: "delivering high-quality product documentation"
                if 'delivering high-quality product documentation' in bullet_lower:
                    transformed = transformed.replace(
                        'delivering high-quality product documentation',
                        'delivering high-quality product documentation, reviewing deliverables, mentoring team members, and ensuring consistency, accuracy, and quality standards'
                    )
                # Specific: "delivering" + "documentation"
                elif 'delivering' in bullet_lower and 'documentation' in bullet_lower:
                    if 'reviewing' not in bullet_lower:
                        transformed = transformed.replace(
                            'delivering',
                            'reviewing deliverables, mentoring team members, and delivering'
                        )
                # General: Any "managed team" without reviewing/mentoring
                elif 'team' in bullet_lower and 'reviewing' not in bullet_lower and 'mentoring' not in bullet_lower:
                    # Add at end
                    transformed = transformed.rstrip('.') + ', reviewing deliverables and mentoring team members'
        
        # Pattern 2: Validation + accuracy + quality priorities
        if 'validated' in bullet_lower or 'verified' in bullet_lower:
            if any(kw in priority_keywords for kw in ['reviewing', 'quality', 'accuracy']):
                # Specific: "and ensured documentation accuracy"
                if 'and ensured documentation accuracy' in bullet_lower:
                    transformed = transformed.replace(
                        'and ensured documentation accuracy',
                        'while reviewing documentation for accuracy, consistency, and quality standards'
                    )
                # Specific: "ensured accuracy"
                elif 'ensured accuracy' in bullet_lower:
                    transformed = transformed.replace(
                        'ensured accuracy',
                        'reviewed for accuracy and quality standards'
                    )
                # General: Any validation without reviewing
                elif 'reviewing' not in bullet_lower and 'review' not in bullet_lower:
                    # Add reviewing context
                    if 'documentation' in bullet_lower:
                        transformed = transformed.rstrip('.') + ', reviewing documentation for accuracy and quality standards'
        
        # Pattern 3: Collaboration + SME priorities
        if any(term in bullet_lower for term in ['worked with', 'collaborated', 'coordinated with', 'partnered']):
            if any(kw in priority_keywords for kw in ['subject matter experts', 'sme', 'stakeholder']):
                # Specific: stakeholders → subject matter experts and stakeholders
                if 'stakeholders' in bullet_lower and 'subject matter' not in bullet_lower:
                    transformed = transformed.replace(
                        'stakeholders',
                        'subject matter experts and stakeholders'
                    )
                # Specific: teams → subject matter experts
                elif 'teams' in bullet_lower and 'subject matter' not in bullet_lower and 'development' not in bullet_lower:
                    transformed = transformed.replace(
                        'teams',
                        'subject matter experts'
                    )
                # General: Any collaboration without SME mention
                elif 'subject matter' not in bullet_lower and 'sme' not in bullet_lower:
                    transformed = transformed.replace(
                        'collaborated with',
                        'collaborated with subject matter experts and'
                    )
        
        # Pattern 4: Ensuring/maintaining + quality/accuracy
        if 'ensuring' in bullet_lower or 'maintaining' in bullet_lower:
            # Specific: stakeholder alignment → alignment with stakeholder requirements
            if 'stakeholder' in priority_keywords:
                if 'alignment' in bullet_lower and 'requirements' not in bullet_lower:
                    transformed = transformed.replace(
                        'stakeholder alignment',
                        'alignment with stakeholder requirements'
                    )
                    transformed = transformed.replace(
                        'cross-functional collaboration and stakeholder alignment',
                        'alignment with stakeholder requirements'
                    )
            
            # Specific: ensuring documentation accuracy → ensuring content accuracy and consistency
            if 'ensuring documentation accuracy' in bullet_lower:
                transformed = transformed.replace(
                    'ensuring documentation accuracy',
                    'ensuring content accuracy and consistency'
                )
            # General: ensuring + quality/accuracy priority
            elif any(kw in priority_keywords for kw in ['quality', 'accuracy', 'consistency']):
                if 'quality' in bullet_lower and 'standards' not in bullet_lower:
                    transformed = transformed.replace(
                        'quality',
                        'quality standards'
                    )
        
        # Pattern 5: Created/developed + content/documentation
        if any(term in bullet_lower for term in ['created', 'developed', 'authored', 'wrote']):
            if any(kw in priority_keywords for kw in ['reviewing', 'quality', 'content development']):
                if 'documentation' in bullet_lower or 'content' in bullet_lower:
                    # Add quality/review context if missing
                    if 'quality' not in bullet_lower and 'accuracy' not in bullet_lower:
                        transformed = transformed.rstrip('.') + ', ensuring content accuracy and quality standards'
        
        # Pattern 6: Improved/enhanced + documentation/content
        if any(term in bullet_lower for term in ['improved', 'enhanced', 'optimized', 'streamlined']):
            if any(kw in priority_keywords for kw in ['quality', 'accuracy', 'consistency']):
                if 'documentation' in bullet_lower or 'content' in bullet_lower or 'process' in bullet_lower:
                    # Add quality/consistency context
                    if 'quality' not in bullet_lower and 'consistency' not in bullet_lower:
                        transformed = transformed.rstrip('.') + ', improving content quality and consistency'
        
        return transformed
    
    def _add_relevant_context(self, bullet: str, priority_keywords: List[str]) -> str:
        """
        AGGRESSIVELY add relevant context to ANY bullet that could benefit.
        
        This is the fallback that catches bullets not handled by specific patterns.
        """
        
        bullet_lower = bullet.lower()
        
        # FALLBACK 1: Any bullet with "documentation" or "content" + quality priority
        if any(term in bullet_lower for term in ['documentation', 'content', 'materials']):
            if any(kw in priority_keywords for kw in ['quality', 'accuracy', 'reviewing']):
                # If no quality/accuracy/review terms present, add them
                if not any(term in bullet_lower for term in ['quality', 'accuracy', 'review', 'consistent', 'standard']):
                    bullet = bullet.rstrip('.') + ', ensuring content quality and accuracy'
        
        # FALLBACK 2: Any bullet with team/people management + mentoring priority
        if any(term in bullet_lower for term in ['team', 'members', 'developers', 'writers']):
            if 'mentoring' in priority_keywords or 'coaching' in priority_keywords:
                if 'mentor' not in bullet_lower and 'coach' not in bullet_lower and 'train' not in bullet_lower:
                    # Only add if it's about managing/leading
                    if any(term in bullet_lower for term in ['managed', 'led', 'supervised', 'directed']):
                        bullet = bullet.rstrip('.') + ', mentoring team members'
        
        # FALLBACK 3: Any bullet with collaboration + SME priority
        if any(term in bullet_lower for term in ['worked', 'collaborated', 'partnered', 'coordinated']):
            if any(kw in priority_keywords for kw in ['subject matter experts', 'sme', 'stakeholder']):
                if 'subject matter' not in bullet_lower and 'sme' not in bullet_lower:
                    # Add SME context
                    if 'with' in bullet_lower:
                        bullet = bullet.replace(' with ', ' with subject matter experts and ', 1)
        
        # FALLBACK 4: Any bullet with process/workflow + quality priority
        if any(term in bullet_lower for term in ['process', 'workflow', 'procedure', 'system']):
            if any(kw in priority_keywords for kw in ['quality', 'consistency', 'standards']):
                if not any(term in bullet_lower for term in ['quality', 'consistency', 'standard', 'governance']):
                    bullet = bullet.rstrip('.') + ', ensuring consistency and quality standards'
        
        # FALLBACK 5: Any bullet with validation/verification + reviewing priority
        if any(term in bullet_lower for term in ['validated', 'verified', 'tested', 'checked']):
            if 'reviewing' in priority_keywords or 'quality' in priority_keywords:
                if 'review' not in bullet_lower and 'quality' not in bullet_lower:
                    bullet = bullet.rstrip('.') + ', reviewing for accuracy and quality'
        
        return bullet
    
    def _inject_missing_skills(self, bullet: str, missing_skills: List[str], priority_keywords: List[str]) -> str:
        """
        AGGRESSIVELY inject missing skills into bullets to improve ATS score.
        
        This is the KEY to improving ATS scores - we must add the missing keywords!
        """
        bullet_lower = bullet.lower()
        
        # Filter missing skills to only inject relevant ones
        relevant_missing = []
        for skill in missing_skills[:10]:  # Top 10 missing skills
            skill_lower = skill.lower()
            
            # Skip if already in bullet
            if skill_lower in bullet_lower:
                continue
            
            # Only inject if relevant to bullet context
            if any(term in bullet_lower for term in ['documentation', 'content', 'writing', 'technical']):
                if any(kw in skill_lower for kw in ['writing', 'documentation', 'content', 'editing', 'reviewing', 'quality', 'accuracy']):
                    relevant_missing.append(skill)
            
            if any(term in bullet_lower for term in ['team', 'managed', 'led', 'supervised']):
                if any(kw in skill_lower for kw in ['mentoring', 'coaching', 'training', 'leadership']):
                    relevant_missing.append(skill)
            
            if any(term in bullet_lower for term in ['collaborated', 'worked with', 'partnered']):
                if any(kw in skill_lower for kw in ['stakeholder', 'sme', 'subject matter', 'cross-functional']):
                    relevant_missing.append(skill)
        
        # Inject up to 3 relevant missing skills
        if relevant_missing:
            skills_to_add = relevant_missing[:3]
            skills_phrase = ', '.join(skills_to_add)
            
            # Add at the end naturally
            bullet = bullet.rstrip('.') + f', including {skills_phrase}'
            print(f"         💡 Injected missing skills: {skills_phrase}")
        
        return bullet
