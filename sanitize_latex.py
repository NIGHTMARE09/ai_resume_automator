# # D:\New_Projects\resume-automator\sanitize_latex.py

# import re

# def sanitize_latex_content(content):
#     """
#     Sanitizes content for LaTeX by escaping special characters,
#     excluding backslash escaping to prevent double-escaping existing LaTeX commands/sequences.
#     """
#     # Define replacements for special characters.
#     # EXCLUDE backslash ('\\') here to prevent double-escaping for '\%'
#     # and to assume other backslashes are part of valid LaTeX commands or already valid sequences.
#     replacements = {
#         '&': '\\&',
#         '%': '\\%',  # This correctly turns raw '%' into '\%' for literal percentage sign in LaTeX
#         '$': '\\$',
#         '#': '\\#',
#         '_': '\\_',
#         '{': '\\{',
#         '}': '\\}',
#         '~': '\\textasciitilde{}',
#         '^': '\\textasciicircum{}',
#         # Removed the line: '\\': '\\textbackslash{}'
#     }

#     result = ""
#     i = 0
#     while i < len(content):
#         char = content[i]

#         # Check if the current character is part of a preserved LaTeX command.
#         # This list should be comprehensive based on your LaTeX template and expected LLM output.
#         # Ensure that actual LaTeX commands are not modified.
#         preserved_commands = [
#             r'\item', r'\section', r'\subsection', r'\\', r'\textbf', r'\textit',
#             r'\hfill', r'\vspace', r'\itemsep', r'\faPhone', r'\faEnvelope',
#             r'\faLinkedin', r'\faCode', r'\faCodeChef', r'\href', r'\normalsize',
#             r'\begin{itemize}', r'\end{itemize}', r'\rSection', r'\bf', r'\emph', r'\sc',
#             r'\url', r'\texttt', r'\textasciitilde{}', r'\textasciicircum{}', r'\textbackslash{}'
#             # Add any other LaTeX commands that might appear literally in LLM output or fixed strings.
#         ]

#         is_command_start = False
#         for cmd in preserved_commands:
#             if content[i:].startswith(cmd):
#                 # Append the command as is and skip its length
#                 result += content[i : i + len(cmd)]
#                 i += len(cmd)
#                 is_command_start = True
#                 break
        
#         if is_command_start:
#             continue # Move to next part of the content

#         # If not a preserved command, apply character-specific escaping.
#         # The condition `(i == 0 or content[i-1] != '\\')` should correctly prevent
#         # other characters from being escaped if they are immediately preceded by a backslash
#         # (e.g., in `\%`), but since `\` is no longer in `replacements`, this is safer.
#         if char in replacements and (i == 0 or content[i-1] != '\\'):
#             result += replacements[char]
#         else:
#             result += char
#         i += 1
#     return result


# D:\New_Projects\resume-automator\sanitize_latex.py

import re

def sanitize_latex_content(content):
    """
    Sanitizes content for LaTeX by escaping special characters,
    while preserving LaTeX commands and their arguments.
    """
    replacements = {
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '_': '\\_',
        # Curly braces, tilde, and caret are handled specially during command parsing
        # and should only be replaced if they are *not* part of a command's argument.
        # Keeping them here as a fallback if not handled by command logic.
        '{': '\\{',
        '}': '\\}',
        '~': '\\textasciitilde{}',
        '^': '\\^{}',
    }

    result = [] # Use a list for efficiency with string appends
    i = 0

    # List of LaTeX commands whose names and immediate arguments (in {} or []) should be preserved
    # Sort by length descending to match longer commands first (e.g., \itemsep before \item)
    preserved_commands = [
        r'\section', r'\subsection', r'\textbf', r'\textit', r'\\',
        r'\hfill', r'\vspace', r'\itemsep', r'\faPhone', r'\faEnvelope',
        r'\faLinkedin', r'\faCode', r'\faCodeChef', r'\href', r'\normalsize',
        r'\begin{itemize}', r'\end{itemize}', r'\rSection', r'\bf', r'\emph', r'\sc',
        r'\url', r'\texttt', r'\textasciitilde{}', r'\textasciicircum{}', r'\textbackslash{}',
        r'\item'
    ]
    preserved_commands.sort(key=len, reverse=True)


    while i < len(content):
        char = content[i]
        
        is_command_token = False
        
        # Check for start of a preserved LaTeX command
        if char == '\\':
            for cmd in preserved_commands:
                if content[i:].startswith(cmd):
                    # Append the command as is
                    result.append(cmd)
                    i += len(cmd)
                    is_command_token = True
                    
                    # Handle arguments for commands that typically have them
                    # This is a simplification; a full LaTeX parser is complex.
                    # This assumes command arguments are immediately in curly braces or square brackets.
                    if i < len(content) and (content[i] == '{' or content[i] == '['):
                        open_bracket_type = content[i]
                        close_bracket_type = '}' if open_bracket_type == '{' else ']'
                        open_count = 1
                        arg_start_index = i
                        i += 1 # Move past opening bracket
                        
                        while i < len(content) and open_count > 0:
                            if content[i] == open_bracket_type:
                                open_count += 1
                            elif content[i] == close_bracket_type:
                                open_count -= 1
                            i += 1
                        # Append the argument (including its braces/brackets)
                        result.append(content[arg_start_index:i])
                    break # Break from inner for-loop (found and processed command)
        
        if is_command_token:
            continue # Move to next part of the content if a command was processed

        # If not a command, apply character-specific escaping
        # Handle unescaped backslashes (not part of recognized commands)
        if char == '\\':
            result.append(r'\textbackslash{}')
            i += 1
        elif char in replacements:
            result.append(replacements[char])
            i += 1
        else:
            result.append(char)
            i += 1
            
    return "".join(result)

