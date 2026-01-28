"""
Note formatter service - Fixes and validates Cornell note format.
Ensures proper callout syntax and quote marker structure.
"""
import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class NoteFormatterService:
    """Post-processes AI-generated notes to ensure correct format."""
    
    def format_note(self, markdown: str) -> str:
        """
        Main entry point - fix all formatting issues.
        
        Args:
            markdown: Raw markdown from AI
            
        Returns:
            Properly formatted markdown
        """
        # Step 1: Fix callout syntax (remove extra brackets)
        markdown = self._fix_callout_syntax(markdown)
        
        # Step 2: Fix cornell section structure
        markdown = self._fix_cornell_structure(markdown)
        
        # Step 3: Fix summary section structure
        markdown = self._fix_summary_structure(markdown)
        
        # Step 4: Fix ad-libitum section structure
        markdown = self._fix_adlibitum_structure(markdown)
        
        # Step 5: Ensure proper spacing between sections
        markdown = self._fix_section_spacing(markdown)
        
        # Step 6: Clean up extra whitespace
        markdown = self._cleanup_whitespace(markdown)
        
        return markdown
    
    def _fix_callout_syntax(self, text: str) -> str:
        """
        Fix callout syntax - ensure [!name] not [[!name]] or other variants.
        """
        # Fix [[!cornell]] -> [!cornell]
        text = re.sub(r'\[\[!cornell\]\]', '[!cornell]', text, flags=re.IGNORECASE)
        text = re.sub(r'\[\[!summary\]\]', '[!summary]', text, flags=re.IGNORECASE)
        text = re.sub(r'\[\[!ad-libitum\]\]', '[!ad-libitum]', text, flags=re.IGNORECASE)
        
        # Fix [!Cornell] -> [!cornell] (case normalization)
        text = re.sub(r'\[!cornell\]', '[!cornell]', text, flags=re.IGNORECASE)
        text = re.sub(r'\[!summary\]', '[!summary]', text, flags=re.IGNORECASE)
        text = re.sub(r'\[!ad-libitum\]', '[!ad-libitum]', text, flags=re.IGNORECASE)
        
        # Fix variations like [!adlibitum] -> [!ad-libitum]
        text = re.sub(r'\[!adlibitum\]', '[!ad-libitum]', text, flags=re.IGNORECASE)
        text = re.sub(r'\[!ad_libitum\]', '[!ad-libitum]', text, flags=re.IGNORECASE)
        
        return text
    
    def _fix_cornell_structure(self, text: str) -> str:
        """
        Fix cornell callout structure.
        
        Expected format:
        > [!cornell] Title
        >
        > > ## Questions/Cues
        > > - content
        > >
        > > ## Reference Points
        > > - content
        >
        > > ### Major Concept 1
        > > content
        """
        lines = text.split('\n')
        result = []
        in_cornell = False
        in_questions_refs = False  # True when in Questions/Cues or Reference Points
        after_refs = False  # True after we've passed Reference Points
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Detect start of cornell callout
            if '[!cornell]' in stripped.lower():
                in_cornell = True
                in_questions_refs = False
                after_refs = False
                # Ensure single > at start
                clean_line = re.sub(r'^[>\s]*', '', line)
                if '[!cornell]' in clean_line.lower():
                    result.append('> ' + clean_line)
                else:
                    result.append(line)
                i += 1
                continue
            
            # Detect end of cornell (start of summary or ad-libitum)
            if in_cornell and ('[!summary]' in stripped.lower() or '[!ad-libitum]' in stripped.lower()):
                in_cornell = False
                in_questions_refs = False
                after_refs = False
            
            if in_cornell:
                # Remove existing > markers to normalize
                content = re.sub(r'^[>\s]+', '', line).strip()
                
                # Empty line handling
                if not content:
                    if in_questions_refs and not after_refs:
                        # Empty line within questions/refs section
                        result.append('> >')
                    elif after_refs:
                        # Don't add extra empty lines in concept section
                        pass
                    else:
                        # Separator line (single >)
                        result.append('>')
                    i += 1
                    continue
                
                # Detect Questions/Cues or Reference Points headers
                if re.match(r'^#{1,2}\s*(questions?|cues?|reference\s*points?)', content, re.IGNORECASE):
                    in_questions_refs = True
                    after_refs = False
                    result.append('> > ## ' + re.sub(r'^#+\s*', '', content))
                    i += 1
                    continue
                
                # Detect end of Reference Points (next major heading)
                if in_questions_refs and re.match(r'^#{2,3}\s+(?!questions?|cues?|reference)', content, re.IGNORECASE):
                    # This is a major concept heading - transition
                    in_questions_refs = False
                    after_refs = True
                    # Add separator before concepts
                    result.append('>')
                    result.append('> > ### ' + re.sub(r'^#+\s*', '', content))
                    i += 1
                    continue
                
                # Detect major concept headings (### or ####)
                if re.match(r'^#{2,4}\s+', content):
                    heading_content = re.sub(r'^#+\s*', '', content)
                    result.append('> > ### ' + heading_content)
                    i += 1
                    continue
                
                # Regular content
                if in_questions_refs or after_refs:
                    # Double > for content in questions/refs and concepts
                    result.append('> > ' + content)
                else:
                    # Single > for other cornell content
                    result.append('> ' + content)
            else:
                result.append(line)
            
            i += 1
        
        return '\n'.join(result)
    
    def _fix_summary_structure(self, text: str) -> str:
        """
        Fix summary callout structure - always single > prefix.
        
        Expected format:
        > [!summary]
        > 
        > Content here with single >
        """
        lines = text.split('\n')
        result = []
        in_summary = False
        
        for line in lines:
            stripped = line.strip()
            
            # Detect start of summary
            if '[!summary]' in stripped.lower():
                in_summary = True
                # Ensure proper format
                content = re.sub(r'^[>\s]*', '', line)
                result.append('> ' + content)
                continue
            
            # Detect end of summary (start of another section)
            if in_summary and ('[!cornell]' in stripped.lower() or '[!ad-libitum]' in stripped.lower()):
                in_summary = False
            
            if in_summary:
                # Normalize to single >
                content = re.sub(r'^[>\s]+', '', line)
                if content:
                    result.append('> ' + content)
                else:
                    result.append('>')
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def _fix_adlibitum_structure(self, text: str) -> str:
        """
        Fix ad-libitum callout structure - always single > prefix.
        
        Expected format:
        > [!ad-libitum]- Additional Information
        > 
        > Content here with single >
        """
        lines = text.split('\n')
        result = []
        in_adlibitum = False
        
        for line in lines:
            stripped = line.strip()
            
            # Detect start of ad-libitum
            if '[!ad-libitum]' in stripped.lower():
                in_adlibitum = True
                # Ensure proper format
                content = re.sub(r'^[>\s]*', '', line)
                result.append('> ' + content)
                continue
            
            # Detect end (start of another section or end of file)
            if in_adlibitum and ('[!cornell]' in stripped.lower() or '[!summary]' in stripped.lower()):
                in_adlibitum = False
            
            if in_adlibitum:
                # Normalize to single >
                content = re.sub(r'^[>\s]+', '', line)
                if content:
                    result.append('> ' + content)
                else:
                    result.append('>')
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def _fix_section_spacing(self, text: str) -> str:
        """
        Ensure blank line between [!cornell], [!summary], and [!ad-libitum] sections.
        """
        # Add blank line before [!summary] if not present
        text = re.sub(r'(\n>[^\n]*\n)(> \[!summary\])', r'\1\n\2', text)
        
        # Add blank line before [!ad-libitum] if not present  
        text = re.sub(r'(\n>[^\n]*\n)(> \[!ad-libitum\])', r'\1\n\2', text)
        
        # Add blank line before [!cornell] if not present (for multiple cornell sections)
        text = re.sub(r'(\n>[^\n]*\n)(> \[!cornell\])', r'\1\n\2', text)
        
        return text
    
    def _cleanup_whitespace(self, text: str) -> str:
        """
        Clean up excessive whitespace while preserving structure.
        """
        # Remove trailing whitespace from lines
        lines = [line.rstrip() for line in text.split('\n')]
        
        # Remove excessive blank lines (more than 2 consecutive)
        result = []
        blank_count = 0
        for line in lines:
            if not line or line == '>':
                blank_count += 1
                if blank_count <= 2:
                    result.append(line)
            else:
                blank_count = 0
                result.append(line)
        
        return '\n'.join(result)
    
    def validate_format(self, markdown: str) -> Tuple[bool, list]:
        """
        Validate the note format and return issues found.
        
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        # Check for wrong callout syntax
        if re.search(r'\[\[!cornell\]\]', markdown, re.IGNORECASE):
            issues.append("Found [[!cornell]] instead of [!cornell]")
        if re.search(r'\[\[!summary\]\]', markdown, re.IGNORECASE):
            issues.append("Found [[!summary]] instead of [!summary]")
        if re.search(r'\[\[!ad-libitum\]\]', markdown, re.IGNORECASE):
            issues.append("Found [[!ad-libitum]] instead of [!ad-libitum]")
        
        # Check for missing sections
        if not re.search(r'\[!cornell\]', markdown, re.IGNORECASE):
            issues.append("Missing [!cornell] section")
        if not re.search(r'\[!summary\]', markdown, re.IGNORECASE):
            issues.append("Missing [!summary] section")
        if not re.search(r'\[!ad-libitum\]', markdown, re.IGNORECASE):
            issues.append("Missing [!ad-libitum] section")
        
        return len(issues) == 0, issues


# Singleton instance
note_formatter_service = NoteFormatterService()