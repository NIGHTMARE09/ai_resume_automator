# AI-Powered Resume Automator

## Table of Contents
- [About](#about)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## About

The AI-Powered Resume Automator is a Python-based application designed to streamline the resume tailoring process for specific job descriptions. It leverages advanced Large Language Models (LLMs) to dynamically generate and optimize your resume content, ensuring it aligns perfectly with the requirements of various job postings.

This tool aims to enhance your resume's impact and ATS (Applicant Tracking System) compatibility by intelligently incorporating relevant keywords, rephrasing achievements, and presenting your experience in a compelling, job-specific manner while preserving authenticity.

## Features

-   **Intelligent Content Generation**: Utilizes an LLM (DeepSeek-r1-0528-qwen3-8b via OpenRouter) to tailor resume sections (summary, skills, experience) based on provided job descriptions.
-   **Dynamic Skill Categorization**: Automatically extracts keywords from job descriptions and generates a categorized skills section based on predefined skill sets.
-   **Authentic Summary Creation**: Generates a concise and impactful summary tailored to the job description, built upon a base template and key skills.
-   **Automated LaTeX Formatting**: Transforms the LLM-generated content into a professional LaTeX document, ensuring correct resume structure and styling.
-   **PDF Compilation**: Automatically compiles the generated LaTeX `.tex` file into a PDF document, ready for submission.
-   **Job Description Monitoring**: Monitors a designated folder for new job description text files and processes them automatically.
-   **Experience Enhancement**: Rewrites and optimizes existing bullet points for various experience sections (e.g., Scale AI, Samsung, Amazon, Side Projects) to highlight impact and relevance.

## Technology Stack

-   **Python**: Core programming language for the application logic.
-   **Jinja2**: Templating engine for dynamic LaTeX document generation.
-   **LiteLLM**: For simplified API calls to various LLMs, routing requests to OpenRouter.
-   **DeepSeek-r1-0528-qwen3-8b**: The Large Language Model used for content generation (accessed via OpenRouter).
-   **LaTeX (pdflatex)**: Document preparation system for generating high-quality PDF resumes.
-   **python-dotenv**: For managing environment variables (e.g., API keys).
-   **re (Python Regex)**: For robust text parsing and formatting.

## Setup and Installation

Follow these steps to get the project up and running on your local machine.

### Prerequisites

*   **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
*   **Git**: [Download Git](https://git-scm.com/downloads)
*   **A LaTeX Distribution**:
    *   **MiKTeX** (Windows): [Download MiKTeX](https://miktex.org/download)
    *   **TeX Live** (Linux/macOS): [Download TeX Live](https://www.tug.org/texlive/acquire-netinstall.html)
    *   Ensure `pdflatex` is installed and accessible in your system's PATH.
*   **OpenRouter API Key**: Obtain a free API key from [OpenRouter.ai](https://openrouter.ai/). Note that usage may incur costs or be subject to free tier limits; ensure you have sufficient credits.

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/NIGHTMARE09/ai_resume_automator.git
    cd ai_resume_automator
    ```
    *(Assuming your repo is named `ai_resume_automator` under your GitHub username `NIGHTMARE09` as per [this memory](https://github.com/NIGHTMARE09/ai_resume_automator))*

2.  **Create a Python virtual environment and activate it:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install project dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (You may need to create a `requirements.txt` file with `pip freeze > requirements.txt` after manually installing `litellm`, `jinja2`, `python-dotenv`, `huggingface_hub` if not already present. Based on your code, `litellm` and `jinja2` are definitely needed.)

4.  **Configure API Key:**
    Create a file named `.env` in the root directory of the project and add your OpenRouter API key:
    ```env
    OPENROUTER_API_KEY="sk-your-openrouter-api-key"
    ```

5.  **Place `resume.cls`:**
    Ensure the `resume.cls` LaTeX class file is present in the root directory of your project, alongside `base_resume_template.tex`. This file defines the styling of your resume. ([D:\New_Projects\resume-automator\resume.cls](file:///D:\New_Projects\resume-automator\resume.cls))

6.  **Update `base_resume_template.tex`**:
    Verify that your [base_resume_template.tex](file:///D:\New_Projects\resume-automator\base_resume_template.tex) has the correct Jinja2 placeholders (`{{ summary }}`, `{{ skills }}`, `{{ scale_ai_experience }}`, etc.) and the Jinja2 loop for skills as discussed in our chat.

## Usage

1.  **Prepare Job Descriptions:**
    Place your job descriptions as plain text files (`.txt`) inside the `job_descriptions/` folder. For example, `job_descriptions/Amazon_SDE.txt`.

2.  **Run the Automator:**
    From your project's root directory (with the virtual environment activated), run the main script:
    ```bash
    python tailor_resume.py
    ```
    The script will monitor the `job_descriptions/` folder for new files.

3.  **View Output:**
    Tailored LaTeX files (`.tex`) and compiled PDF resumes (`.pdf`) will be generated and saved in the `tailored_resumes/` folder. The filenames will be based on your input job description filenames (e.g., `Amazon_SDE_enhanced_tailored.tex`, `Amazon_SDE_enhanced_tailored.pdf`).

## Project Structure
.
├── job_descriptions/                  # Input folder for job description text files
   └── Amazon_SDE.txt
├── tailored_resumes/                  # Output folder for generated .tex and .pdf resumes
   └── Amazon_SDE_enhanced_tailored.tex
   └── Amazon_SDE_enhanced_tailored.pdf
├── base_resume_template.tex           # LaTeX template for resume structure (with Jinja2 placeholders)
├── resume.cls                         # LaTeX class file for resume styling
├── tailor_resume.py                   # Main script to process JDs, call LLM, and generate resumes
├── format_bullet_points.py            # Python module for robust bullet point formatting
├── sanitize_latex.py                  # Python module for sanitizing text for LaTeX compatibility
├── itemize_lists_keys.py              # Defines constants for keys to be treated as itemized lists
├── .env                               # Environment variables (e.g., OPENROUTER_API_KEY)
├── requirements.txt                   # Project dependencies
└── README.md                          # This file


## Troubleshooting

Here are some common issues and their solutions:

1.  **`json.JSONDecodeError: Unterminated string` or `Pydantic serializer warnings`**:
    *   **Issue**: This typically means the LLM API response was cut off.
    *   **Solution**: Check your [OpenRouter.ai account](https://openrouter.ai/account) for sufficient credits or any usage limits. Ensure your `max_tokens` setting in [tailor_resume.py] (`generate_enhanced_tailored_content` function) is adequate for the expected response length. This is usually a credit/billing issue with the API provider.

2.  **`! LaTeX Error: File \`resume.cls' not found.` or PDF compilation failures**:
    *   **Issue**: The `pdflatex` compiler cannot find necessary LaTeX class files or there are errors in the generated `.tex` file.
    *   **Solution**:
        *   Verify that `resume.cls` is present in the root directory. The script will copy it to the `tailored_resumes` folder before compilation.
        *   Ensure a full LaTeX distribution (MiKTeX/TeX Live) is correctly installed and `pdflatex` is in your system's PATH.
        *   Inspect the `.log` file generated alongside the `.tex` file in `tailored_resumes/` for detailed LaTeX errors. These often point to syntax issues in the content generated by the LLM (e.g., unescaped special characters, malformed commands).
        *   Confirm that [sanitize_latex.py] is correctly escaping all LaTeX special characters and preserving commands.

3.  **Incorrect Bullet Point Formatting (points concatenated or excessively split)**:
    *   **Issue**: The generated resume's bullet points (especially for experience/projects) are not formatted as individual items as expected.
    *   **Solution**: Review and refine the logic in [format_bullet_points.py]. Ensure its regular expressions accurately identify and split the LLM's output into distinct points, and that each point is prefixed with `\item ` for LaTeX. The latest version of the `format_bullet_points` function provided in our conversation specifically addresses this.

4.  **Summary or Skills Section Formatting Issues (e.g., `\item` in summary, skills not categorized)**:
    *   **Issue**: The summary has `\item` prefixes, or skills are not divided into categories.
    *   **Solution**:
        *   For the summary, ensure `summary` is **NOT** included in the `ITEMIZE_LIST_KEYS` in [itemize_lists_keys.py] and that the `process_api_response` function in [tailor_resume.py] handles it as plain text.
        *   For categorized skills, verify that your LLM prompt instructs the LLM to return skills in a structured dictionary format (e.g., `{"Category": "skill1, skill2"}`). Also, ensure your [base_resume_template.tex] uses Jinja2 loops to iterate over this structured data, and that [tailor_resume.py]'s `process_api_response` correctly parses and passes this structured skill data.

## Contributing

Contributions are welcome! If you have suggestions for improvements, bug fixes, or new features, please feel free to:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'feat: Add new feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Open a Pull Request.

## License

This project is open-source and available under the [MIT License](LICENSE.md). 

AUTHOR: [NIGHTMARE09](https://github.com/NIGHTMARE09)

