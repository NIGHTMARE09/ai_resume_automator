import re
from sanitize_latex import sanitize_latex_content
# def format_bullet_points(content):
#     """Convert array-like strings to LaTeX bullet points."""
#     # Check if content looks like an array
#     if content.startswith('[') and content.endswith(']'):
#         try:
#             # Remove brackets and split by commas that are followed by a quote
#             items = content[1:-1].split("', '")
            
#             # Clean up the items
#             items = [item.strip().strip("'").strip('"') for item in items]
            
#             # Convert to LaTeX bullet points
#             return "\\begin{itemize}\n" + "\n".join([f"    \\item {sanitize_latex_content(item)}" for item in items]) + "\n\\end{itemize}"
#         except:
#             # If parsing fails, return the original content
#             return content
    
#     return content

def format_bullet_points(content):
    """Format bullet points properly for LaTeX."""
    # Remove any existing \begin{itemize} and \end{itemize} tags
    content = re.sub(r'\\begin\{itemize\}|\\end\{itemize\}', '', content)
    
    # Split by lines and process
    lines = content.strip().split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            # If line doesn't already start with \item, add it
            if not line.startswith(r'\item'):
                line = r'\item ' + line
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)
