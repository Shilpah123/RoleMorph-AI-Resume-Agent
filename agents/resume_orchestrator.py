"""
Resume Orchestrator - Coordinates all agents for resume optimization.
"""

from typing import Dict, List
from .job_analysis_agent import JobAnalysisAgent
from .gap_analysis_agent import GapAnalysisAgent
from .summary_rewriter_agent import SummaryRewriterAgent
from .bullet_optimizer_agent import BulletOptimizerAgent
from .ats_scoring_agent import ATSScoringAgent
from .summary_quality_scorer import SummaryQualityScorer
from .transferable_skills_mapper import TransferableSkillsMapper
from .keyword_surfacer import KeywordSurfacer


class ResumeOrchestrator:
    """
    Orchestrates multiple agents to optimize resume.
    
    Agent Pipeline:
    1. JobAnalysisAgent - Analyzes job description
    2. GapAnalysisAgent - Identifies skill gaps
    3. SummaryRewriterAgent - Rewrites professional summary
    4. BulletOptimizerAgent - Optimizes experience bullets
    5. ATSScoringAgent - Calculates ATS score
    """
    
    def __init__(self):
        self.job_analyzer = JobAnalysisAgent()
        self.gap_analyzer = GapAnalysisAgent()
        self.summary_rewriter = SummaryRewriterAgent()
        self.bullet_optimizer = BulletOptimizerAgent()
        self.ats_scorer = ATSScoringAgent()
        self.quality_scorer = SummaryQualityScorer()
        self.skills_mapper = TransferableSkillsMapper()
        self.keyword_surfacer = KeywordSurfacer()
    
    def analyze_and_optimize(self, resume_text: str, job_desc: str) -> Dict:
        """
        Run complete analysis and optimization pipeline.
        
        Returns:
            {
                'job_analysis': Dict,
                'gap_analysis': Dict,
                'new_summary': str,
                'ats_score': Dict,
                'recommendations': List[str]
            }
        """
        print("\n🔍 Step 1: Analyzing job description...")
        job_analysis = self.job_analyzer.analyze(job_desc)
        
        print("🔍 Step 2: Identifying job priorities...")
        priority_keywords = self.keyword_surfacer.identify_job_priorities(job_desc, job_analysis)
        print(f"  ✓ Top priorities: {', '.join(priority_keywords[:5])}")
        
        print("🔍 Step 3: Analyzing skill gaps...")
        gap_analysis = self.gap_analyzer.analyze(resume_text, job_analysis)
        
        print("✍️ Step 4: Generating new professional summary...")
        # Extract years, background, and original summary from resume
        years = self._extract_years(resume_text)
        background = self._extract_background(resume_text)
        original_summary = self._extract_original_summary(resume_text)
        
        # Check for domain mismatch
        domain_analysis = self.skills_mapper.detect_domain_mismatch(resume_text, job_analysis)
        
        # DEBUG: Show domain detection results
        print(f"\n  🔍 DOMAIN DETECTION:")
        print(f"     Resume Domain: {domain_analysis['resume_domain']}")
        print(f"     Job Domain: {domain_analysis['job_domain']}")
        print(f"     Has Mismatch: {domain_analysis['has_mismatch']}")
        print(f"     Transferable Skills: {len(domain_analysis['transferable_skills'])} found")
        
        # Generate new summary
        if domain_analysis['has_mismatch'] and domain_analysis['transferable_skills']:
            # Use transferable skills approach
            print(f"\n  ⚠ Domain mismatch detected: {domain_analysis['resume_domain']} → {domain_analysis['job_domain']}")
            print(f"  ✓ Using transferable skills approach")
            new_summary = self.skills_mapper.enhance_summary_with_transferable_skills(
                original_summary or "",
                domain_analysis['transferable_skills'],
                years,
                job_domain=domain_analysis['job_domain'],
                resume_text=resume_text,
                job_requirements=job_analysis.get('required_skills', [])
            )
            # For domain mismatch, always use transferable skills summary - it's more relevant
            print(f"  ✓ Using transferable skills summary (domain-specific)")
            print(f"\n  📝 GENERATED SUMMARY (first 150 chars):")
            print(f"     {new_summary[:150]}...")
        else:
            # Use standard rewriter
            print(f"\n  ℹ No domain mismatch - using standard rewriter")
            new_summary = self.summary_rewriter.rewrite(
                years_experience=years,
                current_background=background,
                job_analysis=job_analysis,
                gap_analysis=gap_analysis,
                original_summary=original_summary,
                resume_text=resume_text
            )
            
            # Quality check - preserve original if it's better (only for same-domain rewrites)
            if original_summary:
                should_preserve = self.quality_scorer.should_preserve_original(
                    original_summary,
                    new_summary,
                    job_desc,
                    threshold=10
                )
                
                if should_preserve:
                    print(f"  ✓ Original summary scores higher - preserving it")
                    new_summary = original_summary
                else:
                    print(f"  ✓ New summary approved")
            
            print(f"\n  📝 FINAL SUMMARY (first 150 chars):")
            print(f"     {new_summary[:150]}...")
        
        print("📊 Step 5: Calculating ATS score...")
        ats_score = self.ats_scorer.calculate_score(
            resume_text,
            job_analysis,
            gap_analysis
        )
        
        print("💡 Step 6: Generating recommendations...")
        recommendations = self._generate_recommendations(
            job_analysis,
            gap_analysis,
            ats_score
        )
        
        # Title optimization removed - not needed for this use case
        optimized_title = None
        
        return {
            'job_analysis': job_analysis,
            'gap_analysis': gap_analysis,
            'new_summary': new_summary,
            'ats_score': ats_score,
            'recommendations': recommendations,
            'priority_keywords': priority_keywords,
            'optimized_title': optimized_title
        }
    
    def optimize_bullet(self, bullet: str, job_analysis: Dict, gap_analysis: Dict, 
                       priority_keywords: List = None) -> str:
        """Optimize a single bullet point with keyword surfacing and missing skills injection."""
        original_bullet = bullet
        
        # Extract missing skills from gap analysis
        missing_skills = gap_analysis.get('missing_skills', [])
        
        # First surface relevant keywords AND inject missing skills
        if priority_keywords:
            bullet = self.keyword_surfacer.enhance_bullet_with_surfacing(
                bullet, 
                priority_keywords,
                missing_skills=missing_skills  # CRITICAL: Pass missing skills to improve ATS
            )
            if bullet != original_bullet:
                print(f"      🔍 Keyword surfacing changed bullet")
        else:
            print(f"      ⚠ No priority keywords provided for bullet")
        
        # Then optimize with bullet optimizer
        optimized = self.bullet_optimizer.optimize(bullet, job_analysis, gap_analysis)
        
        if optimized != original_bullet:
            print(f"      ✓ Bullet transformed")
        else:
            print(f"      ℹ Bullet unchanged")
        
        return optimized
    
    def _extract_years(self, resume_text: str) -> int:
        """Extract years of experience from resume."""
        import re
        years_match = re.search(r'(\d+)\+?\s*years', resume_text.lower())
        if years_match:
            return int(years_match.group(1))
        return 15  # Default
    
    def _extract_background(self, resume_text: str) -> str:
        """Extract professional background from resume."""
        resume_lower = resume_text.lower()
        
        if 'technical writ' in resume_lower or 'technical commun' in resume_lower:
            return "Technical Communication Professional"
        elif 'content' in resume_lower and 'develop' in resume_lower:
            return "Content Development Professional"
        elif 'engineer' in resume_lower:
            return "Engineering Professional"
        elif 'manager' in resume_lower or 'director' in resume_lower:
            return "Leadership Professional"
        else:
            return "Professional"
    
    def _extract_original_summary(self, resume_text: str) -> str:
        """Extract original professional summary from resume."""
        lines = resume_text.split('\n')
        
        # Look for summary section
        in_summary = False
        summary_lines = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Detect summary section start
            if any(header in line_lower for header in ['professional summary', 'summary', 'profile', 'objective']):
                in_summary = True
                continue
            
            # Detect section end
            if in_summary and any(header in line_lower for header in ['experience', 'education', 'skills', 'key']):
                break
            
            # Collect summary lines
            if in_summary and line.strip() and len(line.strip()) > 20:
                summary_lines.append(line.strip())
        
        return ' '.join(summary_lines) if summary_lines else None
    
    def _generate_recommendations(self, job_analysis: Dict, gap_analysis: Dict, 
                                  ats_score: Dict) -> list:
        """Generate actionable recommendations."""
        recommendations = []
        
        overall_score = ats_score.get('overall_score', 0)
        missing_skills = gap_analysis.get('missing_skills', [])
        required_skills = job_analysis.get('required_skills', [])
        
        # Score-based recommendations
        if overall_score >= 80:
            recommendations.append("✓ Excellent match! Your resume has been optimized to highlight relevant experience.")
        elif overall_score >= 60:
            recommendations.append("✓ Good match! Resume customized to emphasize transferable skills.")
        else:
            recommendations.append("⚠ Moderate match. Consider highlighting additional relevant experience.")
        
        # Missing critical skills
        critical_missing = [s for s in missing_skills if s in required_skills]
        if critical_missing:
            recommendations.append(f"⚠ Missing required skills: {', '.join(critical_missing[:3])}")
        
        # Keyword optimization
        keyword_score = ats_score.get('keyword_match', 0)
        if keyword_score < 70:
            recommendations.append("💡 Add more relevant keywords from job description to improve ATS score.")
        
        # Experience gap
        experience_score = ats_score.get('experience_match', 0)
        if experience_score < 70:
            recommendations.append("💡 Highlight relevant experience that matches the required years.")
        
        return recommendations
    
