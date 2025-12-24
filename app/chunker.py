# app/chunker.py
from langchain.text_splitter import MarkdownHeaderTextSplitter

def chunk_markdown(text):
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(text)
    
    # Return the text content of each split
    return [split.page_content for split in md_header_splits]