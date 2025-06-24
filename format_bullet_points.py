# D:\New_Projects\resume-automator\format_bullet_points.py

import re

def format_bullet_points(content):
    """
    Formats a block of text into LaTeX bullet points.
    Splits content based on common list item markers and sentence endings,
    ensuring accurate itemization for LLM output.
    """
    if not content:
        return ""

    content = content.strip()
    temp_separator = "@@BULLET_POINT_SEPARATOR@@" # A unique string unlikely to be in content

    # Define a comprehensive pattern to identify the start of new bullet points.
    # We will replace these patterns with our unique temporary separator.
    # Order matters: more specific/longer patterns first.

    # 1. Explicit LaTeX \item or common variations (e.g., /item, \item•, \item-)
    # Replace the full delimiter, consume it.
    content = re.sub(r'(?:\\|/)item\s*[\u2022\*\-]?\s*', temp_separator + ' ', content, flags=re.IGNORECASE)

    # 2. Bullet characters that are clearly new item markers:
    #    a. Immediately preceded by sentence-ending punctuation (., ?, !) and optional whitespace.
    content = re.sub(r'(?<=[.?!])\s*[\u2022\*\-]\s*', temp_separator + ' ', content)
    #    b. Immediately preceded by a newline and optional whitespace.
    content = re.sub(r'(?:\r?\n|\r)\s*[\u2022\*\-]\s*', temp_separator + ' ', content)
    #    c. Standalone bullet character followed by a space at the start of a logical segment (less common from LLM)
    #       This is handled by the splitting and subsequent stripping of leading chars.

    # 3. Sentence-ending punctuation (., ?, !) followed by whitespace and a capital letter.
    # This identifies natural sentence breaks that should become new bullet points.
    # It replaces the whitespace *between* the punctuation and the capital letter,
    # ensuring the punctuation stays with the preceding sentence.
    content = re.sub(r'(?<=[.?!])\s+(?=[A-Z])', temp_separator + ' ', content)

    # Edge case: If the content doesn't start with a separator, prepend one.
    # This ensures the first logical item is always captured.
    if not content.startswith(temp_separator):
        content = temp_separator + content

    # Now, split the content by the unique temporary separator.
    items_raw = content.split(temp_separator)
    
    formatted_lines = []

    for item in items_raw:
        item = item.strip()
        if not item: # Skip empty strings that result from multiple consecutive separators
            continue

        # Remove any residual bullet characters or excessive whitespace that might remain
        # at the very start of an item (e.g., if the LLM output had `•Point`).
        item = re.sub(r'^[\s\u2022\*\-]+', '', item).strip()

        if item: # Only add to the list if content remains after cleaning
            # Prefix with the LaTeX \item command
            formatted_lines.append(r'\item ' + item)

    # Join all formatted items with newlines. The LaTeX template's itemize environment
    # will handle the overall list structure.
    return '\n'.join(formatted_lines)


# Keep your test_formatter and __main__ block for testing this function in isolation
def test_formatter():
    sample_content = r"\item • Optimized data processing pipelines for image annotation projects, reducing annotation time by 25% through parallel processing and improved workflow orchestration using Apache Airflow. Led the implementation of a fault-tolerant microservices architecture for real-time video analysis, ensuring 99.99% uptime during peak loads of 5000+ concurrent users. Architected a distributed caching layer with Redis to handle session management for millions of requests, reducing database load by 70% and improving response times from 200ms to under 50ms."
    sample_content2 = r"\item Designed and implemented a microservices-based architecture for video annotation tasks, improving processing speed by 40\% through parallel processing and load balancing.• Developed Python-based data processing pipelines using Pandas and NumPy to handle large-scale datasets (up to 1TB), reducing annotation errors by 30\%.• Integrated Docker containers with AWS ECS to deploy and scale annotation models efficiently across multiple Availability Zones.\item Optimized database queries using PostgreSQL and Redis caching, improving data retrieval times by 60\%.• Collaborated with data scientists to design scalable data ingestion frameworks, ensuring fault tolerance and high availability for real-time annotation feedback."
    sample_content3 = r'• Optimized large-scale data processing (800TB-1.5PB) using Python, Ray, React, TypeScript, and Java, enhancing service scalability and computational efficiency.\n• Streamlined data quality workflows with Ray, resulting in 13% monthly cost savings and improved data accessibility via Amazon DynamoDB.\n• Created a React-based dashboard for visualizing Marketplace data quality metrics, enabling data-driven decision-making and improving operational insights.'    
    # Example for testing with a full-stop followed by content (no bullet char initially)
    sample_content_dot_split = "First point content. Second point content should start here. Third point here."
    # To make the test case reflect your specific "Zones.\item Optimized" problem more clearly,
    # let's include the problematic `/\item` too.
    sample_content_with_slash_item = r"Point one content. /item Point two content."
    
    print("\n" + "="*50)
    print("TEST: Sample Content 1 (Multi-point block)")
    print("Original content:")
    print(sample_content)
    print("\nFormatted content:")
    print(format_bullet_points(sample_content))

    print("\n" + "="*50)
    print("TEST: Sample Content 2 (Your complex test case)")
    print("Original content:")
    print(sample_content3)
    print("\nFormatted content:")
    print(format_bullet_points(sample_content3))

    print("\n" + "="*50)
    print("TEST: Full-stop without explicit bullet char")
    print("Original content:")
    print(sample_content_dot_split)
    print("\nFormatted content:")
    print(format_bullet_points(sample_content_dot_split)) # This should now result in multiple items

    print("\n" + "="*50)
    print("TEST: Handling /item from LLM")
    print("Original content:")
    print(sample_content_with_slash_item)
    print("\nFormatted content:")
    print(format_bullet_points(sample_content_with_slash_item))


if __name__ == "__main__":
    test_formatter()
