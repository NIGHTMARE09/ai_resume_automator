# import os
# from jinja2 import Template
# import json
# import subprocess
# import time
# from huggingface_hub import InferenceClient

# # --- Configuration ---
# # Use your Hugging Face access token
# HF_TOKEN 
# BASE_RESUME_TEMPLATE_PATH = "base_resume_template.tex"
# JD_FOLDER = "job_descriptions"
# OUTPUT_FOLDER = "tailored_resumes"

# # --- Helper Functions ---
# def load_file(file_path):
#     """Loads content from a text file."""
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             return f.read()
#     except FileNotFoundError:
#         print(f"Error: File not found at {file_path}")
#         return None
#     except Exception as e:
#         print(f"Error loading file {file_path}: {e}")
#         return None

# def generate_tailored_content(base_resume_content, job_description_content):
#     """
#     Uses Hugging Face API to generate tailored content for resume sections
#     based on the job description.
#     The prompt instructs the AI to return content in JSON format
#     matching the placeholders in the template.
#     """
#     prompt = f"""
#     You are a resume optimization expert. Your goal is to tailor a resume
#     section by section based on a job description.
#     The user will provide their base resume content and a job description.
#     Identify the key requirements and keywords from the job description.
#     Then, rewrite/generate content for the following sections, making sure
#     to incorporate relevant keywords and highlight matching experience
#     from the base resume:

#     1.  Summary: A concise 2-3 sentence summary highlighting relevant experience and skills.
#     2.  Skills: A list or paragraph of skills, emphasizing those mentioned in the JD.
#     3.  Scale AI Experience: Bullet points tailored to highlight achievements relevant to the JD.
#     4.  Samsung Experience: Bullet points tailored to highlight achievements relevant to the JD.
#     5.  Amazon Experience: Bullet points tailored to highlight achievements relevant to the JD.
#     6.  Paytm Project: Details tailored to highlight relevant aspects for the JD.

#     Return the tailored content strictly as a JSON object with keys corresponding
#     to the sections: "summary", "skills", "scale_ai_experience", "samsung_experience",
#     "amazon_experience", "paytm_project".
#     Ensure the content for each key is a string formatted appropriately for a LaTeX
#     document (e.g., bullet points using '\\item').

#     Base Resume Content (for context and source material):
#     ---
#     {base_resume_content}
#     ---

#     Job Description:
#     ---
#     {job_description_content}
#     ---

#     Example JSON output structure:
#     ```json
#     {{
#         "summary": "Results-driven...",
#         "skills": "Skills: ...",
#         "scale_ai_experience": "\\item Enhanced LLM models...\\item Built RESTful APIs...",
#         "samsung_experience": "\\item Introduced a React Web-Chat App...\\item Revamped backend infrastructure...",
#         "amazon_experience": "\\item Optimized large-dataset computation...\\item Improved Data Quality...",
#         "paytm_project": "\\item Built full stack payment app..."
#     }}
#     ```
#     Make sure the JSON is valid and contains only the JSON object. Do not include any
#     additional text or markdown outside the JSON object.
#     """

#     try:
#         # Create the Hugging Face inference client with Nebius as provider
#         client = InferenceClient(
#             provider="nebius",  # Using Nebius AI as the inference provider
#             api_key=HF_TOKEN,   # Your Hugging Face token
#         )

#         # Make a request to a model served by Nebius
#         completion = client.chat.completions.create(
#             model="deepseek-ai/DeepSeek-R1-0528",  # A model available via Nebius
#             messages=[
#                 {
#                     "role": "system",
#                     # "content": "You are a helpful assistant that tailors resume content based on job descriptions and provides the output in JSON format."
#                     "content": "You are an expert resume tailoring specialist for software engineering positions with deep knowledge of ATS systems and hiring manager preferences."
#                 },
                
#                 {
#                     "role": "user",
#                     "content": prompt,
#                 }
#             ],
#             response_format={"type": "json_object"}  # Request JSON output
#         )

#         content = completion.choices[0].message.content
#         # print(f"• Hugging Face response: {content}")
#         print("API response for experience field: ")
#         # print(json.dumps(json.loads(content), indent=4))
#         return json.loads(content)

#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON from Hugging Face response: {e}")
#         print("Raw response content:", content)
#         return None
#     except Exception as e:
#         print(f"An error occurred during Hugging Face API call: {e}")
#         print(f"Error details: {str(e)}")
#         return None

# def generate_resume_file(template_path, tailored_content, output_path):
#     """Fills the Jinja2 template with tailored content and saves as a .tex file."""
#     template_str = load_file(template_path)
#     if template_str is None:
#         return False

#     template = Template(template_str)

#     try:
#         # Render the template with the tailored content
#         rendered_resume = template.render(tailored_content)

#         with open(output_path, 'w', encoding='utf-8') as f:
#             f.write(rendered_resume)
#         print(f"• Tailored .tex resume saved at {output_path}")
#         return True
#     except Exception as e:
#         print(f"Error rendering template or saving file {output_path}: {e}")
#         return False

# def compile_pdf(tex_path):
#     """Compile the TeX file to PDF using a more reliable method."""
#     try:
#         # Get directory and filename separately
#         output_dir = os.path.dirname(tex_path)
#         filename = os.path.basename(tex_path)
        
#         print(f"Attempting to compile {filename} to PDF...")
        
#         # Change to the output directory
#         original_dir = os.getcwd()
        
#         # Copy the resume.cls file to the output directory
#         cls_source = os.path.join(original_dir, "resume.cls")
#         cls_dest = os.path.join(output_dir, "resume.cls")
        
#         print(f"Copying resume.cls from {cls_source} to {cls_dest}")
#         if os.path.exists(cls_source):
#             import shutil
#             shutil.copy2(cls_source, cls_dest)
#             print(f"Successfully copied resume.cls to {output_dir}")
#         else:
#             print(f"Warning: resume.cls not found at {cls_source}")
        
#         # Change to the output directory
#         os.chdir(output_dir)
        
#         # Run pdflatex with just the filename (no path issues)
#         cmd = ['pdflatex', '-interaction=nonstopmode', filename]
#         print(f"Running command: {' '.join(cmd)}")
#         process = subprocess.run(cmd, capture_output=True, text=True)
        
#         # Change back to original directory
#         os.chdir(original_dir)
        
#         if process.returncode == 0:
#             pdf_path = tex_path.replace('.tex', '.pdf')
#             print(f"• PDF successfully generated at {pdf_path}")
#             return True
#         else:
#             print(f"Error during pdflatex compilation:")
#             print(f"Command: {cmd}")
#             print(f"Return Code: {process.returncode}")
#             print(f"Stdout: {process.stdout[:500]}...")  # Print first 500 chars of output
#             print(f"• PDF compilation failed for {tex_path}")
#             return False
#     except Exception as e:
#         print(f"Exception during PDF compilation: {e}")
#         # Make sure to return to the original directory even if an exception occurs
#         if 'original_dir' in locals():
#             os.chdir(original_dir)
#         return False


# # --- Main Logic ---
# def main():
#     # Create output folders if they don't exist
#     os.makedirs(JD_FOLDER, exist_ok=True)
#     os.makedirs(OUTPUT_FOLDER, exist_ok=True)

#     base_resume_content = load_file(BASE_RESUME_TEMPLATE_PATH)
#     if base_resume_content is None:
#         print("Base resume template not found. Make sure base_resume_template.tex exists.")
#         return

#     print("Watching for new job descriptions in:", JD_FOLDER)
#     processed_jds = set()  # Keep track of processed files

#     while True:
#         # List files in the job descriptions folder
#         current_jds = set([f for f in os.listdir(JD_FOLDER) if f.endswith(".txt")])

#         # Find new job description files
#         new_jds = current_jds - processed_jds

#         for jd_file_name in new_jds:
#             jd_file_path = os.path.join(JD_FOLDER, jd_file_name)
#             print(f"\nFound new job description: {jd_file_name}")

#             job_description_content = load_file(jd_file_path)
#             if job_description_content is None:
#                 print(f"Could not read job description from {jd_file_name}. Skipping.")
#                 processed_jds.add(jd_file_name)
#                 continue

#             print("Generating tailored content using Hugging Face API...")
#             tailored_content_dict = generate_tailored_content(base_resume_content, job_description_content)

#             if tailored_content_dict:
#                 # Create output filename based on JD filename
#                 output_file_name_base = os.path.splitext(jd_file_name)[0]
#                 output_tex_path = os.path.join(OUTPUT_FOLDER, f"{output_file_name_base}_tailored.tex")

#                 # Generate the .tex file
#                 if generate_resume_file(BASE_RESUME_TEMPLATE_PATH, tailored_content_dict, output_tex_path):
#                     # Compile to PDF
#                     compile_pdf(output_tex_path)

#             processed_jds.add(jd_file_name)  # Mark as processed

#         # Wait for a bit before checking again
#         time.sleep(10)

# if __name__ == "__main__":
#     main()


import os
from jinja2 import Template
import json
import subprocess
import time
from huggingface_hub import InferenceClient
from sanitize_latex import sanitize_latex_content
from format_bullet_points import format_bullet_points
from dotenv import load_dotenv
# --- Configuration ---

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise EnvironmentError("HF_TOKEN is not set in the environment or .env file. Please set it before running this script.")

BASE_RESUME_TEMPLATE_PATH = "base_resume_template.tex"
JD_FOLDER = "job_descriptions"
OUTPUT_FOLDER = "tailored_resumes"

# --- Multiple Prompt Strategies ---
def get_prompt_strategy_1_ats_focused(base_resume_content, job_description_content):
    """
    Strategy 1: ATS-Optimized with Keyword Matching
    Focus: High ATS score, keyword density, direct language mirroring
    """
    return f"""
You are an expert ATS resume optimizer specializing in Software Engineer positions. Your task is to rewrite resume sections to maximize ATS compatibility and recruiter appeal.

CRITICAL REQUIREMENTS:
1. Mirror the exact language and terminology from the job description
2. Incorporate ALL relevant technical keywords naturally
3. Use quantifiable metrics where possible (percentages, numbers, scale)
4. Match the job description's tone and phrasing
5. Prioritize hard skills over soft skills
6. Ensure each bullet point demonstrates IMPACT, not just responsibilities

ANALYSIS FRAMEWORK:
- Extract ALL technical skills, frameworks, and tools mentioned in the JD
- Identify required years of experience and seniority level
- Note specific responsibilities and required outcomes
- Match company culture keywords if mentioned

Job Description Analysis:
---
{job_description_content}
---

Base Resume (Source Material):
---
{base_resume_content}
---

OUTPUT REQUIREMENTS:
Return ONLY a valid JSON object with these keys:
- "summary": 2-3 sentences using JD language, highlighting relevant experience
- "skills": Comma-separated list prioritizing JD-mentioned technologies
- "scale_ai_experience": LaTeX bullet points (\\item) with metrics and JD keywords
- "samsung_experience": LaTeX bullet points (\\item) with metrics and JD keywords  
- "amazon_experience": LaTeX bullet points (\\item) with metrics and JD keywords
- "paytm_project": LaTeX bullet points (\\item) with metrics and JD keywords

BULLET POINT FORMULA: Action Verb + Specific Technology/Method + Quantifiable Result + Business Impact

Example: "\\item Architected scalable microservices using Node.js and Docker, reducing API response time by 40% and supporting 10M+ daily transactions"
"""

def get_prompt_strategy_2_value_focused(base_resume_content, job_description_content):
    """
    Strategy 2: Value Proposition Focus
    Focus: Demonstrating clear business value and problem-solving
    """
    return f"""
You are a senior technical recruiter and resume strategist. Your expertise is translating technical achievements into business value for Software Engineer positions.

CORE OBJECTIVE: Transform this resume to demonstrate clear value proposition and problem-solving capability that directly addresses the hiring manager's needs.

VALUE DEMONSTRATION FRAMEWORK:
1. Problem Identification: What challenge did you solve?
2. Technical Solution: How did you solve it? (using JD-relevant technologies)
3. Measurable Impact: What was the business outcome?
4. Scale/Complexity: What was the scope of your work?

LANGUAGE ALIGNMENT STRATEGY:
- Use the EXACT terminology from the job description
- Match the company's stated values and culture
- Highlight experiences that solve the problems this role will face
- Demonstrate progression and growth in responsibilities

Job Description:
---
{job_description_content}
---

Current Resume Content:
---
{base_resume_content}
---

TAILORING INSTRUCTIONS:
1. Summary: Position yourself as the solution to their specific needs
2. Skills: List technologies in order of JD priority, group by relevance
3. Experience: Reframe each role to show progression toward this target role
4. Projects: Highlight those most relevant to the JD requirements

Return valid JSON with keys: "summary", "skills", "scale_ai_experience", "samsung_experience", "amazon_experience", "paytm_project"

Each experience bullet should follow: Challenge → Solution → Impact → Relevance to target role
"""

def get_prompt_strategy_3_story_driven(base_resume_content, job_description_content):
    """
    Strategy 3: Story-Driven Narrative
    Focus: Coherent career narrative that leads to this specific role
    """
    return f"""
You are a career storytelling expert specializing in Software Engineer positioning. Create a compelling narrative that shows this candidate's journey naturally leads to this specific role.

NARRATIVE STRATEGY:
- Craft a coherent story of technical growth and specialization
- Show how each role built capabilities needed for the target position
- Demonstrate increasing responsibility and impact
- Use the job description's language as the "destination" of this career journey

STORY ELEMENTS TO WEAVE:
1. Technical Evolution: How skills progressed toward JD requirements
2. Impact Scaling: How responsibilities and impact grew over time
3. Domain Expertise: How experience aligns with the company's industry/challenges
4. Leadership Growth: How influence and scope expanded

Job Description (The Destination):
---
{job_description_content}
---

Career Journey (The Path):
---
{base_resume_content}
---

STORYTELLING GUIDELINES:
- Start each experience section with context about the business challenge
- Show technical decisions and their reasoning
- Quantify impact wherever possible
- Connect each role to the next in a logical progression
- Use compelling action verbs that show ownership and initiative

JSON OUTPUT with keys: "summary", "skills", "scale_ai_experience", "samsung_experience", "amazon_experience", "paytm_project"

Summary should be a compelling elevator pitch that positions you as the ideal candidate for THIS specific role.
"""

def get_prompt_strategy_4_technical_depth(base_resume_content, job_description_content):
    """
    Strategy 4: Technical Depth & Architecture Focus
    Focus: Demonstrating deep technical competency and system thinking
    """
    return f"""
You are a senior Software Engineer and technical interviewer. Your job is to evaluate and present technical depth that will impress both technical and non-technical hiring managers.

TECHNICAL COMPETENCY FRAMEWORK:
1. System Design: Show ability to architect scalable solutions
2. Problem Complexity: Demonstrate handling of complex technical challenges
3. Technology Mastery: Show deep understanding, not just usage
4. Performance Impact: Quantify technical improvements
5. Team/Process Impact: Show technical leadership and influence

DEPTH INDICATORS:
- Specific technologies used and WHY they were chosen
- Scale of systems worked on (users, transactions, data volume)
- Performance improvements achieved
- Technical decisions made and their outcomes
- Mentoring or technical leadership provided

Job Requirements Analysis:
---
{job_description_content}
---

Technical Background:
---
{base_resume_content}
---

OPTIMIZATION STRATEGY:
1. Identify the most complex technical achievements from your background
2. Reframe them using the job description's technical terminology
3. Emphasize system thinking and architectural decisions
4. Show progression from individual contributor to technical leader
5. Quantify performance, scalability, and reliability improvements

Return JSON with keys: "summary", "skills", "scale_ai_experience", "samsung_experience", "amazon_experience", "paytm_project"

Each bullet point should demonstrate: Technical Challenge → Solution Architecture → Implementation Details → Measurable Outcome
"""

# --- Helper Functions ---
def load_file(file_path):
    """Loads content from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None

def detect_role_type(job_description_content):
    """
    Analyze job description to determine the best prompt strategy
    """
    jd_lower = job_description_content.lower()
    
    # Keywords that suggest different focus areas
    ats_keywords = ['applicant tracking', 'resume screening', 'keyword', 'ats']
    value_keywords = ['business impact', 'roi', 'revenue', 'growth', 'efficiency']
    story_keywords = ['career progression', 'leadership', 'mentorship', 'growth']
    technical_keywords = ['architecture', 'system design', 'scalability', 'performance', 'senior', 'lead']
    
    scores = {
        'ats': sum(1 for kw in ats_keywords if kw in jd_lower),
        'value': sum(1 for kw in value_keywords if kw in jd_lower),
        'story': sum(1 for kw in story_keywords if kw in jd_lower),
        'technical': sum(1 for kw in technical_keywords if kw in jd_lower)
    }
    
    # Default to ATS-focused for most software engineer roles
    if max(scores.values()) == 0:
        return 'ats'
    
    return max(scores, key=scores.get)

# def generate_tailored_content(base_resume_content, job_description_content, strategy=None):
#     """
#     Uses Hugging Face API to generate tailored content with different strategies
#     """
#     if strategy is None:
#         strategy = detect_role_type(job_description_content)
    
#     print(f"Using strategy: {strategy}")
    
#     # Select prompt based on strategy
#     prompt_strategies = {
#         'ats': get_prompt_strategy_1_ats_focused,
#         'value': get_prompt_strategy_2_value_focused,
#         'story': get_prompt_strategy_3_story_driven,
#         'technical': get_prompt_strategy_4_technical_depth
#     }
    
#     if strategy not in prompt_strategies:
#         strategy = 'ats'  # Default fallback
    
#     prompt = prompt_strategies[strategy](base_resume_content, job_description_content)

#     try:
#         # Create the Hugging Face inference client with Nebius as provider
#         client = InferenceClient(
#             provider="nebius",
#             api_key=HF_TOKEN,
#         )

#         # Make a request to a model served by Nebius
#         completion = client.chat.completions.create(
#             model="deepseek-ai/DeepSeek-R1-0528",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "You are an expert resume optimizer specializing in Software Engineer positions. Always return valid JSON format with precise, impactful content."
#                 },
#                 {
#                     "role": "user",
#                     "content": prompt,
#                 }
#             ],
#             response_format={"type": "json_object"},
#             max_tokens=2000,  # Ensure enough tokens for detailed responses
#             temperature=0.7   # Balance creativity with consistency
#         )

#         content = completion.choices[0].message.content
#         print(f"API response received using {strategy} strategy")
        
#         # Validate JSON before returning
#         parsed_content = json.loads(content)
        
#         for key,value in parsed_content.items():
#             # sanitize and format the content
#             formatted_value = format_bullet_points(value)
#             sanitized_value = sanitize_latex_content(formatted_value)
#             parsed_content[key] = sanitized_value
    
#         # Ensure all required keys are present
#         required_keys = ["summary", "skills", "scale_ai_experience", "samsung_experience", "amazon_experience", "paytm_project"]
#         for key in required_keys:
#             if key not in parsed_content:
#                 print(f"Warning: Missing key '{key}' in response")
#                 parsed_content[key] = ""
        
#         return parsed_content

#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON from Hugging Face response: {e}")
#         print("Raw response content:", content)
#         return None
#     except Exception as e:
#         print(f"An error occurred during Hugging Face API call: {e}")
#         return None

def generate_tailored_content(base_resume_content, job_description_content, strategy=None):
    """
    Uses Hugging Face API to generate tailored content with different strategies
    """
    if strategy is None:
        strategy = detect_role_type(job_description_content)
    
    print(f"Using strategy: {strategy}")
    
    # Select prompt based on strategy
    prompt_strategies = {
        'ats': get_prompt_strategy_1_ats_focused,
        'value': get_prompt_strategy_2_value_focused,
        'story': get_prompt_strategy_3_story_driven,
        'technical': get_prompt_strategy_4_technical_depth
    }
    
    # Improved fallback with logging
    if strategy not in prompt_strategies:
        print(f"Warning: Strategy '{strategy}' not found. Falling back to 'ats' strategy.")
        strategy = 'ats'  # Default fallback
    
    prompt = prompt_strategies[strategy](base_resume_content, job_description_content)

    try:
        # Create the Hugging Face inference client with Nebius as provider
        client = InferenceClient(
            provider="nebius",
            api_key=HF_TOKEN,
        )

        # Make a request to a model served by Nebius
        print(f"Sending request to Nebius AI via Hugging Face...")
        completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1-0528",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume optimizer specializing in Software Engineer positions. Always return valid JSON format with precise, impactful content."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=2000,
            temperature=0.7
        )

        content = completion.choices[0].message.content
        print(f"API response received using {strategy} strategy")
        
        # Process and validate the response
        print("Processing and sanitizing content for LaTeX...")
        
        try:
            # Validate JSON before further processing
            parsed_content = json.loads(content)
            
            # Define required keys for better error handling
            required_keys = ["summary", "skills", "scale_ai_experience", "samsung_experience", "amazon_experience", "paytm_project"]
            
            # Add missing keys with empty values
            for key in required_keys:
                if key not in parsed_content:
                    print(f"Warning: Missing key '{key}' in response. Adding empty value.")
                    parsed_content[key] = ""
            
            # Process each value in the parsed content
            for key, value in parsed_content.items():
                if not isinstance(value, str):
                    print(f"Warning: Value for '{key}' is not a string. Converting to string.")
                    value = str(value)
                
                # Format and sanitize the content
                formatted_value = format_bullet_points(value)
                sanitized_value = sanitize_latex_content(formatted_value)
                parsed_content[key] = sanitized_value
                
            print("Content processing complete.")
            return parsed_content
            
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from API response: {e}")
            print("Raw response content:", content[:500] + "..." if len(content) > 500 else content)
            return None
            
    except Exception as e:
        print(f"An error occurred during API call: {str(e)}")
        import traceback
        print(traceback.format_exc())  # Print full stack trace for debugging
        return None

def generate_resume_file(template_path, tailored_content, output_path):
    """Fills the Jinja2 template with tailored content and saves as a .tex file."""
    template_str = load_file(template_path)
    if template_str is None:
        return False

    template = Template(template_str)

    try:
        # Render the template with the tailored content
        rendered_resume = template.render(tailored_content)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered_resume)
        print(f"• Tailored .tex resume saved at {output_path}")
        return True
    except Exception as e:
        print(f"Error rendering template or saving file {output_path}: {e}")
        return False

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
        cmd = ['pdflatex', '-interaction=nonstopmode', filename]
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

def test_all_strategies(base_resume_content, job_description_content, output_prefix):
    """
    Test all four strategies and generate separate resumes for comparison
    """
    strategies = ['ats', 'value', 'story', 'technical']
    
    for strategy in strategies:
        print(f"\n--- Testing {strategy.upper()} Strategy ---")
        tailored_content = generate_tailored_content(
            base_resume_content, 
            job_description_content, 
            strategy=strategy
        )
        
        if tailored_content:
            output_tex_path = os.path.join(OUTPUT_FOLDER, f"{output_prefix}_{strategy}_strategy.tex")
            if generate_resume_file(BASE_RESUME_TEMPLATE_PATH, tailored_content, output_tex_path):
                compile_pdf(output_tex_path)

# --- Main Logic ---
def main():
    # Create output folders if they don't exist
    os.makedirs(JD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    base_resume_content = load_file(BASE_RESUME_TEMPLATE_PATH)
    if base_resume_content is None:
        print("Base resume template not found. Make sure base_resume_template.tex exists.")
        return

    print("Enhanced Resume Tailoring System Starting...")
    print("Available strategies: ATS-focused, Value-focused, Story-driven, Technical-depth")
    print("Watching for new job descriptions in:", JD_FOLDER)
    
    processed_jds = set()

    while True:
        current_jds = set([f for f in os.listdir(JD_FOLDER) if f.endswith(".txt")])
        new_jds = current_jds - processed_jds

        for jd_file_name in new_jds:
            jd_file_path = os.path.join(JD_FOLDER, jd_file_name)
            print(f"\nProcessing new job description: {jd_file_name}")

            job_description_content = load_file(jd_file_path)
            if job_description_content is None:
                print(f"Could not read job description from {jd_file_name}. Skipping.")
                processed_jds.add(jd_file_name)
                continue

            output_file_name_base = os.path.splitext(jd_file_name)[0]
            
            # Option 1: Auto-detect best strategy
            print("\n=== Auto-detecting best strategy ===")
            tailored_content = generate_tailored_content(base_resume_content, job_description_content)
            
            if tailored_content:
                output_tex_path = os.path.join(OUTPUT_FOLDER, f"{output_file_name_base}_auto_tailored.tex")
                if generate_resume_file(BASE_RESUME_TEMPLATE_PATH, tailored_content, output_tex_path):
                    compile_pdf(output_tex_path)
            
            # Option 2: Generate all strategies for comparison (uncomment to enable)
            # print("\n=== Generating all strategies for comparison ===")
            # test_all_strategies(base_resume_content, job_description_content, output_file_name_base)

            processed_jds.add(jd_file_name)

        time.sleep(10)

if __name__ == "__main__":
    main()