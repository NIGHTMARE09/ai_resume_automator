import os
import subprocess

"""
    You are an expert resume tailoring specialist for software engineering positions with deep knowledge of ATS systems
    and hiring manager preferences. Your task is to optimize this candidate's resume for the specific job description provided.
    
    ## GUIDELINES FOR TAILORING:
    
    1. KEYWORD MATCHING: Carefully analyze the job description and identify all technical skills, frameworks, languages, 
       and methodologies mentioned. Incorporate these exact keywords naturally throughout the resume.
    
    2. QUANTIFY ACHIEVEMENTS: For each relevant experience, include measurable outcomes with metrics (%, time saved, 
       efficiency gained, user impact) where available in the base resume.
    
    3. TECHNICAL DEPTH BALANCE: Demonstrate technical expertise without overwhelming with jargon. Focus on technologies 
       mentioned in the job description plus relevant complementary skills.
    
    4. SOFT SKILLS INTEGRATION: Identify soft skills in the job description (communication, teamwork, problem-solving) 
       and weave these into achievement descriptions rather than listing them separately.
    
    5. VALUE PROPOSITION: For each experience, highlight how the candidate's work created business value - emphasize 
       not just what was built, but why it mattered.
    
    6. ATS OPTIMIZATION: Use clear section headings and standard formatting for maximum ATS compatibility.
    
    ## SECTIONS TO TAILOR:
    
    1. Summary: A powerful 2-3 sentence professional summary emphasizing years of relevant experience, key technical 
       skills from the job description, and 1-2 standout accomplishments aligned with the role's needs.
       
    2. Skills: A focused list prioritizing skills explicitly mentioned in the job description first, followed by relevant 
       complementary skills from the base resume. Format as a clean list for ATS compatibility.
       
    3. Experience sections (Scale AI, Samsung, Amazon): For each role, create 3-5 bullet points that:
       - Lead with strong technical action verbs
       - Emphasize projects/responsibilities matching the job requirements
       - Include specific technologies mentioned in the job description when truthfully used
       - Demonstrate problem-solving abilities with technical challenges
       - Quantify impact where possible with specific metrics
       
    4. Paytm Project: Frame this project to highlight aspects that directly relate to the job requirements, 
       emphasizing technical skills, methodologies, and outcomes relevant to the position.
    
    Base Resume Content (for context and source material):
    ---
    {base_resume_content}
    ---
    
    Job Description:
    ---
    {job_description_content}
    ---
    
    Return ONLY a valid JSON object with the following keys exactly as specified:
    "summary", "skills", "scale_ai_experience", "samsung_experience", "amazon_experience", "paytm_project"
    
    Each value must be a string properly formatted for LaTeX (use \\item for bullet points, avoid characters that 
    would break LaTeX compilation). Do not exaggerate qualifications or include untrue information.
    
    Example JSON structure:
    ```json
    {{
        "summary": "Results-driven Software Engineer with 5+ years experience in backend development...",
        "skills": "Python, Java, Kubernetes, AWS, System Design, CI/CD, Microservices...",
        "scale_ai_experience": "\\item Engineered scalable API endpoints that improved data processing speed by 40%\\item...",
        "samsung_experience": "\\item Developed microservices architecture that reduced system latency by 25%\\item...",
        "amazon_experience": "\\item Optimized database queries reducing computational load by 35%\\item...",
        "paytm_project": "\\item Architected and implemented a payment processing system handling 100K+ transactions..."
    }}
    ```
"""

def compile_pdf(tex_path):
    """Compile the TeX file to PDF using a more reliable method."""
    try:
        # Get directory and filename separately
        output_dir = os.path.dirname(tex_path)
        filename = os.path.basename(tex_path)
        
        print(f"Attempting to compile {filename} to PDF...")
        
        # Change to the output directory
        original_dir = os.getcwd()
        
        # Copy the resume.cls file to the output directory
        cls_source = os.path.join(original_dir, "resume.cls")
        cls_dest = os.path.join(output_dir, "resume.cls")
        
        print(f"Copying resume.cls from {cls_source} to {cls_dest}")
        if os.path.exists(cls_source):
            import shutil
            shutil.copy2(cls_source, cls_dest)
            print(f"Successfully copied resume.cls to {output_dir}")
        else:
            print(f"Warning: resume.cls not found at {cls_source}")
        
        # Change to the output directory
        os.chdir(output_dir)
        
        # Run pdflatex with just the filename (no path issues)
        cmd = ['pdflatex', '-interaction=nonstopmode', '-file-line-error', '-verbose',filename]
        print(f"Running command: {' '.join(cmd)}")
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        # Change back to original directory
        os.chdir(original_dir)
        
        if process.returncode == 0:
            pdf_path = tex_path.replace('.tex', '.pdf')
            print(f"• PDF successfully generated at {pdf_path}")
            return True
        else:
            print(f"Error during pdflatex compilation:")
            print(f"Command: {cmd}")
            print(f"Return Code: {process.returncode}")
            print(f"Stdout: {process.stdout[:500]}...")  # Print first 500 chars of output
            print(f"• PDF compilation failed for {tex_path}")
            return False
    except Exception as e:
        print(f"Exception during PDF compilation: {e}")
        # Make sure to return to the original directory even if an exception occurs
        if 'original_dir' in locals():
            os.chdir(original_dir)
        return False

