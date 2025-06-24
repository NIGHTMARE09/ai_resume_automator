# import re

# def extract_original_sections(latex_content):
#     """
#     Extracts original bullet points for specific experience and project sections
#     from a LaTeX resume content string.
#     """
#     original_sections = {}

#     # Helper to clean up common LaTeX directives within bullet points
#     def clean_item_content(content_block):
#         # Remove \vspace and \itemsep directives
#         cleaned = re.sub(r'\\vspace\{.*?\}|\s*\\itemsep.*?\{\}', '', content_block)
#         # Remove extraneous newlines that are not \\
#         cleaned = re.sub(r'(?<!\\)\n+', ' ', cleaned).strip() # Replace single newlines not preceded by \ with space
#         # Normalize multiple spaces
#         cleaned = re.sub(r'\s+', ' ', cleaned).strip()
#         # Ensure each \item starts a new line for easier LLM processing
#         cleaned = re.sub(r'\\item\s*', r'\n\\item ', cleaned).strip()
#         return cleaned.strip() # Final strip

#     # Define patterns for each section. Captures content within \begin{itemize}...\end{itemize}
#     # re.DOTALL makes '.' match newlines
#     section_patterns = {
#         "scale_ai_original": r'\\textbf\{Scale AI\}\(Contractual Role\).*?\\begin\{itemize\}(.*?)\\end\{itemize\}',
#         "samsung_original": r'\\textbf\{Samsung R\\&D Institute Bangalore\}.*?\\begin\{itemize\}(.*?)\\end\{itemize\}',
#         "amazon_original": r'\\textbf\{Amazon\}.*?\\begin\{itemize\}(.*?)\\end\{itemize\}',
#         "paytm_mini_original": r'\\textbf\{Paytm-mini\}.*?\\begin\{itemize\}(.*?)\\end\{itemize\}',
#     }

#     for key, pattern in section_patterns.items():
#         match = re.search(pattern, latex_content, re.DOTALL)
#         if match:
#             # Clean and store the captured content
#             original_sections[key] = clean_item_content(match.group(1))

#     # Also extract original categorized skills for the prompt reference
#     match_skills = re.search(
#         r'\\begin\{rSection\}\{SKILLS\}(.*?)\\end\{rSection\}',
#         latex_content, re.DOTALL
#     )
#     if match_skills:
#         skills_block = match_skills.group(1)
#         skill_categories = {}
#         # This regex looks for \item\s*\textbf{Category Name}: (content)
#         for cat_match in re.finditer(
#             r'\\item\s*\\textbf\{(.+?):\}(.*?)(?:\\\\\s*\\vspace\{.*\}|\s*\\item\s*\\textbf\{|$)',
#             skills_block, re.DOTALL
#         ):
#             category = cat_match.group(1).strip()
#             skills_text = cat_match.group(2).strip()
#             # Remove LaTeX commands within skill text (e.g., \\vspace, \\itemsep, \\\\)
#             skills_text = re.sub(r'\\vspace\{.*?\}|\s*\\itemsep.*?\{\}|\\\\\s*', '', skills_text).strip()
#             skill_categories[category] = skills_text
#         original_sections["original_categorized_skills"] = skill_categories
        
#     return original_sections



import re
from pylatexenc.latexwalker import LatexWalker, LatexCharsNode, LatexMacroNode, LatexEnvironmentNode
from pylatexenc.latexwalker import LatexGroupNode, LatexSpecialsNode, LatexCommentNode

def _latex_nodes_to_text(nodelist):
    """
    Converts a list of LatexWalker nodes to plain text, handling basic LaTeX commands
    and environments. More robust than simple regex.
    """
    text_parts = []
    if nodelist is None:
        return ""

    for node in nodelist:
        if isinstance(node, LatexCharsNode):
            text_parts.append(node.chars)
        elif isinstance(node, LatexMacroNode):
            # Handle common macros for formatting or newlines
            if node.macroname == 'item':
                if text_parts and text_parts[-1] != "\\item ": # Avoid double \item if already added
                    text_parts.append("\\item ")
            elif node.macroname == '\\': # Newline
                text_parts.append("\n")
            elif node.macroname in ['textbf', 'textit', 'textunderscore']: # Basic formatting, extract content
                if node.nodeargd and node.nodeargd.argnlist:
                    text_parts.append(_latex_nodes_to_text(node.nodeargd.argnlist[0]))
            else:
                # For other macros, just include their name or argument if they have one
                # For example, \faPhone might be handled by stripping or converting to unicode later
                if node.macroname in ['faPhone', 'faEnvelope', 'faLinkedin', 'faCode']:
                    pass # Ignore font awesome icons in text extraction
                elif node.nodeargd and node.nodeargd.argnlist:
                    text_parts.append(_latex_nodes_to_text(node.nodeargd.argnlist[0]))
                # else:
                #     text_parts.append(f"\\{node.macroname}") # Include macro name for debugging if needed
        elif isinstance(node, LatexEnvironmentNode):
            # Recursively handle content within environments
            if node.environmentname == 'itemize':
                # Process items inside the itemize environment
                items_content = []
                for item_node in node.nodelist:
                    if isinstance(item_node, LatexMacroNode) and item_node.macroname == 'item':
                        # Each item content
                        item_text = _latex_nodes_to_text(item_node.nodeargd.argnlist[0]) if item_node.nodeargd else ""
                        items_content.append(item_text)
                text_parts.append("\n".join(f"\\item {item}" for item in items_content if item))
            elif node.environmentname == 'rSection': # Special section environment
                 text_parts.append(_latex_nodes_to_text(node.nodelist))
            else:
                text_parts.append(_latex_nodes_to_text(node.nodelist))
        elif isinstance(node, LatexGroupNode):
            text_parts.append(_latex_nodes_to_text(node.nodelist))
        elif isinstance(node, LatexCommentNode):
            pass # Ignore comments
        # Add more node types as needed

    return "".join(text_parts).strip()


def extract_original_sections(latex_content):
    """
    Extracts original content for specific sections from a LaTeX resume
    using pylatexenc.
    """
    lw = LatexWalker(latex_content)
    nodelist, _, _ = lw.get_latex_nodes()

    extracted_sections = {
        "scale_ai_original": "",
        "samsung_original": "",
        "amazon_original": "",
        "paytm_mini_original": "",
        "original_categorized_skills": {} # This will be a dictionary
    }

    current_section = None
    for node in nodelist:
        # Find major sections (EXPERIENCE, PROJECTS, SKILLS)
        if isinstance(node, LatexMacroNode) and node.macroname == 'section*':
            section_title_nodes = node.nodeargd.argnlist[0] if node.nodeargd else None
            section_title = _latex_nodes_to_text(section_title_nodes).strip().upper()
            current_section = section_title
        elif isinstance(node, LatexEnvironmentNode) and node.environmentname == 'rSection':
            # Check for skills section within rSection (common in resume templates)
            # Assuming 'SKILLS' is the title of an rSection
            env_title_nodes = None
            if node.nodeargd and node.nodeargd.argnlist:
                env_title_nodes = node.nodeargd.argnlist[0]
            env_title = _latex_nodes_to_text(env_title_nodes).strip().upper() if env_title_nodes else None

            if env_title == "SKILLS":
                # Find itemize environment within the SKILLS rSection
                for sub_node in node.nodelist:
                    if isinstance(sub_node, LatexEnvironmentNode) and sub_node.environmentname == 'itemize':
                        for item_node in sub_node.nodelist:
                            if isinstance(item_node, LatexMacroNode) and item_node.macroname == 'item':
                                item_content_nodes = item_node.nodeargd.argnlist[0] if item_node.nodeargd else None
                                item_text = _latex_nodes_to_text(item_content_nodes).strip()
                                # Try to parse skill categories (e.g., \textbf{Category}: skill1, skill2)
                                match = re.match(r'\\item\\textbf\{([^}]+)\}:\s*(.*)', item_text)
                                if match:
                                    category = match.group(1).strip()
                                    skills_str = match.group(2).strip()
                                    extracted_sections["original_categorized_skills"][category] = [s.strip() for s in skills_str.split(',')]
                                else:
                                    # If not categorized, add to a general 'Other' category or process as raw text
                                    if "Other" not in extracted_sections["original_categorized_skills"]:
                                        extracted_sections["original_categorized_skills"]["Other"] = []
                                    # Ensure we don't duplicate \\item prefix if it's already there
                                    cleaned_item_text = item_text.lstrip('\\item ').strip()
                                    if cleaned_item_text:
                                        extracted_sections["original_categorized_skills"]["Other"].append(cleaned_item_text)

        # Look for specific company/project names and extract their itemize content
        if current_section == "EXPERIENCE":
            if isinstance(node, LatexMacroNode) and node.macroname == 'textbf':
                company_name_nodes = node.nodeargd.argnlist[0] if node.nodeargd else None
                company_name = _latex_nodes_to_text(company_name_nodes).strip()

                # Find the next itemize environment for this company
                next_node_is_itemize = False
                for i, n in enumerate(nodelist):
                    if n == node:
                        # Find the first itemize environment after the current company name
                        for sub_n in nodelist[i:]:
                            if isinstance(sub_n, LatexEnvironmentNode) and sub_n.environmentname == 'itemize':
                                itemize_content = _latex_nodes_to_text(sub_n.nodelist)
                                if "Scale AI" in company_name:
                                    extracted_sections["scale_ai_original"] = itemize_content
                                elif "Samsung R&D Institute Bangalore" in company_name:
                                    extracted_sections["samsung_original"] = itemize_content
                                elif "Amazon" in company_name:
                                    extracted_sections["amazon_original"] = itemize_content
                                next_node_is_itemize = True
                                break # Found itemize for this company
                        if next_node_is_itemize:
                            break # Break outer loop too

        elif current_section == "PROJECTS":
            if isinstance(node, LatexMacroNode) and node.macroname == 'textbf':
                project_name_nodes = node.nodeargd.argnlist[0] if node.nodeargd else None
                project_name = _latex_nodes_to_text(project_name_nodes).strip()
                if "Paytm-mini" in project_name:
                    # Find the next itemize environment for this project
                    next_node_is_itemize = False
                    for i, n in enumerate(nodelist):
                        if n == node:
                            for sub_n in nodelist[i:]:
                                if isinstance(sub_n, LatexEnvironmentNode) and sub_n.environmentname == 'itemize':
                                    itemize_content = _latex_nodes_to_text(sub_n.nodelist)
                                    extracted_sections["paytm_mini_original"] = itemize_content
                                    next_node_is_itemize = True
                                    break
                            if next_node_is_itemize:
                                break

    return extracted_sections

# Example Usage (for testing the module directly)
if __name__ == '__main__':
    # This is a sample LaTeX content. Replace with content from your original_resume.tex
    # Make sure this content truly has the original bullet points, not Jinja2 placeholders.
    sample_latex_content = r"""
\documentclass{resume} % Use the custom resume.cls style

\usepackage[left=0.4 in,top=0.55in,right=0.4 in,bottom=0.4in]{geometry} % Document margins
\usepackage{xcolor} % For color
\usepackage{titlesec}
\usepackage{tabularx}
\usepackage{fontawesome}
\usepackage[T1]{fontenc} % Use T1 font encoding

\name{Shivam Jha} % Your name

\address{
 \faPhone \hspace{0.1cm} \href{tel:+91 8003127994}{+91 8003127994} \\
 \faEnvelope \hspace{0.1cm} \href{mailto:Shivamjha.1299@gmail.com}{Shivamjha.1299@gmail.com} \\
 \faLinkedin \hspace{0.1cm} \href{https://linkedin.com/in/shivam-jha-0009/}{shivam-jha-0009} \\
 \faCode \hspace{0.1cm} \href{https://leetcode.com/Nightmare9}{Leetcode} \\
  \faCode \hspace{0.1cm} \href{https://www.codechef.com/users/nightmare_9}{CodeChef}
}

\newcommand{\tab}[1]{\hspace{.2667\textwidth}\rlap{##1}} 
\newcommand{\itab}[1]{\hspace{0em}\rlap{##1}}
\renewcommand{\normalsize}{\fontsize{9}{3}\selectfont}

\begin{document}


%----------------------------------------------------------------------------------------
%	SUMMARY
%---------------------------------------------------------

\begin{rSection}{SUMMARY}
 \vspace{-2pt}
Full-Stack Software Engineer with nearly 3 years of experience specialising in React.js, Next.js, Node.js, TypeScript, and Python. I'm proficient in building microservices, web applications, scaling Backend, RESTful APIs, and cloud-native solutions on AWS.
\end{rSection}
%----------------------------------------------------------------------------------------
% WORK EXPERIENCE SECTION
%----------------------------------------------------------------------------------------
 \vspace{-5pt}
\begin{rSection}{EXPERIENCE}

\textit{Software Engineer} \hfill December 2023 - Present\\
\textbf{Scale AI} (Contractual Role)\hfill \textit{Remote, US}
 \begin{itemize}
    \vspace{-1pt} % Adjust the space as needed
    \itemsep -3pt {} 
    \item Developed and maintained full-stack web applications using React.js, Next.js and TypeScript, implementing SSR and API routes to improve performance by 22\%.
    \item Built RESTful APIs using Node.js/Express and integrated third-party services, achieving 5/5 accuracy ratings in evaluation projects.
    \item Implemented responsive UI components with React hooks and context API, following modern frontend architecture principles.
    \item Created reusable component libraries and custom hooks, improving development efficiency across multiple projects.

    \item Optimized PostgreSQL database interactions to efficiently manage and query large datasets.
    \item Collaborated effectively with cross-functional teams across US time zones, demonstrating excellent remote work capabilities.
 \end{itemize}

\textit{Software Engineer} \hfill \textit{March 2023 - December 2023} \\
\textbf{Samsung R\&D Institute Bangalore} \hfill \textit{Bengaluru, India}
\begin{itemize}
    \vspace{-1pt}
    \itemsep -3.5pt {}
    \item Introduced a React Web-Chat App for 10,000+ users, improving internal communication and user experience.
    \item Revamped backend infrastructure with Node.js, Socket.IO, and Express, resulting in a 25\% improvement in application performance.
    \item Led containerization and deployment of 15+ microservices using Docker and Kubernetes, attaining 98\% service availability on AWS EKS clusters, efficiently handling 2x peak traffic volume.
    \item Implemented robust deployment, replication, auto-healing, and auto-scaling strategies for Kubernetes clusters, leveraging Kong gateway for API rate limiting and decreasing API latency by 15\%.
    \item Enhanced application security by integrating Bcrypt, JWT, OAuth, and upgrading encryption with Libsodium, significantly reducing unauthorized access attempts and addressing security vulnerabilities.
\end{itemize}


 
\textit{Software Development Engineer Intern} \hfill January 2022 - July 2022\\
\textbf{Amazon} \hfill \textit{Bengaluru, India}
 \begin{itemize}
    \vspace{-1pt} % Adjust the space as needed
    \itemsep -4pt {}
    \item Optimized large-dataset (800TB-1.5PB) computation time using Python, Ray, React, TypeScript \& Java, significantly boosting service efficiency and scalability.
    \item Improved Data Quality Standards, achieving 13\% monthly cost savings by streamlining calculations with Ray and enhancing data accessibility with Amazon DynamoDB.
    \item Developed a React front-end to visualise Marketplace tables Data Quality statistics, improving decision-making.
\end{itemize}


\end{rSection} 


%----------------------------------------------------------------------------------------
% PROJECTS SECTION
%----------------------------------------------------------------------------------------
\begin{rSection}{PROJECTS}
\textbf{Paytm-mini} \hfill \textit{Side Project}
\begin{itemize}
    \vspace{-1pt} % Adjust the space as needed
    \itemsep -3pt {}
    \item Built full-stack payments app (TypeScript, React, Recoil, Vite, Tailwind) with reusable UI for transfers \& dashboard; secured with JWT auth (Node.js backend) \& Postman API validation.
    \item Deployed backend on AWS; built responsive features: debounced search, live balance, and validated transfers with error handling.
\end{itemize}
\end{rSection}




%----------------------------------------------------------------------------------------
% SKILLS SECTION
%----------------------------------------------------------------------------------------
\begin{rSection}{SKILLS}
\begin{itemize}
\itemsep -3pt {}
\item
\textbf{Programming Languages:} JavaScript, TypeScript, C++, Python, SQL, Java (Intermediate). \\
\vspace{1pt} % Adjust the vertical space as needed

\item
\textbf{Tools and Frameworks:} React.js, Next.js, Node.js, Express.js, Flask, Django, Socket.IO, Redis, GraphQL, HTML, Tailwind CSS, REST APIs, Redux/Recoil, JWT, OAuth, Docker, Kubernetes, Git, JIRA, Unit Testing, CI/CD. \\
\vspace{1pt} % Adjust the vertical space as needed

\item
\textbf{Cloud Skills:} AWS services (EKS, Lambda, S3, ECR, EC2, VPCs, SNS, SQS, API Gateway, DynamoDB), Microservices, GCP. \\
\vspace{1pt} % Adjust the vertical space as needed

\item
\textbf{Databases:} PostgreSQL, MongoDB, DynamoDB, Redis, Elastic Search, Firebase, Database Optimization. \\
\vspace{1pt} % Adjust the space as needed

\item
\textbf{Other:} Full-Stack Development, RESTful API Design, Backend Architecture, Agile, Code Reviews, System Design, Problem-Solving. \\
\end{itemize}
\end{rSection}

% ----------------------------------------------------------------------------------------
% EDUCATION SECTION
% ----------------------------------------------------------------------------------------

\begin{rSection}{Education}

{\bf Indian Institute of Information Technology, Lucknow} \hfill {July 2018 - May 2022} \\
    % \vspace{-1pt} % Adjust the space as needed
    \itemsep -3pt {}
    \vspace{-5pt} % Adjust the space as needed
\begin{itemize}
    \item Bachelor of Technology in Information Technology, CGPA: 8.1. \\
    \vspace{-3pt} % Adjust the space as needed
    \item Coursework: Data Structures and Algorithms, Web Development, DBMS, OS, Computer Networks, System Design. \\
\end{itemize}

\end{rSection}

%----------------------------------------------------------------------------------------
% ACHIEVEMENTS SECTION
%----------------------------------------------------------------------------------------
 \vspace{-5pt}
\begin{rSection}{Achievements} 
\begin{itemize}
% \itemsep 1pt {} 
\vspace{3pt}
    \item Achieved \textbf{Samsung Pro Certified} status by passing the \textbf{SWC Pro Test} and receiving a bonus for this accomplishment.
    \item Ranked \textbf{132} globally in \textbf{CodeChef June LunchTime} 2021 among \textbf{4500+} contestants.
    \vspace{-3pt} % Adjust the space as needed
    \item Awarded a global rank of \textbf{1032} in \textbf{Google KickStart} 2021 Round D from \textbf{15000+} participants.
    \vspace{-3pt} % Adjust the space as needed
    \item Secured \textbf{9th} place globally in the Code Benders competition out of \textbf{900+} participants.
    \vspace{-3pt} % Adjust the space as needed
\end{itemize}
\end{rSection}

\end{document}
"""
    extracted_data = extract_original_sections(sample_latex_content)
    import json
    print(json.dumps(extracted_data, indent=2))

    # Expected output format for experience/project bullet points
    # should be strings where each bullet point is prefixed with \\item
    # e.g. "scale_ai_original": "\\item Developed a comprehensive React web application...\\item Modernized backend infrastructure..."
    # And original_categorized_skills should be a dictionary.
