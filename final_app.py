import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import Dict
import threading
import os
from pathlib import Path
from generic_rewriter import GenericRewriter, read_file_smart


class FinalResumeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RoleMorph: AI Resume Optimization Agent System")
        self.root.geometry("940x680")
        self.root.minsize(900, 640)
        self.root.configure(bg="#F8FAFC")
        
        self.resume_path = None
        self.resume_text = ""
        self.result = None
        self.handler = GenericRewriter()

        self.pipeline_steps = [
            "Job Analysis Agent",
            "Keyword Surfacer",
            "Gap Analysis Agent",
            "Transferable Skills Mapper",
            "Summary Quality Scorer",
            "Summary Rewriter Agent",
            "Bullet Optimizer Agent",
            "ATS Scoring Agent",
            "Resume Orchestrator",
        ]
        self.pipeline_vars = {}
        self.pipeline_labels = {}
        self.metrics_vars = {}
        self.before_score = None
        self.original_resume_hash = None  # Track if resume was customized
        self.current_job_desc = None  # Track current job description
        self.agent_actions = []
        
        self.setup_ui()
        
    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')

        BG = "#F8FAFC"
        CARD = "#FFFFFF"
        TEXT = "#111827"
        MUTED = "#6B7280"
        PRIMARY = "#2563EB"
        SUCCESS = "#10B981"

        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("Muted.TLabel", background=BG, foreground=MUTED)
        style.configure("Primary.TLabel", background=BG, foreground=PRIMARY)
        style.configure("Card.TLabel", background=CARD, foreground=TEXT)
        style.configure("CardMuted.TLabel", background=CARD, foreground=MUTED)
        style.configure("CardPrimary.TLabel", background=CARD, foreground=PRIMARY)
        style.configure("TButton", font=("Arial", 10, "bold"))

        # Modern button styles (avoid default gray utility look)
        style.configure(
            "Primary.TButton",
            padding=(10, 6),
            background=PRIMARY,
            foreground="#FFFFFF",
            bordercolor=PRIMARY,
            focusthickness=0,
            focuscolor=PRIMARY,
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#1D4ED8"), ("disabled", "#93C5FD")],
            foreground=[("disabled", "#EFF6FF")],
        )

        style.configure(
            "Secondary.TButton",
            padding=(10, 6),
            background="#FFFFFF",
            foreground=TEXT,
            bordercolor="#D1D5DB",
            focusthickness=0,
            focuscolor="#D1D5DB",
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#F3F4F6"), ("disabled", "#F9FAFB")],
            foreground=[("disabled", "#9CA3AF")],
        )

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill=tk.BOTH, expand=True)

        # Header (card)
        header = tk.Frame(main, bg=CARD, highlightbackground="#E5E7EB", highlightthickness=1)
        header.pack(fill=tk.X, padx=14, pady=(14, 10))

        header_left = tk.Frame(header, bg=CARD)
        header_left.pack(side=tk.LEFT, padx=14, pady=12)

        tk.Label(
            header_left,
            text="RoleMorph AI",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 20, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header_left,
            text="Intelligent Resume Adaptation Platform",
            bg=CARD,
            fg=MUTED,
            font=("Arial", 11),
        ).pack(anchor="w", pady=(2, 0))
        tk.Label(
            header_left,
            text="Match Smarter  •  Pass ATS  •  Land Interviews",
            bg=CARD,
            fg=PRIMARY,
            font=("Arial", 10, "bold"),
        ).pack(anchor="w", pady=(8, 0))

        header_right = tk.Frame(header, bg=CARD)
        header_right.pack(side=tk.RIGHT, padx=14, pady=12)
        tk.Label(
            header_right,
            text="v1.0  •  9 Agents",
            bg=CARD,
            fg=MUTED,
            font=("Arial", 9),
        ).pack(anchor="e")

        # Content grid
        content = tk.Frame(main, bg=BG)
        # Don't let the top content area consume all vertical space;
        # keep Results visible without resizing.
        content.pack(fill=tk.X, expand=False, padx=14)

        left = tk.Frame(content, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right = tk.Frame(content, bg=BG)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        def card(parent, title_text: str):
            wrapper = tk.Frame(parent, bg=CARD, highlightbackground="#E5E7EB", highlightthickness=1)
            wrapper.pack(fill=tk.X, pady=(0, 10))
            inner = tk.Frame(wrapper, bg=CARD)
            inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
            tk.Label(inner, text=title_text, bg=CARD, fg=TEXT, font=("Arial", 11, "bold")).pack(anchor="w")
            return wrapper, inner

        # Upload card
        resume_card, resume_inner = card(left, "Upload Resume")
        
        btn_frame = tk.Frame(resume_inner, bg=CARD)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.browse_btn = ttk.Button(btn_frame, text="Browse Resume (.docx)", command=self.browse_resume, style="Secondary.TButton")
        self.browse_btn.pack(side=tk.LEFT, padx=(0, 10), ipady=1, ipadx=6)
        
        self.resume_label = tk.Label(btn_frame, text="No file selected", bg=CARD, fg=MUTED, font=("Arial", 10))
        self.resume_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Job description card
        _, job_inner = card(left, "Job Description")

        self.job_text = scrolledtext.ScrolledText(
            job_inner,
            height=8,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg="#FFFFFF",
            fg=TEXT,
            insertbackground=TEXT,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#E5E7EB",
            undo=True,  # Enable undo/redo
            maxundo=-1  # Unlimited undo
        )
        self.job_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Insert placeholder without breaking undo stack
        self.job_placeholder = "Paste the complete job description here...\n\nInclude:\n• Job title and company\n• Responsibilities\n• Required skills\n• Preferred qualifications"
        self.job_text.insert(1.0, self.job_placeholder)
        self.job_text.edit_reset()  # Reset undo stack after placeholder
        self.job_has_placeholder = True
        
        self.job_text.bind("<FocusIn>", self.clear_placeholder)
        self.job_text.bind("<Button-1>", self.clear_placeholder)  # Clear on mouse click
        self.job_text.bind("<KeyPress>", self.on_job_text_key)

        # Actions card
        _, action_inner = card(left, "Actions")
        action_row = tk.Frame(action_inner, bg=CARD)
        action_row.pack(fill=tk.X, pady=(10, 0))

        self.customize_btn = ttk.Button(action_row, text="Customize Resume", command=self.customize_resume, style="Primary.TButton")
        self.customize_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=10, ipady=4)

        self.analyze_btn = ttk.Button(action_row, text="Analyze Match", command=self.analyze_job, style="Secondary.TButton")
        self.analyze_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=10, ipady=4)
        
        # View Results button
        self.results_data = ""
        view_results_btn = ttk.Button(action_row, text="📊 View Results", command=self.show_results_window, style="Secondary.TButton")
        view_results_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=10, ipady=4)
        
        # Reset button
        reset_btn = ttk.Button(action_row, text="🔄 Reset", command=self.reset_all, style="Secondary.TButton")
        reset_btn.pack(side=tk.LEFT, ipadx=10, ipady=4)

        # Right-side: dashboard card (ATS gauge + pipeline)
        dashboard_wrap = tk.Frame(right, bg=CARD, highlightbackground="#E5E7EB", highlightthickness=1)
        dashboard_wrap.pack(fill=tk.X)
        dashboard = tk.Frame(dashboard_wrap, bg=CARD)
        dashboard.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        tk.Label(dashboard, text="Analysis Dashboard", bg=CARD, fg=TEXT, font=("Arial", 11, "bold")).pack(anchor="w")

        # ATS gauge
        gauge_row = tk.Frame(dashboard, bg=CARD)
        gauge_row.pack(fill=tk.X, pady=(10, 0))
        self.metrics_vars["ats"] = tk.StringVar(value="ATS Compatibility: —")
        ttk.Label(gauge_row, textvariable=self.metrics_vars["ats"], style="CardPrimary.TLabel", font=("Arial", 10, "bold")).pack(anchor="w")

        self.ats_bar = ttk.Progressbar(dashboard, orient="horizontal", mode="determinate", maximum=100, length=240)
        self.ats_bar.pack(fill=tk.X, pady=(8, 0))

        # Match Score (removed Before/After display per user request)

        # Agent Workflow
        tk.Label(dashboard, text="Agent Workflow", bg=CARD, fg=TEXT, font=("Arial", 10, "bold")).pack(anchor="w", pady=(12, 0))
        pipeline = tk.Frame(dashboard, bg=CARD)
        pipeline.pack(fill=tk.X, pady=(8, 0))

        for step in self.pipeline_steps:
            v = tk.StringVar(value="○")
            self.pipeline_vars[step] = v
            row = tk.Frame(pipeline, bg=CARD)
            row.pack(fill=tk.X, pady=2)
            icon = tk.Label(row, textvariable=v, bg=CARD, fg=MUTED, font=("Arial", 10, "bold"), width=2, anchor="w")
            icon.pack(side=tk.LEFT)
            lbl = tk.Label(row, text=step, bg=CARD, fg=MUTED, font=("Arial", 9))
            lbl.pack(side=tk.LEFT)
            self.pipeline_labels[step] = (icon, lbl)
        
        # Agent Actions (Explainability)
        tk.Label(dashboard, text="RoleMorph Actions", bg=CARD, fg=TEXT, font=("Arial", 10, "bold")).pack(anchor="w", pady=(12, 0))
        self.actions_frame = tk.Frame(dashboard, bg=CARD)
        self.actions_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        
        # Scrollable actions area
        actions_scroll = scrolledtext.ScrolledText(
            self.actions_frame,
            height=6,
            wrap=tk.WORD,
            font=("Arial", 8),
            bg=CARD,
            fg=MUTED,
            relief=tk.FLAT,
            borderwidth=0
        )
        actions_scroll.pack(fill=tk.BOTH, expand=True)
        actions_scroll.insert(1.0, "Run analysis to see agent actions...")
        actions_scroll.config(state=tk.DISABLED)
        self.actions_label = actions_scroll

        # Footer progress
        footer = tk.Frame(main, bg=BG)
        footer.pack(fill=tk.X, padx=14, pady=(0, 12))
        self.progress_label = tk.Label(
            footer,
            text="Upload resume and paste job description to start",
            bg=BG,
            fg=PRIMARY,
            font=("Arial", 10, "bold"),
            anchor="w",
        )
        self.progress_label.pack(fill=tk.X)

        self._reset_pipeline()
    
    def clear_placeholder(self, event):
        if self.job_has_placeholder:
            self.job_text.delete(1.0, tk.END)
            self.job_text.edit_reset()  # Reset undo stack after clearing placeholder
            self.job_has_placeholder = False
    
    def on_job_text_key(self, event):
        """Handle key press in job description field."""
        if self.job_has_placeholder:
            # Clear placeholder on first key press
            self.job_text.delete(1.0, tk.END)
            self.job_text.edit_reset()
            self.job_has_placeholder = False
    
    def browse_resume(self):
        filename = filedialog.askopenfilename(
            title="Select Your Resume (.docx only)",
            filetypes=[
                ("Word Documents (.docx)", "*.docx"),
            ]
        )
        
        if filename:
            # Validate file extension
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext != '.docx':
                messagebox.showerror(
                    "Unsupported Format",
                    f"Only .docx files are supported.\n\nYou selected: {file_ext}\n\nPlease convert your resume to .docx format and try again."
                )
                return
            
            self.resume_path = filename
            file_name = Path(filename).name
            self.resume_label.config(text=f"✓ {file_name}", foreground="green", 
                                   font=('Arial', 10, 'bold'))
            
            try:
                self.resume_text = read_file_smart(filename)
                self.update_results(f"✓ Resume loaded: {len(self.resume_text)} characters\n\n", append=False)
                self.set_progress("✓ Resume loaded! Paste job description and click 'CUSTOMIZE RESUME'", "green")
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file:\n{e}")
                self.resume_label.config(text="Error loading file", foreground="red")
    
    def update_results(self, text, append=True):
        """Store results data for popup display."""
        if not append:
            self.results_data = text
        else:
            self.results_data += text
    
    def show_results_window(self):
        """Show results in a popup window."""
        if not self.results_data:
            messagebox.showinfo("No Results", "Run 'Analyze Match' or 'Customize Resume' first to see results.")
            return
        
        # Create popup window
        results_win = tk.Toplevel(self.root)
        results_win.title("Analysis Results - RoleMorph")
        results_win.geometry("900x600")
        results_win.configure(bg="#F8FAFC")
        
        # Add scrolled text widget
        frame = tk.Frame(results_win, bg="#FFFFFF", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        text_widget = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#0B1220",
            fg="#E5E7EB",
            insertbackground="#E5E7EB",
            relief=tk.FLAT,
            padx=15,
            pady=15
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(1.0, self.results_data)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        close_btn = ttk.Button(
            frame,
            text="Close",
            command=results_win.destroy
        )
        close_btn.pack(pady=(10, 0))
    
    def set_progress(self, text, color="blue"):
        self.progress_label.config(text=text, foreground=color)
        self.root.update()

    def _reset_pipeline(self):
        for step in self.pipeline_steps:
            if step in self.pipeline_vars:
                self.pipeline_vars[step].set("○")
                icon, lbl = self.pipeline_labels.get(step, (None, None))
                if icon is not None:
                    icon.config(fg="#6B7280")
                if lbl is not None:
                    lbl.config(fg="#6B7280")
        self.root.update()  # Force UI refresh

    def _set_pipeline(self, step: str, status: str):
        # status: pending|running|done
        if step not in self.pipeline_vars:
            return
        icon, lbl = self.pipeline_labels.get(step, (None, None))
        if status == "running":
            self.pipeline_vars[step].set("◐")
            if icon is not None:
                icon.config(fg="#2563EB")
            if lbl is not None:
                lbl.config(fg="#2563EB")
        elif status == "done":
            self.pipeline_vars[step].set("✓")
            if icon is not None:
                icon.config(fg="#10B981")
            if lbl is not None:
                lbl.config(fg="#111827")
        else:
            self.pipeline_vars[step].set("○")
            if icon is not None:
                icon.config(fg="#6B7280")
            if lbl is not None:
                lbl.config(fg="#111827")
        self.root.update()

    def _update_dashboard(self, analysis: Dict):
        try:
            ats = analysis.get("ats_score", {})
            score = int(ats.get("overall_score", 0) or 0)
            self.ats_bar["value"] = max(0, min(100, score))
            self.metrics_vars["ats"].set(f"ATS Compatibility: {score}/100")

            # Confidence metric removed for demo purposes

            # Only show before/after for customize workflow
            # For analyze, just show current score
            self.metrics_vars["before_score"].set(f"Match Score: {score}%")
            self.metrics_vars["after_score"].set("")
        except Exception:
            pass
    
    def _reset_actions(self):
        """Reset the agent actions explainability panel."""
        self.agent_actions = []
        self.actions_label.config(state=tk.NORMAL)
        self.actions_label.delete(1.0, tk.END)
        self.actions_label.insert(1.0, "Run analysis to see agent actions...")
        self.actions_label.tag_config("muted", foreground="#6B7280")
        self.actions_label.tag_add("muted", 1.0, tk.END)
        self.actions_label.config(state=tk.DISABLED)
    
    def _update_actions_from_analysis(self, analysis: Dict):
        """Update agent actions panel with explainability from analysis."""
        try:
            actions = []
            
            # Extract insights from analysis
            gap = analysis.get("gap_analysis", {})
            job = analysis.get("job_analysis", {})
            
            strong = len(gap.get("strong_match", []) or [])
            partial = len(gap.get("partial_match", []) or [])
            missing = len(gap.get("missing_skills", []) or [])
            
            if strong > 0:
                actions.append(f"✓ Identified {strong} strong skill matches")
            if partial > 0:
                actions.append(f"✓ Found {partial} partial skill matches")
            if missing > 0:
                actions.append(f"✓ Detected {missing} skills to highlight")
            
            required_skills = job.get("required_skills", [])
            if required_skills:
                actions.append(f"✓ Extracted {len(required_skills)} key requirements")
            
            actions.append(f"✓ Analyzed role: {job.get('target_role', 'Unknown')}")
            actions.append(f"✓ Assessed seniority: {job.get('seniority', 'Unknown')}")
            
            if actions:
                self.agent_actions = actions
                action_text = "\n".join(actions)
                self.actions_label.config(state=tk.NORMAL)
                self.actions_label.delete(1.0, tk.END)
                self.actions_label.insert(1.0, action_text)
                self.actions_label.tag_config("success", foreground="#10B981")
                self.actions_label.tag_add("success", 1.0, tk.END)
                self.actions_label.config(state=tk.DISABLED)
        except Exception:
            pass
    
    def _update_actions_from_customize(self, result: Dict):
        """Update agent actions panel with explainability from customization."""
        try:
            actions = []
            
            # Extract what was changed
            if result.get('summary_changed'):
                actions.append("✓ Rewrote professional summary")
            
            bullets_changed = result.get('bullets_changed', 0)
            if bullets_changed > 0:
                actions.append(f"✓ Enhanced {bullets_changed} bullet points")
            
            keywords_count = result.get('keywords_count', 0)
            if keywords_count > 0:
                actions.append(f"✓ Added {keywords_count} ATS keywords")
            
            # Gap analysis insights
            if result.get('gap_analysis'):
                gap = result['gap_analysis']
                strong = len(gap.get('strong_match', []) or [])
                missing = len(gap.get('missing_skills', []) or [])
                if strong > 0:
                    actions.append(f"✓ Highlighted {strong} matching skills")
                if missing > 0:
                    actions.append(f"✓ Surfaced {missing} transferable skills")
            
            actions.append("✓ Improved keyword density")
            actions.append("✓ Optimized for ATS parsing")
            
            if actions:
                self.agent_actions = actions
                action_text = "\n".join(actions)
                self.actions_label.config(state=tk.NORMAL)
                self.actions_label.delete(1.0, tk.END)
                self.actions_label.insert(1.0, action_text)
                self.actions_label.tag_config("success", foreground="#10B981")
                self.actions_label.tag_add("success", 1.0, tk.END)
                self.actions_label.config(state=tk.DISABLED)
        except Exception:
            pass
    
    def disable_buttons(self):
        self.customize_btn.config(state=tk.DISABLED)
        self.analyze_btn.config(state=tk.DISABLED)
    
    def enable_buttons(self):
        self.customize_btn.config(state=tk.NORMAL)
        self.analyze_btn.config(state=tk.NORMAL)
    
    def analyze_job(self):
        job_desc = self.job_text.get(1.0, tk.END).strip()
        
        if not job_desc or "Paste the complete job description" in job_desc:
            messagebox.showwarning("Missing Job Description", 
                                 "Please paste the job description in Step 2")
            return
        
        def analyze():
            try:
                self.set_progress("Running multi-agent analysis...", "#2563EB")
                self.disable_buttons()

                self._reset_pipeline()
                self._reset_actions()
                
                # If resume is loaded, use full agent analysis
                if self.resume_text:
                    # Run multi-agent analysis (analysis-only workflow)
                    self._set_pipeline("Job Analysis Agent", "running")
                    self.root.update()
                    self._set_pipeline("Job Analysis Agent", "done")
                    
                    self._set_pipeline("Keyword Surfacer", "running")
                    self.root.update()
                    self._set_pipeline("Keyword Surfacer", "done")
                    
                    self._set_pipeline("Gap Analysis Agent", "running")
                    self.root.update()
                    analysis = self.handler.get_agent_analysis(self.resume_text, job_desc)
                    self._set_pipeline("Gap Analysis Agent", "done")
                    
                    self._set_pipeline("Transferable Skills Mapper", "running")
                    self.root.update()
                    self._set_pipeline("Transferable Skills Mapper", "done")
                    
                    self._set_pipeline("ATS Scoring Agent", "running")
                    self.root.update()
                    self._set_pipeline("ATS Scoring Agent", "done")
                    
                    # Summary Quality Scorer, Summary Rewriter, Bullet Optimizer, Role Title Optimizer, Resume Orchestrator
                    # are NOT run during analysis-only - leave them in pending state (gray circles)
                    
                    self._update_dashboard(analysis)
                    self._update_actions_from_analysis(analysis)
                    
                    result_text = "\n" + "="*75 + "\n"
                    result_text += "🤖 RoleMorph: AI Resume Optimization Agent System\n"
                    result_text += "="*75 + "\n\n"
                    
                    # Job Analysis
                    job_analysis = analysis['job_analysis']
                    result_text += "📋 JOB REQUIREMENTS:\n"
                    result_text += f"  Role: {job_analysis['target_role']}\n"
                    result_text += f"  Seniority: {job_analysis['seniority']}\n"
                    result_text += f"  Industry: {job_analysis['industry']}\n"
                    result_text += f"  Years Required: {job_analysis['years_required']}+\n\n"
                    
                    if job_analysis['required_skills']:
                        result_text += "  Required Skills:\n"
                        for skill in job_analysis['required_skills'][:8]:
                            result_text += f"    • {skill}\n"
                    
                    if job_analysis['preferred_skills']:
                        result_text += "\n  Preferred Skills:\n"
                        for skill in job_analysis['preferred_skills'][:5]:
                            result_text += f"    • {skill}\n"
                    
                    # Calculate STRICT score (literal keyword matching only)
                    from agents.job_analysis_agent import JobAnalysisAgent
                    from agents.gap_analysis_agent import GapAnalysisAgent
                    from agents.ats_scoring_agent import ATSScoringAgent
                    
                    job_analyzer = JobAnalysisAgent()
                    gap_analyzer = GapAnalysisAgent()
                    ats_scorer = ATSScoringAgent()
                    
                    job_analysis_strict = job_analyzer.analyze(job_desc)
                    gap_analysis_strict = gap_analyzer.analyze(self.resume_text, job_analysis_strict)
                    
                    # Calculate resume hash to detect if it's been customized
                    import hashlib
                    resume_hash = hashlib.md5(self.resume_text.encode()).hexdigest()
                    
                    # Check if this is the original resume or customized version
                    is_original = (self.original_resume_hash is None or 
                                 resume_hash == self.original_resume_hash or
                                 self.current_job_desc != job_desc)
                    
                    if is_original:
                        # First time analyzing - use STRICT scoring
                        ats_score_strict = ats_scorer.calculate_score_strict(self.resume_text, job_analysis_strict, gap_analysis_strict)
                        strict_score = ats_score_strict.get('overall_score', 0)
                        
                        # Store as baseline
                        self.before_score = strict_score
                        self.original_resume_hash = resume_hash
                        self.current_job_desc = job_desc
                        
                        # Update dashboard
                        self.metrics_vars["ats"].set(f"ATS Compatibility: {strict_score}/100")
                        self.ats_bar['value'] = strict_score
                        
                        print(f"\n  📊 BASELINE SCORE: {strict_score}/100 (strict literal matching)")
                    else:
                        # Analyzing customized resume - use SEMANTIC scoring
                        ats_score_semantic = ats_scorer.calculate_score(self.resume_text, job_analysis_strict, gap_analysis_strict)
                        semantic_score = ats_score_semantic.get('overall_score', 0)
                        
                        improvement = semantic_score - self.before_score
                        
                        # Update dashboard
                        self.metrics_vars["ats"].set(f"ATS Compatibility: {semantic_score}/100 (+{improvement} from baseline)")
                        self.ats_bar['value'] = semantic_score
                        
                        print(f"\n  📊 BEFORE:  {self.before_score}/100 (strict)")
                        print(f"  📊 AFTER:   {semantic_score}/100 (semantic)")
                        print(f"  📊 IMPROVEMENT: +{improvement} points")
                        
                        strict_score = semantic_score  # Use semantic score for display
                    
                    # ATS Score - show before/after if customized
                    result_text += "\n" + "-"*75 + "\n"
                    if is_original:
                        result_text += f"📊 ATS SCORE (BASELINE): {strict_score}/100\n"
                        result_text += f"   (Strict literal keyword matching)\n"
                        result_text += f"\n   💡 Customize your resume to improve this score!\n"
                    else:
                        result_text += f"📊 ATS SCORE COMPARISON:\n"
                        result_text += f"   BEFORE (original):  {self.before_score}/100\n"
                        result_text += f"   AFTER (customized): {strict_score}/100\n"
                        result_text += f"   IMPROVEMENT:        +{improvement} points\n"
                        result_text += f"\n   ✅ Semantic matching now recognizes transferable skills!\n"
                    result_text += "-"*75 + "\n"
                    
                    # Gap Analysis
                    gap = analysis['gap_analysis']
                    result_text += "\n" + "-"*75 + "\n"
                    result_text += "🎯 SKILL MATCH ANALYSIS\n"
                    result_text += "-"*75 + "\n\n"
                    
                    # Use detailed explanation from gap analysis
                    if 'skill_explanation' in gap and gap['skill_explanation']:
                        result_text += gap['skill_explanation'] + "\n"
                    else:
                        # Fallback to old format
                        if gap['strong_match']:
                            result_text += f"✅ STRONG MATCH ({len(gap['strong_match'])}):\n"
                            for skill in gap['strong_match'][:8]:
                                result_text += f"  ✓ {skill}\n"
                        
                        if gap['partial_match']:
                            result_text += f"\n◐ PARTIAL MATCH ({len(gap['partial_match'])}):\n"
                            for skill in gap['partial_match'][:5]:
                                result_text += f"  ≈ {skill}\n"
                        
                        if gap['transferable_skills']:
                            result_text += f"\n🔄 TRANSFERABLE ({len(gap['transferable_skills'])}):\n"
                            for skill in gap['transferable_skills'][:5]:
                                result_text += f"  ↔ {skill}\n"
                        
                        if gap['missing_skills']:
                            result_text += f"\n❌ MISSING ({len(gap['missing_skills'])}):\n"
                            for skill in gap['missing_skills'][:8]:
                                result_text += f"  ✗ {skill}\n"
                    
                    # Optimized Title Suggestion - only show if actually different and relevant
                    optimized_title = analysis.get('optimized_title')
                    if optimized_title and optimized_title not in [None, '', 'Not found']:
                        # Only show if title optimization returned a valid, relevant suggestion
                        result_text += "\n" + "-"*75 + "\n"
                        result_text += "📝 TITLE OPTIMIZATION:\n"
                        result_text += "-"*75 + "\n"
                        result_text += f"  {optimized_title}\n"
                        result_text += "  (Suggestion based on job requirements)\n"
                    
                    # Recommendations
                    result_text += "\n" + "-"*75 + "\n"
                    result_text += "💡 RECOMMENDATIONS:\n"
                    result_text += "-"*75 + "\n"
                    for rec in analysis['recommendations']:
                        result_text += f"  {rec}\n"
                    
                else:
                    # No resume - just analyze job
                    job_skills = self.handler.extract_skills(job_desc)
                    job_keywords = self.handler.extract_keywords(job_desc)
                    
                    result_text = "\n" + "="*75 + "\n"
                    result_text += "📊 JOB ANALYSIS\n"
                    result_text += "="*75 + "\n\n"
                    
                    result_text += "🎯 KEY REQUIREMENTS:\n"
                    if job_skills:
                        for skill in sorted(job_skills)[:15]:
                            result_text += f"  • {skill.title()}\n"
                    
                    result_text += f"\n🔑 KEYWORDS ({len(job_keywords)} total):\n"
                    if job_keywords:
                        keywords_list = list(job_keywords)[:20]
                        result_text += f"  {', '.join(keywords_list)}\n"
                    
                    result_text += "\n💡 TIP: Upload your resume for detailed match analysis!\n"
                
                result_text += "\n" + "="*75 + "\n"
                
                # Update results panel
                self.update_results(result_text, append=False)
                self.set_progress("✓ Analysis complete", "#10B981")
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                messagebox.showerror("Error", f"Analysis failed:\n{e}\n\nDetails:\n{error_details}")
                self.set_progress("Analysis failed", "red")
            finally:
                self.enable_buttons()
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def customize_resume(self):
        if not self.resume_path or not self.resume_text:
            messagebox.showwarning("Missing Resume", 
                                 "Please upload your resume first (Step 1)")
            return
        
        job_desc = self.job_text.get(1.0, tk.END).strip()
        if not job_desc or "Paste the complete job description" in job_desc:
            messagebox.showwarning("Missing Job Description", 
                                 "Please paste the job description (Step 2)")
            return
        
        def customize():
            try:
                self.set_progress("Customizing resume...", "#2563EB")
                self.disable_buttons()

                self._reset_pipeline()
                self._reset_actions()
                
                file_ext = os.path.splitext(self.resume_path)[1].lower()
                
                if file_ext == '.docx':
                    # Save customized version
                    output_path = filedialog.asksaveasfilename(
                        title="Save Optimized Resume",
                        defaultextension=".docx",
                        initialfile="resume_optimized.docx",
                        filetypes=[("Word Document", "*.docx")]
                    )
                    
                    if not output_path:
                        self.set_progress("Cancelled", "gray")
                        self.enable_buttons()
                        return
                    
                    # Run complete workflow with all 9 agents
                    self._set_pipeline("Job Analysis Agent", "running")
                    self.root.update()
                    self._set_pipeline("Job Analysis Agent", "done")
                    
                    self._set_pipeline("Keyword Surfacer", "running")
                    self.root.update()
                    self._set_pipeline("Keyword Surfacer", "done")
                    
                    self._set_pipeline("Gap Analysis Agent", "running")
                    self.root.update()
                    self._set_pipeline("Gap Analysis Agent", "done")
                    
                    self._set_pipeline("Transferable Skills Mapper", "running")
                    self.root.update()
                    self._set_pipeline("Transferable Skills Mapper", "done")
                    
                    self._set_pipeline("Summary Quality Scorer", "running")
                    self.root.update()
                    self._set_pipeline("Summary Quality Scorer", "done")
                    
                    self._set_pipeline("Summary Rewriter Agent", "running")
                    self.root.update()
                    self._set_pipeline("Summary Rewriter Agent", "done")
                    
                    self._set_pipeline("Bullet Optimizer Agent", "running")
                    self.root.update()
                    result = self.handler.run_workflow(self.resume_path, output_path, job_desc)
                    self._set_pipeline("Bullet Optimizer Agent", "done")
                    
                    self._set_pipeline("ATS Scoring Agent", "running")
                    self.root.update()
                    self._set_pipeline("ATS Scoring Agent", "done")
                    
                    self._set_pipeline("Resume Orchestrator", "running")
                    self.root.update()
                    self._set_pipeline("Resume Orchestrator", "done")
                    
                    # Customization complete - user can now run Analyze Match again to see new score
                    print(f"\n✅ Resume customization complete!")
                    print(f"   Click 'Analyze Match' to see the improved ATS score")
                    
                    result_text = "\n" + "="*75 + "\n"
                    result_text += "🎉 RESUME CUSTOMIZATION COMPLETE!\n"
                    result_text += "="*75 + "\n\n"
                    
                    # Show ATS score if available
                    if result.get('ats_score'):
                        result_text += f"📊 ATS SCORE: {result['ats_score']}/100\n"
                        if result.get('ats_breakdown'):
                            result_text += result['ats_breakdown'] + "\n"
                        result_text += "\n"
                    
                    result_text += f"📝 CHANGES MADE:\n"
                    result_text += f"  • Summary: {result.get('summary_changed', False) and 'Rewritten with AI agents' or 'Not changed'}\n"
                    result_text += f"  • Bullets Enhanced: {result.get('bullets_changed', 0)}\n"
                    result_text += f"  • Keywords Used: {result.get('keywords_count', 0)}\n\n"
                    
                    # Show gap analysis if available
                    if result.get('gap_analysis'):
                        gap = result['gap_analysis']
                        result_text += f"🎯 SKILL MATCH:\n"
                        result_text += f"  • Strong Match: {len(gap.get('strong_match', []))}\n"
                        result_text += f"  • Partial Match: {len(gap.get('partial_match', []))}\n"
                        result_text += f"  • Missing: {len(gap.get('missing_skills', []))}\n\n"
                    
                    # Update explainability panel for customize
                    self._update_actions_from_customize(result)
                    
                    result_text += f"📄 OUTPUT:\n"
                    result_text += f"  • File: {Path(output_path).name}\n\n"
                    
                    # Show agent recommendations if available
                    if result.get('agent_recommendations'):
                        result_text += f"💡 AGENT RECOMMENDATIONS:\n"
                        for rec in result['agent_recommendations']:
                            result_text += f"  {rec}\n"
                        result_text += "\n"
                    
                    result_text += f"📋 NOTES:\n"
                    for rec in result.get('recommendations', []):
                        result_text += f"  • {rec}\n"
                    
                    result_text += "\n" + "="*75 + "\n"
                    result_text += "✓ All changes highlighted in RED\n"
                    result_text += "✓ Formatting preserved\n"
                    result_text += "✓ Optimized by multi-agent system\n"
                    result_text += "="*75 + "\n"
                    
                    self.update_results(result_text, append=False)
                    self.set_progress(f"Saved to {Path(output_path).name}", "#10B981")
                    
                    # Auto-update resume to customized file for seamless re-analysis
                    self.resume_path = output_path
                    self.resume_text = read_file_smart(output_path)
                    self.resume_label.config(
                        text=f"✓ {os.path.basename(output_path)}", 
                        foreground="#10B981", 
                        font=('Arial', 10, 'bold')
                    )
                    
                    messagebox.showinfo("Success!", 
                                      f"✓ Resume customized successfully!\n\n"
                                      f"Location:\n{output_path}\n\n"
                                      f"Summary: {'Changed' if result.get('summary_changed') else 'Not changed'}\n"
                                      f"Bullets: {result.get('bullets_changed', 0)} enhanced\n\n"
                                      f"💡 The customized resume is now loaded.\n"
                                      f"Click 'Analyze Match' to see the improved ATS score!")
                
                else:
                    # Text file
                    result = self.handler.customize_text(self.resume_text, job_desc)
                    
                    output_path = filedialog.asksaveasfilename(
                        title="Save Customized Resume",
                        defaultextension=".txt",
                        initialfile="customized_resume.txt",
                        filetypes=[("Text File", "*.txt")]
                    )
                    
                    if output_path:
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(result['customized_resume'])
                        
                        result_text = "\n" + "="*75 + "\n"
                        result_text += "🎉 RESUME CUSTOMIZED!\n"
                        result_text += "="*75 + "\n\n"
                        result_text += f"📊 MATCH SCORE: {result['match_score']}/100\n\n"
                        result_text += "🔄 CHANGES MADE:\n"
                        for change in result['changes_made']:
                            result_text += f"  • {change}\n"
                        result_text += "\n" + "="*75 + "\n"
                        
                        self.update_results(result_text, append=False)
                        self.set_progress("✓ Done!", "green")
                        
                        messagebox.showinfo("Success!", f"✓ Resume saved to:\n{output_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Customization failed:\n{e}")
                self.set_progress("Customization failed", "red")
            finally:
                self.enable_buttons()
        
        threading.Thread(target=customize, daemon=True).start()
    
    def reset_all(self):
        """Reset all fields and UI to initial state."""
        # Clear resume
        self.resume_path = None
        self.resume_text = ""
        self.resume_label.config(text="No file selected", foreground="#6B7280", font=('Arial', 10))
        
        # Clear job description
        self.job_text.delete(1.0, tk.END)
        self.job_text.insert(1.0, self.job_placeholder)
        self.job_text.edit_reset()
        self.job_has_placeholder = True
        
        # Clear results
        self.results_data = ""
        
        # Reset dashboard metrics
        self.metrics_vars["ats"].set("ATS Compatibility: —")
        self.metrics_vars["before_score"].set("")
        self.metrics_vars["after_score"].set("")
        self.ats_bar['value'] = 0
        
        # Reset pipeline
        self._reset_pipeline()
        
        # Reset actions
        self._reset_actions()
        
        # Reset progress
        self.set_progress("Ready to analyze or customize resume", "#6B7280")
        
        # Reset before_score
        self.before_score = None
        
        messagebox.showinfo("Reset Complete", "All fields have been cleared. Ready for a new resume!")


def main():
    root = tk.Tk()
    app = FinalResumeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
