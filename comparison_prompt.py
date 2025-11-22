from typing import List

from llama_index.core import Document


def build_comparison_prompt(cleaned_documents: List[Document]) -> str:
    """
    Builds an improved, detailed prompt for an LLM to compare structured movie screening data.

    This version includes few-shot examples, clearer rules, and resolved ambiguities
    from the original prompt.
    """
    comparison_prompt = f"""
    You are a strict, methodical comparison engine. Your task is to compare two sets of movie screening data, "Gemini" and "DeepSeek".
    Follow ALL rules and formatting instructions exactly. Do NOT add any commentary, explanations, or extra sections.

    [INPUT DATA]
    The data below contains movie information extracted from two sources.
    DATA_EXTRACTED:
    {cleaned_documents}

    --------------------------------------------------
    [EXAMPLES]

    -- EXAMPLE 1: DISCREPANCY REPORT (TRIGGER B) --
    [INPUT]
    cleaned_documents = [
        Document(text="Source: Gemini, Movie: 'O Corvo', Dates: ['2024-09-05 19:00', '2024-09-09 17:00']"),
        Document(text="Source: DeepSeek, Movie: 'O Corvo', Dates: ['2024-09-05 19:00', '2024-09-11 21:00']")
    ]
    # Note: 2024-09-09 is a Monday. The Monday Rule will cause Gemini's date to be ignored.

    [EXPECTED OUTPUT]
    ## Discrepancies

    ** Movie **
    • Title: O Corvo
    • Screening dates
      • Gemini: ['2024-09-05 19:00']
      • DeepSeek: ['2024-09-05 19:00', '2024-09-11 21:00']
    • Counts
      • Gemini: 1
      • DeepSeek: 2
    • Missing
      • From Gemini: ['2024-09-11 21:00']
    • Quantity of dates missing: 1

    -- EXAMPLE 2: EXACT MATCH (TRIGGER A) --
    [INPUT]
    cleaned_documents = [
        Document(text="Source: Gemini, Movie: 'Retratos Fantasmas', Dates: ['2024-10-01 15:00']"),
        Document(text="Source: DeepSeek, Movie: 'Retratos Fantasmas', Dates: ['2024-10-01 15:00']")
    ]

    [EXPECTED OUTPUT]
    ** Movie **
    • Title: Retratos Fantasmas
    • Files match exactly.
    --------------------------------------------------

    [DATA FORMAT EXPECTATIONS]
    - There are two sources: Gemini and DeepSeek.
    - Each source contains a list of movies with associated screening datetimes.
    - Movie titles should be matched case-insensitively and trimmed of extra whitespace.
    - Dates and times may appear in various formats. Normalize ALL datetimes to ISO format `YYYY-MM-DD HH:MM` for comparison and reporting.

    [MONDAY RULE - PRE-PROCESSING STEP]
    You MUST apply this rule BEFORE any comparison or counting:
    - For any given movie, if a screening date from the Gemini source falls on a Monday, that date is considered a 'false positive' and MUST BE IGNORED, UNLESS a corresponding screening date for the same movie also exists in the DeepSeek source.

    [COMPARISON LOGIC]
    After applying the Monday Rule and normalizing titles/datetimes, perform the comparison.

    1. EXACT MATCH ("TRIGGER A"):
       - The number of movies is identical in both sources, AND
       - For every matched movie, the lists of screening datetimes are identical.
       - If TRUE, use the "Trigger A" output schema.

    2. DISCREPANCY REPORT ("TRIGGER B"):
       - If the "TRIGGER A" criteria are not met, you MUST produce a full discrepancy report using the "Trigger B" output schema.

    [OUTPUT SCHEMAS]
    - If Trigger A, output EXACTLY this Markdown for each movie:

      ** Movie **
      • Title: <string>
      • Files match exactly.

    - If Trigger B, output EXACTLY the following Markdown structure. Omit any empty fields (e.g., if nothing is missing from Gemini, omit the "From Gemini" line entirely).

      ## Discrepancies

      ** Movie **
      • Title: <string>
      • Screening dates
        • Gemini: [ '<YYYY-MM-DD HH:MM>', ... ]
        • DeepSeek: [ '<YYYY-MM-DD HH:MM>', ... ]
      • Counts
        • Gemini: <number>
        • DeepSeek: <number>
      • Missing
        • From Gemini: [ '<YYYY-MM-DD HH:MM>', ... ]
        • From DeepSeek: [ '<YYYY-MM-DD HH:MM>', ... ]
      • Quantity of dates missing: <number> (Total count of datetimes that appear in one source's list but not the other)
      • File-level counts (ONLY if the number of movies differs across sources)
        • Number of Movies in Gemini: <number>
        • Number of Movies in DeepSeek: <number>

      [Add a blank line between each movie discrepancy entry]

    [STRICT FORMATTING RULES]
    - Do NOT include any sections, explanations, prefaces, or conclusions other than those specified in the schemas.
    - Do NOT use code blocks (```) in the final output.
    - All datetimes in the output MUST be in ISO format (`YYYY-MM-DD HH:MM`).
    - Movie titles must be shown in their canonical normalized form.

    [CONTROL BLOCK — FOLLOW THIS EXACT SEQUENCE]
    1. For each movie, normalize titles (trim whitespace).
    2. For each movie, normalize all datetimes to `YYYY-MM-DD HH:MM`.
    3. Apply the Monday Rule to the Gemini data.
    4. Compare the processed data from both sources.
    5. Decide if the result is an EXACT MATCH (Trigger A) or a DISCREPANCY REPORT (Trigger B).
    6. Generate the output strictly following the corresponding schema and formatting rules. Do not deviate.
    """
    return comparison_prompt
