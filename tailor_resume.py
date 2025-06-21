# import os
# from jinja2 import Template
# import json
# import subprocess
# import time
# from huggingface_hub import InferenceClient
# from sanitize_latex import sanitize_latex_content
# from format_bullet_points import format_bullet_points
# from dotenv import load_dotenv
# from litellm import completion
# # --- Configuration ---

# load_dotenv()
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# if not OPENROUTER_API_KEY:
#     raise EnvironmentError("OPENROUTER_API_KEY is not set in the environment or .env file. Please set it before running this script.")

# BASE_RESUME_TEMPLATE_PATH = "base_resume_template.tex"
# JD_FOLDER = "job_descriptions"
# OUTPUT_FOLDER = "tailored_resumes"

# # --- Multiple Prompt Strategies ---
# def get_prompt_strategy_1_ats_focused(base_resume_content, job_description_content):
#     """
#     Strategy 1: ATS-Optimized with Keyword Matching
#     Focus: High ATS score, keyword density, direct language mirroring
#     """
#     return f"""
# You are an expert ATS resume optimizer specializing in Software Engineer positions. Your task is to rewrite resume sections to maximize ATS compatibility and recruiter appeal.

# CRITICAL REQUIREMENTS:
# 1. Mirror the exact language and terminology from the job description
# 2. Incorporate ALL relevant technical keywords naturally
# 3. Use quantifiable metrics where possible (percentages, numbers, scale)
# 4. Match the job description's tone and phrasing
# 5. Prioritize hard skills over soft skills
# 6. Ensure each bullet point demonstrates IMPACT, not just responsibilities

# ANALYSIS FRAMEWORK:
# - Extract ALL technical skills, frameworks, and tools mentioned in the JD
# - Identify required years of experience and seniority level
# - Note specific responsibilities and required outcomes
# - Match company culture keywords if mentioned

# Job Description Analysis:
# ---
# {job_description_content}
# ---

# Base Resume (Source Material):
# ---
# {base_resume_content}
# ---

# OUTPUT REQUIREMENTS:
# Return ONLY a valid JSON object with these keys:
# - "summary": 2-3 sentences using JD language, highlighting relevant experience
# - "skills": Comma-separated list prioritizing JD-mentioned technologies
# - "scale_ai_experience": LaTeX bullet points (\\item) with metrics and JD keywords
# - "samsung_experience": LaTeX bullet points (\\item) with metrics and JD keywords  
# - "amazon_experience": LaTeX bullet points (\\item) with metrics and JD keywords
# - "paytm_mini": LaTeX bullet points (\\item) with metrics and JD keywords

# BULLET POINT FORMULA: Action Verb + Specific Technology/Method + Quantifiable Result + Business Impact

# Example: "\\item Architected scalable microservices using Node.js and Docker, reducing API response time by 40% and supporting 10M+ daily transactions"

# IMPORTANT: Return ONLY the raw JSON object without any markdown code blocks, explanations, or additional text.
# Do not include ```json or ``` markers around your response.
# """

# def get_prompt_strategy_2_value_focused(base_resume_content, job_description_content):
#     """
#     Strategy 2: Value Proposition Focus
#     Focus: Demonstrating clear business value and problem-solving
#     """
#     return f"""
# You are a senior technical recruiter and resume strategist. Your expertise is translating technical achievements into business value for Software Engineer positions.

# CORE OBJECTIVE: Transform this resume to demonstrate clear value proposition and problem-solving capability that directly addresses the hiring manager's needs.

# VALUE DEMONSTRATION FRAMEWORK:
# 1. Problem Identification: What challenge did you solve?
# 2. Technical Solution: How did you solve it? (using JD-relevant technologies)
# 3. Measurable Impact: What was the business outcome?
# 4. Scale/Complexity: What was the scope of your work?

# LANGUAGE ALIGNMENT STRATEGY:
# - Use the EXACT terminology from the job description
# - Match the company's stated values and culture
# - Highlight experiences that solve the problems this role will face
# - Demonstrate progression and growth in responsibilities

# Job Description:
# ---
# {job_description_content}
# ---

# Current Resume Content:
# ---
# {base_resume_content}
# ---

# TAILORING INSTRUCTIONS:
# 1. Summary: Position yourself as the solution to their specific needs
# 2. Skills: List technologies in order of JD priority, group by relevance
# 3. Experience: Reframe each role to show progression toward this target role
# 4. Projects: Highlight those most relevant to the JD requirements

# Return valid JSON with keys: "summary", "skills", "scale_ai_experience", "samsung_experience", "amazon_experience", "paytm_mini"

# Each experience bullet should follow: Challenge → Solution → Impact → Relevance to target role

# IMPORTANT: Return ONLY the raw JSON object without any markdown code blocks, explanations, or additional text.
# Do not include ```json or ``` markers around your response.
# """

# def get_prompt_strategy_3_story_driven(base_resume_content, job_description_content):
#     """
#     Strategy 3: Story-Driven Narrative
#     Focus: Coherent career narrative that leads to this specific role
#     """
#     return f"""
# You are a career storytelling expert specializing in Software Engineer positioning. Create a compelling narrative that shows this candidate's journey naturally leads to this specific role.

# NARRATIVE STRATEGY:
# - Craft a coherent story of technical growth and specialization
# - Show how each role built capabilities needed for the target position
# - Demonstrate increasing responsibility and impact
# - Use the job description's language as the "destination" of this career journey

# STORY ELEMENTS TO WEAVE:
# 1. Technical Evolution: How skills progressed toward JD requirements
# 2. Impact Scaling: How responsibilities and impact grew over time
# 3. Domain Expertise: How experience aligns with the company's industry/challenges
# 4. Leadership Growth: How influence and scope expanded

# Job Description (The Destination):
# ---
# {job_description_content}
# ---

# Career Journey (The Path):
# ---
# {base_resume_content}
# ---

# STORYTELLING GUIDELINES:
# - Start each experience section with context about the business challenge
# - Show technical decisions and their reasoning
# - Quantify impact wherever possible
# - Connect each role to the next in a logical progression
# - Use compelling action verbs that show ownership and initiative

# JSON OUTPUT with keys: "summary", "skills", "scale_ai_experience", "samsung_experience", "amazon_experience", "paytm_mini"

# Summary should be a compelling elevator pitch that positions you as the ideal candidate for THIS specific role.

# IMPORTANT: Return ONLY the raw JSON object without any markdown code blocks, explanations, or additional text.
# Do not include ```json or ``` markers around your response.
# """

# def get_prompt_strategy_4_technical_depth(base_resume_content, job_description_content):
#     """
#     Strategy 4: Technical Depth & Architecture Focus
#     Focus: Demonstrating deep technical competency and system thinking
#     """
#     return f"""
# You are a senior Software Engineer and technical interviewer. Your job is to evaluate and present technical depth that will impress both technical and non-technical hiring managers.

# TECHNICAL COMPETENCY FRAMEWORK:
# 1. System Design: Show ability to architect scalable solutions
# 2. Problem Complexity: Demonstrate handling of complex technical challenges
# 3. Technology Mastery: Show deep understanding, not just usage
# 4. Performance Impact: Quantify technical improvements
# 5. Team/Process Impact: Show technical leadership and influence

# DEPTH INDICATORS:
# - Specific technologies used and WHY they were chosen
# - Scale of systems worked on (users, transactions, data volume)
# - Performance improvements achieved
# - Technical decisions made and their outcomes
# - Mentoring or technical leadership provided

# Job Requirements Analysis:
# ---
# {job_description_content}
# ---

# Technical Background:
# ---
# {base_resume_content}
# ---

# OPTIMIZATION STRATEGY:
# 1. Identify the most complex technical achievements from your background
# 2. Reframe them using the job description's technical terminology
# 3. Emphasize system thinking and architectural decisions
# 4. Show progression from individual contributor to technical leader
# 5. Quantify performance, scalability, and reliability improvements

# Return JSON with keys: "summary", "skills", "scale_ai_experience", "samsung_experience", "amazon_experience", "paytm_mini"

# Each bullet point should demonstrate: Technical Challenge → Solution Architecture → Implementation Details → Measurable Outcome

# IMPORTANT: Return ONLY the raw JSON object without any markdown code blocks, explanations, or additional text.
# Do not include ```json or ``` markers around your response.

# """

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

# def detect_role_type(job_description_content):
#     """
#     Analyze job description to determine the best prompt strategy
#     """
#     jd_lower = job_description_content.lower()
    
#     # Keywords that suggest different focus areas
#     ats_keywords = ['applicant tracking', 'resume screening', 'keyword', 'ats']
#     value_keywords = ['business impact', 'roi', 'revenue', 'growth', 'efficiency']
#     story_keywords = ['career progression', 'leadership', 'mentorship', 'growth']
#     technical_keywords = ['architecture', 'system design', 'scalability', 'performance', 'senior', 'lead']
    
#     scores = {
#         'ats': sum(1 for kw in ats_keywords if kw in jd_lower),
#         'value': sum(1 for kw in value_keywords if kw in jd_lower),
#         'story': sum(1 for kw in story_keywords if kw in jd_lower),
#         'technical': sum(1 for kw in technical_keywords if kw in jd_lower)
#     }
    
#     # Default to ATS-focused for most software engineer roles
#     if max(scores.values()) == 0:
#         return 'ats'
    
#     return max(scores, key=scores.get)

# def process_api_response(content):
#     """
#     Process and sanitize the API response by removing markdown code block markers
#     and properly parsing the JSON content.
#     """
#     print("Processing and sanitizing content for LaTeX...")
    
#     from itemize_lists_keys import ITEMIZE_LIST_KEYS
    
#     try:
#         # Strip any markdown code block markers
#         if content.startswith("```json"):
#             # Find the end of the code block
#             end_marker = content.rfind("```")
#             if end_marker > 6:  # 6 is the length of "```json"
#                 content = content[6:end_marker].strip()
#             else:
#                 content = content[6:].strip()
#         elif content.startswith("```"):
#             # Find the end of the code block
#             end_marker = content.rfind("```")
#             if end_marker > 3:  # 3 is the length of "```"
#                 content = content[3:end_marker].strip()
#             else:
#                 content = content[3:].strip()
                
#         # Validate JSON before further processing
#         parsed_content = json.loads(content)
        
#         # Define required keys for better error handling
#         required_keys = ["summary", "skills", "scale_ai_experience", "samsung_experience", "amazon_experience", "paytm_mini"]
        
#         # Add missing keys with empty values
#         for key in required_keys:
#             if key not in parsed_content:
#                 print(f"Warning: Missing key '{key}' in response. Adding empty value.")
#                 parsed_content[key] = ""
        
#         processed_content = {}
        
#         # Process each value in the parsed content
#         for key, value in parsed_content.items():
#             if not isinstance(value, str):
#                 print(f"Warning: Value for '{key}' is not a string. Converting to string.")
#                 value = str(value)
            
#             # Format and sanitize the content
            
#             # Apply bullet formatting ONLY for keys specified in keys_that_are_itemize_lists
#             if key in ITEMIZE_LIST_KEYS:
#                 print(f"Formatting '{key}' as bullet points.")
#                 formatted_value = format_bullet_points(value)
#             else:
#                 # for sections that are Not lists (like summary), just strip whitespace
#                 formatted_value = value.strip()
#             sanitized_value = sanitize_latex_content(formatted_value)
#             processed_content[key] = sanitized_value
            
#         print("Content processing complete.")
#         # print("Parsed content:", parsed_content)
#         return processed_content
        
#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON from API response: {e}")
#         print("Raw response content:", content[:500] + "..." if len(content) > 500 else content)
#         return None


# def generate_tailored_content(base_resume_content, job_description_content, strategy=None):
#     """
#     Uses Hugging Face/ LiteLLM API to generate tailored content with different strategies
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
    
#     # Improved fallback with logging
#     if strategy not in prompt_strategies:
#         print(f"Warning: Strategy '{strategy}' not found. Falling back to 'ats' strategy.")
#         strategy = 'ats'  # Default fallback
    
#     prompt = prompt_strategies[strategy](base_resume_content, job_description_content)

#     try:
        
#         print(f"Sending request to DeepSeek-r1-0528-qwen3-8b via LiteLLM...")
#         response = completion(
#             model="openrouter/deepseek/deepseek-r1-0528-qwen3-8b",
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
#             max_tokens=1800,
#             temperature=0.5,
#             api_key = OPENROUTER_API_KEY
            
#         )

#         content = response.choices[0].message.content
#         print(f"API response received using {strategy} strategy")
        
#         return process_api_response(content)
                
#     except Exception as e:
#         print(f"An error occurred during API call: {str(e)}")
#         import traceback
#         print(traceback.format_exc())  # Print full stack trace for debugging
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

# def test_all_strategies(base_resume_content, job_description_content, output_prefix):
#     """
#     Test all four strategies and generate separate resumes for comparison
#     """
#     strategies = ['ats', 'value', 'story', 'technical']
    
#     for strategy in strategies:
#         print(f"\n--- Testing {strategy.upper()} Strategy ---")
#         tailored_content = generate_tailored_content(
#             base_resume_content, 
#             job_description_content, 
#             strategy=strategy
#         )
        
#         if tailored_content:
#             output_tex_path = os.path.join(OUTPUT_FOLDER, f"{output_prefix}_{strategy}_strategy.tex")
#             if generate_resume_file(BASE_RESUME_TEMPLATE_PATH, tailored_content, output_tex_path):
#                 compile_pdf(output_tex_path)

# # --- Main Logic ---
# def main():
#     # Create output folders if they don't exist
#     os.makedirs(JD_FOLDER, exist_ok=True)
#     os.makedirs(OUTPUT_FOLDER, exist_ok=True)

#     base_resume_content = load_file(BASE_RESUME_TEMPLATE_PATH)
#     if base_resume_content is None:
#         print("Base resume template not found. Make sure base_resume_template.tex exists.")
#         return

#     print("Enhanced Resume Tailoring System Starting...")
#     print("Available strategies: ATS-focused, Value-focused, Story-driven, Technical-depth")
#     print("Watching for new job descriptions in:", JD_FOLDER)
    
#     processed_jds = set()

#     while True:
#         current_jds = set([f for f in os.listdir(JD_FOLDER) if f.endswith(".txt")])
#         new_jds = current_jds - processed_jds

#         for jd_file_name in new_jds:
#             jd_file_path = os.path.join(JD_FOLDER, jd_file_name)
#             print(f"\nProcessing new job description: {jd_file_name}")

#             job_description_content = load_file(jd_file_path)
#             if job_description_content is None:
#                 print(f"Could not read job description from {jd_file_name}. Skipping.")
#                 processed_jds.add(jd_file_name)
#                 continue

#             output_file_name_base = os.path.splitext(jd_file_name)[0]
            
#             # Option 1: Auto-detect best strategy
#             print("\n=== Auto-detecting best strategy ===")
#             tailored_content = generate_tailored_content(base_resume_content, job_description_content)
            
#             if tailored_content:
#                 output_tex_path = os.path.join(OUTPUT_FOLDER, f"{output_file_name_base}_auto_tailored.tex")
#                 if generate_resume_file(BASE_RESUME_TEMPLATE_PATH, tailored_content, output_tex_path):
#                     compile_pdf(output_tex_path)
            
#             # Option 2: Generate all strategies for comparison (uncomment to enable)
#             # print("\n=== Generating all strategies for comparison ===")
#             # test_all_strategies(base_resume_content, job_description_content, output_file_name_base)

#             processed_jds.add(jd_file_name)

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
from litellm import completion
import re

# --- Configuration ---
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise EnvironmentError("OPENROUTER_API_KEY is not set in the environment or .env file. Please set it before running this script.")

BASE_RESUME_TEMPLATE_PATH = "base_resume_template.tex"
JD_FOLDER = "job_descriptions"
OUTPUT_FOLDER = "tailored_resumes"

# --- Base Resume Content (Your Original Skills and Summary) ---
BASE_SKILLS_CATEGORIES = {
    "Programming Languages": ["JavaScript", "TypeScript", "C++", "Python", "SQL", "Java"],
    "Tools and Frameworks": ["React.js", "Next.js", "Node.js", "Express.js", "Flask", "Django", "Socket.IO", "Redis", "GraphQL", "HTML", "Tailwind CSS", "REST APIs", "Redux/Recoil", "JWT", "OAuth", "Docker", "Kubernetes", "Git", "JIRA", "Unit Testing", "CI/CD"],
    "Cloud Skills": ["AWS services (EKS, Lambda, S3, ECR, EC2, VPCs, SNS, SQS, API Gateway, DynamoDB)", "Microservices", "GCP"],
    "Databases": ["PostgreSQL", "MongoDB", "DynamoDB", "Redis", "Elastic Search", "Firebase", "Database Optimization"],
    "Other": ["Full-Stack Development", "RESTful API Design", "Backend Architecture", "Agile", "Code Reviews", "System Design", "Problem-Solving"]
}

BASE_SUMMARY_TEMPLATE = "Full-Stack Software Engineer with nearly 3 years of experience specialising in {core_skills}. Proficient in building microservices, web applications, scaling Backend, RESTful APIs, and cloud-native solutions on AWS."

def extract_jd_keywords(job_description_content):
    """Extract relevant technical keywords from job description"""
    jd_lower = job_description_content.lower()
    
    # Common technical keywords to look for
    tech_keywords = [
        'java', 'python', 'javascript', 'typescript', 'react', 'node.js', 'spring boot',
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'microservices', 'rest api',
        'sql', 'nosql', 'mongodb', 'postgresql', 'redis', 'kafka', 'rabbitmq',
        'jenkins', 'ci/cd', 'git', 'linux', 'shell scripting', 'terraform',
        'prometheus', 'grafana', 'elk stack', 'system design', 'algorithms',
        'data structures', 'agile', 'scrum', 'devops', 'cloud computing',
        'machine learning', 'ai', 'graphql', 'express', 'flask', 'django',
        'vue.js', 'angular', 'spring', 'hibernate', 'junit', 'testing',
        'oauth', 'jwt', 'security', 'encryption', 'load balancing',
        'elastic search', 'distributed systems', 'high availability'
    ]
    
    found_keywords = []
    for keyword in tech_keywords:
        if keyword in jd_lower:
            found_keywords.append(keyword)
    
    return found_keywords

def generate_categorized_skills(jd_keywords):
    """Generate skills section maintaining categories while prioritizing JD keywords"""
    
    # Map JD keywords to categories
    keyword_to_category = {
        'java': 'Programming Languages',
        'python': 'Programming Languages', 
        'javascript': 'Programming Languages',
        'typescript': 'Programming Languages',
        'sql': 'Programming Languages',
        'c++': 'Programming Languages',
        
        'react': 'Tools and Frameworks',
        'react.js': 'Tools and Frameworks',
        'node.js': 'Tools and Frameworks',
        'express': 'Tools and Frameworks',
        'flask': 'Tools and Frameworks',
        'django': 'Tools and Frameworks',
        'spring boot': 'Tools and Frameworks',
        'spring': 'Tools and Frameworks',
        'docker': 'Tools and Frameworks',
        'kubernetes': 'Tools and Frameworks',
        'git': 'Tools and Frameworks',
        'jenkins': 'Tools and Frameworks',
        'ci/cd': 'Tools and Frameworks',
        'junit': 'Tools and Frameworks',
        'testing': 'Tools and Frameworks',
        'oauth': 'Tools and Frameworks',
        'jwt': 'Tools and Frameworks',
        'rest api': 'Tools and Frameworks',
        'graphql': 'Tools and Frameworks',
        'redux': 'Tools and Frameworks',
        'tailwind css': 'Tools and Frameworks',
        
        'aws': 'Cloud Skills',
        'azure': 'Cloud Skills',
        'gcp': 'Cloud Skills',
        'microservices': 'Cloud Skills',
        'cloud computing': 'Cloud Skills',
        'terraform': 'Cloud Skills',
        'prometheus': 'Cloud Skills',
        'grafana': 'Cloud Skills',
        'elk stack': 'Cloud Skills',
        
        'postgresql': 'Databases',
        'mongodb': 'Databases',
        'redis': 'Databases',
        'nosql': 'Databases',
        'elastic search': 'Databases',
        'firebase': 'Databases',
        'database optimization': 'Databases',
        
        'system design': 'Other',
        'algorithms': 'Other',
        'data structures': 'Other',
        'agile': 'Other',
        'scrum': 'Other',
        'devops': 'Other',
        'linux': 'Other',
        'shell scripting': 'Other',
        'problem-solving': 'Other',
        'full-stack development': 'Other',
        'backend architecture': 'Other',
        'code reviews': 'Other'
    }
    
    # Start with base skills
    enhanced_skills = {category: skills.copy() for category, skills in BASE_SKILLS_CATEGORIES.items()}
    
    # Add JD keywords to appropriate categories
    for keyword in jd_keywords:
        category = keyword_to_category.get(keyword.lower())
        if category and category in enhanced_skills:
            # Capitalize properly
            formatted_keyword = keyword.title() if keyword.lower() not in ['ci/cd', 'rest api', 'jwt', 'oauth', 'sql', 'nosql', 'ai', 'ml', 'aws', 'gcp', 'elk stack'] else keyword.upper() if keyword.lower() in ['sql', 'nosql', 'ai', 'ml', 'aws', 'gcp'] else keyword
            if formatted_keyword not in enhanced_skills[category]:
                enhanced_skills[category].append(formatted_keyword)
    
    # Generate LaTeX format
    latex_skills = []
    for category, skills in enhanced_skills.items():
        if skills:  # Only include categories with skills
            skills_str = ", ".join(skills)
            latex_skills.append(f"\\item\n\\textbf{{{category}:}} {skills_str}. \\\\\n\\vspace{{1pt}}")
    
    return "\n\n".join(latex_skills)

def generate_authentic_summary(jd_keywords, job_description_content):
    """Generate summary that maintains authenticity while incorporating JD keywords"""
    
    # Extract core skills mentioned in JD
    priority_skills = []
    skill_mapping = {
        'react': 'React.js',
        'node': 'Node.js', 
        'javascript': 'JavaScript',
        'typescript': 'TypeScript',
        'python': 'Python',
        'java': 'Java',
        'aws': 'AWS',
        'docker': 'Docker',
        'kubernetes': 'Kubernetes',
        'microservices': 'microservices',
        'rest': 'RESTful APIs',
        'full-stack': 'full-stack development',
        'backend': 'backend development',
        'frontend': 'frontend development'
    }
    
    for keyword in jd_keywords[:6]:  # Top 6 keywords
        for key, value in skill_mapping.items():
            if key in keyword.lower():
                if value not in priority_skills:
                    priority_skills.append(value)
                break
    
    # Default to current skills if no matches
    if not priority_skills:
        priority_skills = ["React.js", "Next.js", "Node.js", "TypeScript", "Python"]
    
    core_skills_str = ", ".join(priority_skills[:4])  # Keep it concise
    
    return BASE_SUMMARY_TEMPLATE.format(core_skills=core_skills_str)

def get_enhanced_prompt_strategy(base_resume_content, job_description_content):
    """
    Enhanced prompt strategy that maintains authenticity while optimizing for ATS
    """
    jd_keywords = extract_jd_keywords(job_description_content)
    
    return f"""
You are an expert ATS resume optimizer specializing in Software Engineer positions. Your task is to enhance resume sections while maintaining authenticity and the candidate's actual experience.

CRITICAL REQUIREMENTS:
1. MAINTAIN AUTHENTICITY: Do not fabricate experiences or skills
2. ENHANCE EXISTING CONTENT: Reword and optimize existing bullet points using JD terminology
3. INCORPORATE KEYWORDS NATURALLY: Use JD keywords where they genuinely fit
4. QUANTIFY ACHIEVEMENTS: Keep existing metrics, enhance where appropriate
5. PRESERVE CORE EXPERIENCES: Don't change the fundamental nature of each role

EXTRACTED JD KEYWORDS: {', '.join(jd_keywords[:15])}

Job Description:
---
{job_description_content}
---

Base Resume Content:
---
{base_resume_content}
---

SPECIFIC INSTRUCTIONS:
1. For each work experience section, REWRITE the existing bullet points. Each point should be a concise achievement. Separate each achievement with a newline and a bullet character '•'.
   - Use more impactful action verbs
   - Incorporate relevant JD keywords naturally
   - Maintain the same core achievements and metrics
   - Follow the pattern: Action Verb + Technology/Method + Quantifiable Result + Business Impact

2. For the projects section, enhance the existing project description with relevant JD keywords. Separate each point with a newline and a bullet character '•'.

3. DO NOT CREATE: New experiences, fake metrics, or completely different roles

OUTPUT REQUIREMENTS:
Return ONLY a valid JSON object with these keys:
- "summary": A 2-3 sentence summary (plain text, no bullet points).
- "skills": JSON object where keys are skill categories (e.g., "Programming Languages", "Tools and Frameworks") and values are comma-separated strings of relevant skills for that category (plain text).
- "scale_ai_experience": Enhanced bullet points for Scale AI role (separated by newlines and '•').
- "samsung_experience": Enhanced bullet points for Samsung role  (separated by newlines and '•').
- "amazon_experience": Enhanced bullet points for Amazon role (separated by newlines and '•').
- "paytm_mini": Enhanced project description having at max 2-3 sentences (separated by newlines and '•').


IMPORTANT: Return ONLY the raw JSON object without any markdown code blocks, explanations, or additional text.
Do not include ```json or ``` markers around your response.
"""

def process_enhanced_api_response(content, jd_keywords):
    """
    Process API response and add the generated skills and summary
    """
    from itemize_lists_keys import ITEMIZE_LIST_KEYS
    
    try:
        # Clean up the content
        if content.startswith("```json"):
            end_marker = content.rfind("```")
            if end_marker > 6:
                content = content[6:end_marker].strip()
            else:
                content = content[6:].strip()
        elif content.startswith("```"):
            end_marker = content.rfind("```")
            if end_marker > 3:
                content = content[3:end_marker].strip()
            else:
                content = content[3:].strip()
                
        parsed_content = json.loads(content)
        
        # Generate authentic summary and categorized skills
        authentic_summary = generate_authentic_summary(jd_keywords, "")
        categorized_skills = generate_categorized_skills(jd_keywords)
        
        # Add summary and skills to parsed content
        parsed_content["summary"] = authentic_summary
        parsed_content["skills"] = categorized_skills
        
        # Required keys
        required_keys = ["scale_ai_experience", "samsung_experience", "amazon_experience", "paytm_mini"]
        
        # Add missing keys with empty values
        for key in required_keys:
            if key not in parsed_content:
                print(f"Warning: Missing key '{key}' in response. Adding empty value.")
                parsed_content[key] = ""
        
        processed_content = {}
        
        # Process each value
        for key, value in parsed_content.items():
            if not isinstance(value, str):
                value = str(value)
            
            # Apply bullet formatting for itemize list keys
            if key in ITEMIZE_LIST_KEYS:
                print(f"Formatting '{key}' as bullet points.")
                formatted_value = format_bullet_points(value)
            else:
                formatted_value = value.strip()
                
            sanitized_value = sanitize_latex_content(formatted_value)
            processed_content[key] = sanitized_value
            
        print("Enhanced content processing complete.")
        return processed_content
        
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from API response: {e}")
        print("Raw response content:", content[:500] + "..." if len(content) > 500 else content)
        return None

def generate_enhanced_tailored_content(base_resume_content, job_description_content):
    """
    Generate tailored content using the enhanced approach
    """
    jd_keywords = extract_jd_keywords(job_description_content)
    print(f"Extracted JD keywords: {jd_keywords[:10]}...")  # Show first 10
    
    prompt = get_enhanced_prompt_strategy(base_resume_content, job_description_content)

    try:
        print(f"Sending request to DeepSeek-r1-0528-qwen3-8b via LiteLLM...")
        response = completion(
            model="openrouter/deepseek/deepseek-r1-0528-qwen3-8b",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume optimizer. Enhance existing content authentically while incorporating relevant keywords. Always return valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=2000,
            temperature=0.3,  # Lower temperature for more consistent output
            api_key=OPENROUTER_API_KEY
        )

        content = response.choices[0].message.content
        print(f"API response received")
        
        return process_enhanced_api_response(content, jd_keywords)
                
    except Exception as e:
        print(f"An error occurred during API call: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

# --- Helper Functions (keeping the existing ones) ---
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

def generate_resume_file(template_path, tailored_content, output_path):
    """Fills the Jinja2 template with tailored content and saves as a .tex file."""
    template_str = load_file(template_path)
    if template_str is None:
        return False

    template = Template(template_str)

    try:
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
        output_dir = os.path.dirname(tex_path)
        filename = os.path.basename(tex_path)
        
        print(f"Attempting to compile {filename} to PDF...")
        
        original_dir = os.getcwd()
        
        # Copy the resume.cls file to the output directory
        cls_source = os.path.join(original_dir, "resume.cls")
        cls_dest = os.path.join(output_dir, "resume.cls")
        
        if os.path.exists(cls_source):
            import shutil
            shutil.copy2(cls_source, cls_dest)
            print(f"Successfully copied resume.cls to {output_dir}")
        else:
            print(f"Warning: resume.cls not found at {cls_source}")
        
        os.chdir(output_dir)
        
        cmd = ['pdflatex', '-interaction=nonstopmode', filename]
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        os.chdir(original_dir)
        
        if process.returncode == 0:
            pdf_path = tex_path.replace('.tex', '.pdf')
            print(f"• PDF successfully generated at {pdf_path}")
            return True
        else:
            print(f"Error during pdflatex compilation:")
            print(f"Return Code: {process.returncode}")
            print(f"• PDF compilation failed for {tex_path}")
            return False
    except Exception as e:
        print(f"Exception during PDF compilation: {e}")
        if 'original_dir' in locals():
            os.chdir(original_dir)
        return False

# --- Main Logic ---
def main():
    os.makedirs(JD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    base_resume_content = load_file(BASE_RESUME_TEMPLATE_PATH)
    if base_resume_content is None:
        print("Base resume template not found. Make sure base_resume_template.tex exists.")
        return

    print("Enhanced Authentic Resume Tailoring System Starting...")
    print("Features: Categorized skills, authentic summaries, keyword optimization")
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
            
            print("\n=== Generating enhanced authentic resume ===")
            tailored_content = generate_enhanced_tailored_content(base_resume_content, job_description_content)
            
            if tailored_content:
                output_tex_path = os.path.join(OUTPUT_FOLDER, f"{output_file_name_base}_enhanced_tailored.tex")
                if generate_resume_file(BASE_RESUME_TEMPLATE_PATH, tailored_content, output_tex_path):
                    compile_pdf(output_tex_path)
                    
                    # Print preview of generated content
                    print("\n--- GENERATED CONTENT PREVIEW ---")
                    print("Summary:", tailored_content.get("summary", "")[:100] + "...")
                    print("Skills preview:", tailored_content.get("skills", "")[:150] + "...")
            
            processed_jds.add(jd_file_name)

        time.sleep(10)

if __name__ == "__main__":
    main()