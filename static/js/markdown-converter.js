/**
 * Converts LLM report text to markdown format
 * @param {string} reportText - The original report text
 * @returns {string} Markdown formatted text
 */
function convertToMarkdown(reportText) {
  if (!reportText) return '';
  
  // Split the text into lines
  let lines = reportText.split('\n');
  let markdownLines = [];
  
  for (let line of lines) {
    // Convert section headers (lines starting with ** and ending with **)
    if (line.trim().startsWith('**') && line.trim().endsWith('**')) {
      // Remove the asterisks
      let heading = line.trim().replace(/^\*\*|\*\*$/g, '');
      
      // Determine heading level based on content
      if (heading.includes('Diagnostic Report') || heading.includes('Diagnosebericht')) {
        // Main title - h1
        markdownLines.push(`# ${heading}`);
      } else if (heading.includes('Output') || heading.includes('Observations') || 
                heading.includes('Analysis') || heading.includes('Precautions') || 
                heading.includes('Solutions') || heading.includes('Cause') ||
                heading.includes('Modellvorhersage') || heading.includes('Eingangsdaten')) {
        // Major sections - h2
        markdownLines.push(`## ${heading}`);
      } else {
        // Subsections - h3
        markdownLines.push(`### ${heading}`);
      }
    } 
    // Handle lines that start with ##
    else if (line.trim().startsWith('##')) {
      markdownLines.push(line); // Already in markdown format
    }
    // Convert list items (lines starting with *)
    else if (line.trim().startsWith('* ')) {
      markdownLines.push(line); // Already in markdown format
    }
    // Handle bold text
    else if (line.includes('**')) {
      markdownLines.push(line); // Keep the original markdown bold format
    } 
    // Regular text
    else if (line.trim()) {
      markdownLines.push(line);
    }
    // Preserve empty lines
    else {
      markdownLines.push('');
    }
  }
  
  return markdownLines.join('\n');
} 