from docx import Document
from datetime import datetime
from typing import List, Tuple, Dict, Optional
import os

class DocumentHandler:
    def __init__(self, file_path: str):
        """Initialize the DocumentHandler with a Word document.
        
        Args:
            file_path (str): Path to the Word document
        """
        self.file_path = file_path
        self.document = Document(file_path)
        
    def get_paragraph_text_and_header(self, paragraph_index: int) -> Tuple[str, Optional[int]]:
        """Get the text and header level of a specific paragraph.
        
        Args:
            paragraph_index (int): Index of the paragraph
            
        Returns:
            Tuple[str, Optional[int]]: Tuple of (text, header_level). 
                                     Header level is None if paragraph is not a header
        """
        if paragraph_index >= len(self.document.paragraphs):
            raise IndexError("Paragraph index out of range")
            
        paragraph = self.document.paragraphs[paragraph_index]
        
        # Check if paragraph is a header by checking its style
        header_level = None
        if paragraph.style.name.startswith('Heading'):
            header_level = int(paragraph.style.name[-1])
            
        return paragraph.text, header_level
    
    def get_document_structure(self) -> Dict[str, List[Dict]]:
        """Analyze document structure and return hierarchy of headers.
        
        Returns:
            Dict[str, List[Dict]]: Dictionary containing document structure
        """
        structure = {
            'headers': [],
            'total_paragraphs': len(self.document.paragraphs)
        }
        
        for i, paragraph in enumerate(self.document.paragraphs):
            if paragraph.style.name.startswith('Heading'):
                level = int(paragraph.style.name[-1])
                structure['headers'].append({
                    'level': level,
                    'text': paragraph.text,
                    'index': i
                })
                
        return structure
    
    def update_section(self, section_index: int, new_text: str, is_header: bool = False) -> None:
        """Update the text of a specific section.
        
        Args:
            section_index (int): Index of the section to update
            new_text (str): New text for the section
            is_header (bool): Whether the section is a header (preserves header formatting)
        """
        if section_index >= len(self.document.paragraphs):
            raise IndexError("Section index out of range")
            
        paragraph = self.document.paragraphs[section_index]
        
        # If it's a header, preserve the header style
        style_name = paragraph.style.name
        
        # Clear the paragraph and add new text
        paragraph.clear()
        run = paragraph.add_run(new_text)
        
        # Restore style if it's a header
        if is_header:
            paragraph.style = style_name
            
    def save_document(self, output_dir: str = None) -> str:
        """Save the document with date appended to filename.
        
        Args:
            output_dir (str, optional): Directory to save the file. Defaults to same directory.
            
        Returns:
            str: Path of the saved document
        """
        # Get original filename without extension
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        
        # Create new filename with date
        date_str = datetime.now().strftime("%Y%m%d")
        new_filename = f"{base_name}_{date_str}.docx"
        
        # Determine save path
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            save_path = os.path.join(output_dir, new_filename)
        else:
            save_path = os.path.join(os.path.dirname(self.file_path), new_filename)
            
        self.document.save(save_path)
        return save_path
    
    def get_full_text(self) -> str:
        
        """Get all text content from the document.
        
        Returns:
            str: Full text content of the document
        """
        return "\n".join([paragraph.text for paragraph in self.document.paragraphs if paragraph.text])
    
    def get_section_by_header(self, header_text: str) -> Tuple[int, str]:
        """Find a section by its header text and return its index and content.
        
        Args:
            header_text (str): Text of the header to search for
            
        Returns:
            Tuple[int, str]: Tuple of (section_index, section_text)
            
        Raises:
            ValueError: If header is not found
        """
        for i, paragraph in enumerate(self.document.paragraphs):
            if paragraph.style.name.startswith('Heading') and header_text.lower() in paragraph.text.lower():
                # Find the content until the next header or document end
                content = []
                current_idx = i + 1
                while (current_idx < len(self.document.paragraphs) and 
                       not self.document.paragraphs[current_idx].style.name.startswith('Heading')):
                    content.append(self.document.paragraphs[current_idx].text)
                    current_idx += 1
                return i, "\n".join(content)
                
        raise ValueError(f"Header '{header_text}' not found in document")