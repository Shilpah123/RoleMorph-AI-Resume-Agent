"""
Bullet Optimizer Agent - Rewrites experience bullets with Action + Impact + Technology.
"""

import re
from typing import Dict, List, Set


class BulletOptimizerAgent:
    """Optimizes experience bullets using proven formulas."""
    
    def __init__(self):
        # Multiple verb options for variation
        self.action_verb_options = {
            'led': ['Led', 'Spearheaded', 'Directed', 'Guided'],
            'managed': ['Managed', 'Oversaw', 'Coordinated', 'Supervised'],
            'created': ['Created', 'Developed', 'Established', 'Built'],
            'made': ['Established', 'Created', 'Developed'],
            'did': ['Executed', 'Performed', 'Completed', 'Delivered'],
            'worked': ['Collaborated', 'Partnered', 'Worked'],
            'helped': ['Facilitated', 'Supported', 'Assisted', 'Enabled'],
            'improved': ['Improved', 'Enhanced', 'Optimized', 'Strengthened'],
            'changed': ['Transformed', 'Revised', 'Updated', 'Modified'],
            'built': ['Built', 'Developed', 'Created', 'Constructed'],
            'wrote': ['Authored', 'Wrote', 'Developed', 'Created'],
            'handled': ['Managed', 'Handled', 'Oversaw'],
            'implemented': ['Implemented', 'Deployed', 'Launched', 'Rolled out'],
            'designed': ['Designed', 'Developed', 'Created', 'Architected']
        }
        
        self.used_phrases = set()
        self.used_verbs = {}  # Track verb usage for variation
    
    def optimize(self, bullet: str, job_analysis: Dict, gap_analysis: Dict) -> str:
        """
        Optimize a bullet using: Action + What + How + Impact
        
        Note: KeywordSurfacer has already done aggressive transformations.
        This should only do light touch-ups.
        
        Formula:
        [Strong Action Verb] + [What you did] + [Technology/Method] + [Business Impact]
        """
        # Clean bullet
        bullet = bullet.strip()
        if not bullet:
            return bullet
        
        # Remove bullet markers
        bullet = re.sub(r'^[•\-\*\◦]\s*', '', bullet)
        
        # If bullet is already well-structured or has been enhanced, don't rewrite
        # Just return as-is to preserve keyword surfacing
        if self._is_well_structured(bullet) or len(bullet.split(',')) >= 3:
            return bullet
        
        # Only rewrite if bullet is truly weak
        if len(bullet.split()) < 8:
            return self._rewrite_bullet(bullet, job_analysis, gap_analysis)
        
        return bullet
    
    def _is_well_structured(self, bullet: str) -> bool:
        """Check if bullet already has good structure."""
        # Good bullets typically have:
        # - Strong action verb at start
        # - Reasonable length (20-150 words)
        # - Some specificity
        
        words = bullet.split()
        if len(words) < 5 or len(words) > 40:
            return False
        
        # Check for strong action verb
        first_word = words[0].lower().rstrip('.,;:')
        strong_verbs = ['spearheaded', 'directed', 'developed', 'established', 'executed',
                       'facilitated', 'enhanced', 'transformed', 'architected', 'authored',
                       'deployed', 'engineered', 'optimized', 'streamlined', 'delivered']
        
        if first_word in strong_verbs:
            return True
        
        return False
    
    def _rewrite_bullet(self, bullet: str, job_analysis: Dict, gap_analysis: Dict) -> str:
        """Rewrite bullet using Action + What + How + Impact formula."""
        
        # Extract key elements from original bullet
        original_lower = bullet.lower()
        
        # Determine action verb
        action_verb = self._get_action_verb(bullet)
        
        # Determine what was done
        what = self._extract_what(bullet)
        
        # Add technology/method if relevant
        how = self._add_technology(original_lower, job_analysis)
        
        # Add business impact
        impact = self._add_impact(original_lower, job_analysis)
        
        # Combine components
        components = [action_verb, what]
        if how:
            components.append(how)
        if impact:
            components.append(impact)
        
        return " ".join(components).strip()
    
    def _get_action_verb(self, bullet: str) -> str:
        """Get strong action verb for bullet with variation."""
        words = bullet.split()
        if not words:
            return "Executed"
        
        first_word = words[0].lower().rstrip('.,;:')
        
        # Check if we have options for this verb
        if first_word in self.action_verb_options:
            options = self.action_verb_options[first_word]
            
            # Track usage and rotate through options
            if first_word not in self.used_verbs:
                self.used_verbs[first_word] = 0
            
            # Get next option in rotation
            idx = self.used_verbs[first_word] % len(options)
            selected_verb = options[idx]
            self.used_verbs[first_word] += 1
            
            return selected_verb
        
        # Use first word if it's already strong
        strong_verbs = ['led', 'managed', 'created', 'developed', 'implemented', 
                       'designed', 'built', 'established', 'drove', 'delivered']
        
        if first_word in strong_verbs:
            return first_word.capitalize()
        
        return "Executed"
    
    def _extract_what(self, bullet: str) -> str:
        """Extract the core 'what' from bullet."""
        # Remove first word (verb) and clean up
        words = bullet.split()[1:]
        what = " ".join(words)
        
        # Clean up
        what = re.sub(r'\s+', ' ', what).strip()
        
        # Limit length
        if len(what.split()) > 15:
            what = " ".join(what.split()[:15])
        
        return what
    
    def _add_technology(self, bullet_lower: str, job_analysis: Dict) -> str:
        """Add technology/method if relevant and not already present."""
        tools = job_analysis.get('tools', [])
        strong_match = job_analysis.get('strong_match', [])
        
        # Check if bullet already mentions technology
        has_tech = any(tool.lower() in bullet_lower for tool in tools)
        
        if has_tech:
            return ""
        
        # Add relevant technology if it's in strong match
        for tool in tools:
            if tool in strong_match:
                phrases = [
                    f"leveraging {tool}",
                    f"utilizing {tool}",
                    f"implementing {tool}-based solutions"
                ]
                
                for phrase in phrases:
                    if phrase not in self.used_phrases:
                        self.used_phrases.add(phrase)
                        return phrase
        
        return ""
    
    def _add_impact(self, bullet_lower: str, job_analysis: Dict) -> str:
        """Add business impact if not already present."""
        
        # Check if bullet already has impact/results
        impact_indicators = ['reducing', 'improving', 'increasing', 'accelerating',
                           'enhancing', 'streamlining', 'optimizing', '%', 'x']
        
        has_impact = any(indicator in bullet_lower for indicator in impact_indicators)
        
        if has_impact:
            return ""
        
        # Add generic but relevant impact based on job type
        leadership_req = job_analysis.get('leadership_requirements', [])
        
        impact_phrases = []
        
        if leadership_req:
            impact_phrases = [
                "improving team efficiency and delivery timelines",
                "enhancing cross-functional collaboration and stakeholder alignment",
                "driving operational excellence and process standardization"
            ]
        else:
            impact_phrases = [
                "improving operational efficiency and reducing manual effort",
                "enhancing user experience and content accessibility",
                "streamlining workflows and accelerating delivery timelines",
                "ensuring quality and consistency across deliverables"
            ]
        
        # Return first unused phrase
        for phrase in impact_phrases:
            if phrase not in self.used_phrases:
                self.used_phrases.add(phrase)
                return phrase
        
        return ""
    
    def _add_keywords_if_relevant(self, bullet: str, job_analysis: Dict, gap_analysis: Dict) -> str:
        """Add keywords to already well-structured bullet if relevant."""
        
        bullet_lower = bullet.lower()
        strong_match = gap_analysis.get('strong_match', [])
        
        # Find relevant keywords not in bullet
        missing_keywords = [skill for skill in strong_match if skill.lower() not in bullet_lower]
        
        if not missing_keywords:
            return bullet
        
        # Add one relevant keyword naturally
        keyword = missing_keywords[0]
        
        # Check if keyword is contextually relevant to this bullet
        if self._is_keyword_relevant(bullet_lower, keyword.lower()):
            # Add keyword naturally
            if ',' in bullet:
                # Add after first clause
                parts = bullet.split(',', 1)
                return f"{parts[0]} leveraging {keyword},{parts[1]}"
            else:
                # Add at end
                return f"{bullet.rstrip('.')} utilizing {keyword}."
        
        return bullet
    
    def _is_keyword_relevant(self, bullet: str, keyword: str) -> bool:
        """Check if keyword is contextually relevant to bullet."""
        
        relevance_map = {
            'python': ['automat', 'script', 'tool', 'data', 'process'],
            'ai': ['automat', 'intelligent', 'smart', 'transform'],
            'agile': ['team', 'sprint', 'iterative', 'deliver'],
            'documentation': ['content', 'write', 'document', 'manual'],
            'leadership': ['team', 'lead', 'manage', 'direct']
        }
        
        context_words = relevance_map.get(keyword, [])
        
        return any(word in bullet for word in context_words)
