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
from extract_original_sections import extract_original_sections, _latex_nodes_to_text

# --- Configuration ---
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise EnvironmentError("OPENROUTER_API_KEY is not set in the environment or .env file. Please set it before running this script.")

BASE_RESUME_TEMPLATE_PATH = "base_resume_template.tex" # path to the Jinja2 template with {{placeholders}} 
ORIGINAL_RESUME_PATH = "original_resume.tex" # Path to the original resume file
JD_FOLDER = "job_descriptions"
OUTPUT_FOLDER = "tailored_resumes"

ORIGINAL_RESUME_DETAILS = {}
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
        'elastic search', 'distributed systems', 'high availability',
        'scalability', 'performance tuning', 'api design', 'web services',
        'full-stack development', 'backend development', 'next.js', 'tailwind css',
        'redux', 'recoil', 'socket.io', 'websockets', 'graphql', 'firebase',
        'cloudformation', 'serverless', 'event-driven architecture', 'data pipelines',
        'cloudflare workers', 'nginx', 'genai', 'llm', 'large language models', 'openai',
        'openApi', 'newrelic', 'elk stack', 'observability', 'monitoring', 'logging', 'distributed tracing'
    ]
    
    found_keywords = []
    for keyword in tech_keywords:
        if keyword in jd_lower:
            found_keywords.append(keyword)
    
    return found_keywords


# --- IMPORTANT: Update generate_categorized_skills to accept LLM's structured output ---
# Original signature: def generate_categorized_skills(jd_keywords):
# New signature: def generate_categorized_skills(jd_keywords, llm_structured_skills):

def generate_categorized_skills(jd_keywords, llm_structured_skills):
    """
    Generate skills section maintaining categories while prioritizing JD keywords.
    Prioritizes structured skills from LLM, falls back to base categories.
    """
    
    # Start with base skills as a fallback, or if LLM didn't provide complete categories
    enhanced_skills = {category: skills.copy() for category, skills in BASE_SKILLS_CATEGORIES.items()}

    # Prioritize and merge skills from the LLM's structured output
    if isinstance(llm_structured_skills, dict):
        for category, skill_string in llm_structured_skills.items():
            if isinstance(skill_string, str):
                # Ensure the category exists in our base structure or add it
                if category not in enhanced_skills:
                    enhanced_skills[category] = []
                # Split LLM's comma-separated string and add to the category, avoiding duplicates
                for skill in [s.strip() for s in skill_string.split(',') if s.strip()]:
                    if skill not in enhanced_skills[category]:
                        enhanced_skills[category].append(skill)

    # Now, add JD keywords to appropriate categories, merging with existing
    keyword_to_category = {
        # ... (your existing keyword_to_category mapping) ...
        'java': 'Programming Languages', 'python': 'Programming Languages', 'javascript': 'Programming Languages',
        'typescript': 'Programming Languages', 'sql': 'Programming Languages', 'c++': 'Programming Languages',
        'react': 'Tools and Frameworks', 'react.js': 'Tools and Frameworks', 'node.js': 'Tools and Frameworks',
        'express': 'Tools and Frameworks', 'flask': 'Tools and Frameworks', 'django': 'Tools and Frameworks',
        'spring boot': 'Tools and Frameworks', 'spring': 'Tools and Frameworks', 'docker': 'Tools and Frameworks',
        'kubernetes': 'Tools and Frameworks', 'git': 'Tools and Frameworks', 'jenkins': 'Tools and Frameworks',
        'ci/cd': 'Tools and Frameworks', 'junit': 'Tools and Frameworks', 'testing': 'Tools and Frameworks',
        'oauth': 'Tools and Frameworks', 'jwt': 'Tools and Frameworks', 'rest api': 'Tools and Frameworks',
        'graphql': 'Tools and Frameworks', 'redux': 'Tools and Frameworks', 'tailwind css': 'Tools and Frameworks',
        'aws': 'Cloud Skills', 'azure': 'Cloud Skills', 'gcp': 'Cloud Skills', 'microservices': 'Cloud Skills',
        'cloud computing': 'Cloud Skills', 'terraform': 'Cloud Skills', 'prometheus': 'Cloud Skills',
        'grafana': 'Cloud Skills', 'elk stack': 'Cloud Skills',
        'postgresql': 'Databases', 'mongodb': 'Databases', 'redis': 'Databases', 'nosql': 'Databases',
        'elastic search': 'Databases', 'firebase': 'Databases', 'database optimization': 'Databases',
        'system design': 'Other', 'algorithms': 'Other', 'data structures': 'Other', 'agile': 'Other',
        'scrum': 'Other', 'devops': 'Other', 'linux': 'Other', 'shell scripting': 'Other',
        'problem-solving': 'Other', 'full-stack development': 'Other', 'backend architecture': 'Other', 'code reviews': 'Other'
    }

    for keyword in jd_keywords:
        category = keyword_to_category.get(keyword.lower())
        if category and category in enhanced_skills:
            formatted_keyword = keyword.title() if keyword.lower() not in ['ci/cd', 'rest api', 'jwt', 'oauth', 'sql', 'nosql', 'ai', 'ml', 'aws', 'gcp', 'elk stack'] else keyword.upper() if keyword.lower() in ['sql', 'nosql', 'ai', 'ml', 'aws', 'gcp'] else keyword
            if formatted_keyword not in enhanced_skills[category]:
                enhanced_skills[category].append(formatted_keyword)
    
    # Generate LaTeX format
    latex_skills = []
    for category, skills in enhanced_skills.items():
        if skills:  # Only include categories with skills
            
            # Sanitize the category name and the skills string BEFORE creating the LaTeX string
            sanitized_category = sanitize_latex_content(category)
            sanitized_skills_str = sanitize_latex_content(", ".join(skills))
            
            # Now, use the sanitized variables in the f-string
            latex_skills.append(f"\\item\n\\textbf{{{sanitized_category}:}} {sanitized_skills_str}. \\\\\n\\vspace{{1pt}}")
        
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
        'frontend': 'frontend development',
        'sql': 'SQL',
        'nosql': 'NoSQL',
        'graphql': 'GraphQL',
        'redis': 'Redis',
        'postgresql': 'PostgreSQL',
        'mongodb': 'MongoDB',
        'elasticsearch': 'Elastic Search',
        'firebase': 'Firebase',
        'jenkins': 'Jenkins',
        'ci/cd': 'CI/CD',
        'agile': 'Agile',
        'devops': 'DevOps',
        'cloud': 'Cloud Computing',
        'observability': 'Observability',
        'monitoring': 'Monitoring',
        'logging': 'Logging',
        'distributed tracing': 'Distributed Tracing',
        'llm': 'Large Language Models',
        'genai': 'Generative AI',
        'openai': 'OpenAI',
        'openapi': 'OpenAPI',
        'newrelic': 'New Relic',
        'sqs': 'Amazon SQS',
        'sns': 'Amazon SNS',
        'api gateway': 'API Gateway',
        'lambda': 'AWS Lambda',
        'dynamodb': 'Amazon DynamoDB',
        'vpc': 'Amazon VPC',
        's3': 'Amazon S3',
        'ec2': 'Amazon EC2',
        'cloudflare': 'Cloudflare',
        'cloudflare workers': 'Cloudflare Workers',
        'tailwind css': 'Tailwind CSS',
        'next.js': 'Next.js',
        'socket.io': 'Socket.IO',
        'recoil': 'Recoil',
        'unit testing': 'Unit Testing',
        'system design': 'System Design',
        'problem solving': 'Problem Solving',
        'data structures': 'Data Structures',
        'algorithms': 'Algorithms',
        'code reviews': 'Code Reviews',
        'security': 'Security',
        'encryption': 'Encryption',
        'load balancing': 'Load Balancing',
        'high availability': 'High Availability',
        'scalability': 'Scalability',
        'performance tuning': 'Performance Tuning',
        'api design': 'API Design',
        'web services': 'Web Services',
        'express': 'Express.js',
        'flask': 'Flask',
        'django': 'Django',
        'c++': 'C++',
        'kafka': 'Kafka',
        'rabbitmq': 'RabbitMQ',
        'linux': 'Linux',
    }
    
    for keyword in jd_keywords[:6]:  # Top 6 keywords
        for key, value in skill_mapping.items():
            if key in keyword.lower():
                if value not in priority_skills:
                    priority_skills.append(value)
                break
    
    # Default to current skills if no matches
    if not priority_skills:
        priority_skills = ['C++', "React.js", "Next.js", "Node.js", "TypeScript", "Python", "AWS"]
    
    core_skills_str = ", ".join(priority_skills[:4])  # Keep it concise
    
    return BASE_SUMMARY_TEMPLATE.format(core_skills=core_skills_str)

def get_enhanced_prompt_strategy(job_description_content, original_content_dict):
    """
    Enhanced prompt strategy that maintains authenticity while optimizing for ATS
    Now includes original experience and project details.
    """
    jd_keywords = extract_jd_keywords(job_description_content)
    
    # Format original content for the prompt
    scale_ai_orig = original_content_dict.get("scale_ai_original", "N/A")
    samsung_orig = original_content_dict.get("samsung_original", "N/A")
    amazon_orig = original_content_dict.get("amazon_original", "N/A")
    paytm_mini_orig = original_content_dict.get("paytm_mini_original", "N/A")
    original_skills_text = "\n".join([f"- {cat}: {skills}" for cat, skills in original_content_dict.get("original_categorized_skills", {}).items()])
    if not original_skills_text:
        original_skills_text = "N/A (Original categorized skills not found or extracted)."


    return f"""
You are an expert ATS resume optimizer specializing in Software Engineer positions. Your task is to enhance resume sections while maintaining authenticity and the candidate's actual experience.
Your goal is to optimize the resume content for ATS score by incorporating relevant keywords from the provided job description, while preserving the core achievements and metrics of the original content.

CRITICAL REQUIREMENTS:
1.  **AUTHENTICITY IS KEY:** You MUST base your rewritten content on the provided "Original Experience & Project Details." Do NOT invent new experiences, roles, or projects.
2.  **ENHANCEMENT, NOT FABRICATION:** Your task is to rephrase, expand, and optimize the *existing* bullet points by:
    -   Incorporating relevant keywords from the "Job Description."
    -   Using strong action verbs.
    -   Maintaining or enhancing existing quantifiable metrics (percentages, numbers, scale).
    -   Ensuring the core achievement, technology, and business impact of the original bullet point are preserved.
3.  **LAZY EVALUATION:** If an original bullet point is already highly relevant and impactful for the JD, you may return it as is or with minimal, precise adjustments.

EXTRACTED JD KEYWORDS: {', '.join(jd_keywords[:15])}

Job Description:
---
{job_description_content}
---

Original Experience & Project Details (Base for Enhancement):
---
Scale AI (Original):
{scale_ai_orig}

Samsung R&D (Original):
{samsung_orig}

Amazon (Original):
{amazon_orig}

Paytm-mini (Original):
{paytm_mini_orig}

Original Categorized Skills Reference (for populating the 'skills' section):
{original_skills_text}
---

SPECIFIC INSTRUCTIONS FOR OUTPUT:
1.  **Summary:** A concise 2-3 sentence summary (plain text, no bullet points) that highlights key skills relevant to the JD and author's experience.
2.  **Skills:** A JSON object where keys are skill categories (e.g., "Programming Languages", "Tools and Frameworks") and values are comma-separated strings of relevant skills for that category. Prioritize JD-mentioned technologies within categories. You are provided with the original categorized skills for reference; adapt these, ensuring all original categories are present unless clearly irrelevant to the JD.
    Original Categorized Skills Reference: 
    {original_skills_text}
3.  **Work Experience Sections (scale_ai_experience, samsung_experience, amazon_experience):** Enhance the *provided original bullet points* for these roles based on the enhancement rules above. Each point should be a concise achievement. Separate each point with a newline and a bullet character '•'.
4.  **Projects (Paytm-mini):** Rewrite the *provided original project description* based on the enhancement rules above. This should be a concise description (at max 2-3 sentences). Separate each point with a newline and a bullet character '•'.


OUTPUT REQUIREMENTS:
Return ONLY a valid JSON object with these keys:
- "summary": (string, plain text)
- "skills": A JSON object. Use ONLY these keys for categories: "Programming Languages", "Tools and Frameworks", "Cloud Skills", "Databases", "Other". The value for each key should be a list of relevant skills as strings. Prioritize JD-mentioned technologies.
- "scale_ai_experience": Enhanced bullet points for Scale AI role (separated by newlines and '•').
- "samsung_experience": Enhanced bullet points for Samsung R&D role (separated by newlines and '•').
- "amazon_experience": Enhanced bullet points for Amazon role (separated by newlines and '•').
- "paytm_mini": (string, '\\item ' prefixed project description)

IMPORTANT: Return ONLY the raw JSON object without any markdown code blocks, explanations, or additional text.
Do not include ```json or ``` markers around your response.
"""

def process_and_deduplicate_skills(skills_dict):
    """
    Cleans, de-duplicates, and standardizes skills within their categories.
    """
    if not isinstance(skills_dict, dict):
        return {}

    processed_skills = {}
    seen_skills = set() # Keep track of all skills seen across all categories

    # Define the desired order of categories
    category_order = ["Programming Languages", "Tools and Frameworks", "Cloud Skills", "Databases", "Other"]

    for category in category_order:
        if category in skills_dict:
            skills_list = skills_dict[category]
            if not isinstance(skills_list, list):
                continue # Skip if the value isn't a list

            unique_skills_in_category = []
            for skill in skills_list:
                # Normalize skill: lowercase and strip whitespace
                normalized_skill = skill.lower().strip()
                if normalized_skill and normalized_skill not in seen_skills:
                    # Capitalize for display, e.g., "react.js" -> "React.js"
                    # This is a simple capitalization, can be improved if needed
                    display_skill = skill.strip().capitalize() 
                    unique_skills_in_category.append(display_skill)
                    seen_skills.add(normalized_skill)
            
            if unique_skills_in_category:
                 processed_skills[category] = ", ".join(unique_skills_in_category)

    return processed_skills

from itemize_lists_keys import ITEMIZE_LIST_KEYS
import re
def process_enhanced_api_response(content, jd_keywords):
    """
    Process API response and properly parse the JSON content.
    Applies bullet formatting conditionally and LaTeX sanitization to all.
    Handles structured skills data specifically to preserve dictionary format for Jinja2.
    """
    print("Processing and sanitizing content for LaTeX...")

    try:
        # Strip any markdown code block markers (keep your existing logic for this)
        if content.startswith("```json"):
            end_marker = content.rfind("```")
            if end_marker > 6:  # 6 is the length of "```json"
                content = content[6:end_marker].strip()
            else:
                content = content[6:].strip()
        elif content.startswith("```"):
            end_marker = content.rfind("```")
            if end_marker > 3:  # 3 is the length of "```"
                content = content[3:end_marker].strip()
            else:
                content = content[3:].strip()

        # Validate JSON before further processing
        parsed_content = json.loads(content)

        # Define required keys for better error handling
        # Ensure all expected keys from your LLM prompt are listed here.
        required_keys = ["summary", "skills", "scale_ai_experience", "samsung_experience", "amazon_experience", "paytm_mini"]
        # Add other keys like "achievements" if they are expected from LLM and in template

        # Initialize processed_content - this will hold the data ready for the Jinja2 template
        processed_content = {}

        # --- Handle the 'skills' key specifically first ---
        llm_generated_skills_dict = parsed_content.get("skills", {})
        if not isinstance(llm_generated_skills_dict, dict):
            print(f"Warning: LLM did not return skills as a dictionary. Setting to empty dictionary or using a fallback strategy.")
            llm_generated_skills_dict = {} # Ensure it's a dict for safety

        # Generate the skills data in the format expected by the Jinja2 template.
        # This means `generate_categorized_skills` should ideally return the structured dictionary,
        # and then the sanitization of its values (category names, skill strings) happens here.
        # For the provided `generate_categorized_skills` which returns a LaTeX string,
        # we need to slightly adjust how `skills` is handled to pass a dictionary.
        # Assuming your prompt instructs the LLM to return skills like:
        # {"Programming Languages": "Python, Java", "Tools": "Docker, K8s"}

        # If `generate_categorized_skills` in your code already returns a dictionary,
        # then directly use its output. If it returns a LaTeX string, we need to adapt.
        # Based on your definition of generate_categorized_skills, it creates LaTeX output directly.
        # To make it work with the Jinja2 loop, we need the *raw, categorized* skills.
        # So, instead of calling `generate_categorized_skills` to produce LaTeX string for `skills` key,
        # we will directly use the `llm_generated_skills_dict` after sanitizing its components.

        processed_skills_for_template = {}
        if isinstance(llm_generated_skills_dict, dict):
            for category, skill_string_or_list in llm_generated_skills_dict.items():
                sanitized_category = sanitize_latex_content(category.strip())
                if isinstance(skill_string_or_list, list):
                    # If LLM returns a list of skills, join them into a string
                    sanitized_skill_string = sanitize_latex_content(", ".join([s.strip() for s in skill_string_or_list if s.strip()]))
                elif isinstance(skill_string_or_list, str):
                    # If LLM returns a comma-separated string, sanitize it directly
                    sanitized_skill_string = sanitize_latex_content(skill_string_or_list.strip())
                else:
                    print(f"Warning: Unexpected type for skill value in category '{category}'. Skipping.")
                    continue
                processed_skills_for_template[sanitized_category] = sanitized_skill_string
        processed_content["skills"] = processed_skills_for_template


        # --- Process other keys from parsed_content ---
        for key in required_keys:
            if key == "skills": # Already handled above, skip this in the general loop
                continue

            value = parsed_content.get(key, "")
            if not isinstance(value, str):
                print(f"Warning: Value for '{key}' is not a string. Converting to string.")
                value = str(value)

            if key in ITEMIZE_LIST_KEYS:
                # Apply bullet formatting and then sanitize for itemized sections
                print(f"Formatting '{key}' as bullet points.")
                formatted_value = format_bullet_points(value)
            else:
                # For plain text keys like 'summary'
                formatted_value = value.strip()

            sanitized_value = sanitize_latex_content(formatted_value)
            processed_content[key] = sanitized_value

        print("Content processing complete.")
        print("Processed content: ", processed_content) # This print should now show skills as a dictionary
        return processed_content # This `processed_content` is passed to generate_resume_file

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from API response: {e}")
        print("Raw response content:", content[:500] + "..." if len(content) > 500 else content)
        return None
    except Exception as e:
        print(f"An error occurred during content processing: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None


# --- Update generate_enhanced_tailored_content to pass original_content_dict ---
def generate_enhanced_tailored_content(job_description_content, original_content_dict):
    """
    Generate tailored content using the enhanced approach
    """
    jd_keywords = extract_jd_keywords(job_description_content)
    print(f"Extracted JD keywords: {jd_keywords[:10]}...")
    
    # Pass original_content_dict to the prompt strategy
    prompt = get_enhanced_prompt_strategy(job_description_content, original_content_dict)

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
            temperature=0.3,
            api_key=OPENROUTER_API_KEY
        )

        content = response.choices[0].message.content
        print(f"API response received")
        
        # Pass jd_keywords to process_enhanced_api_response as it might be used there
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
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        print(f"pdflatex output:\n{process.stdout}")
        print(f"pdflatex stderr:\n{process.stderr}")
        if process.returncode != 0:
            print(f"pdflatex return code: {process.returncode}")
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

    # Load original resume content and extract details once at the start
    original_resume_latex_content = load_file(ORIGINAL_RESUME_PATH)
    if original_resume_latex_content is None:
        print(f"Original resume not found. Make sure {ORIGINAL_RESUME_PATH} exists.")
        return

    global ORIGINAL_RESUME_DETAILS # Populate the global variable
    ORIGINAL_RESUME_DETAILS = extract_original_sections(original_resume_latex_content)
    if not ORIGINAL_RESUME_DETAILS:
        print("Warning: Could not extract any sections from the original resume. Proceeding without original content for enhancement.")

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
            # Pass the extracted original content to the generation function
            tailored_content = generate_enhanced_tailored_content(job_description_content, ORIGINAL_RESUME_DETAILS)
            
            if tailored_content:
                output_tex_path = os.path.join(OUTPUT_FOLDER, f"{output_file_name_base}_enhanced_tailored.tex")
                # When calling generate_resume_file, we still use BASE_RESUME_TEMPLATE_PATH
                # because it contains the Jinja2 placeholders.
                if generate_resume_file(BASE_RESUME_TEMPLATE_PATH, tailored_content, output_tex_path):
                    compile_pdf(output_tex_path)
                    
                    # Print preview of generated content
                    print("\n--- GENERATED CONTENT PREVIEW ---")
                    print("Summary:", tailored_content.get("summary", "")[:100] + "...")
                    print("Skills preview:", str(tailored_content.get("skills", {}))[:150] + "...")
            
            processed_jds.add(jd_file_name)

        time.sleep(10)

if __name__ == "__main__":
    main()
