import re
def sanitize_latex_content(content):
    """Properly sanitize content for LaTeX while preserving LaTeX commands."""
    # Don't escape these LaTeX commands
    latex_commands = [
        r'\item', r'\begin', r'\end', r'\textbf', r'\textit', r'\hfill',
        r'\vspace', r'\itemsep'
    ]
    
    # First, temporarily replace actual LaTeX commands to protect them
    for i, cmd in enumerate(latex_commands):
        content = content.replace(cmd, f"__LATEXCMD{i}__")
    
    # Now escape special characters
    replacements = {
        '%': r'\%',
        '&': r'\&',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',  # This must come last
    }
    
    for char, replacement in replacements.items():
        # Don't replace backslashes in our temporary command placeholders
        if char != '\\':
            content = content.replace(char, replacement)
        else:
            # Only replace isolated backslashes that aren't part of our protected commands
            content = re.sub(r'(?<!__LATEXCMD)\\', replacement, content)
    
    # Replace newlines with actual LaTeX newlines
    content = content.replace('\\n', r' \\ ')
    
    # Restore LaTeX commands
    for i, cmd in enumerate(latex_commands):
        content = content.replace(f"__LATEXCMD{i}__", cmd)
    
    return content
