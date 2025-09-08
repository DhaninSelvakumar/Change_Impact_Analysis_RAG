from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class LlamaAnalyzer:
    def __init__(self, model_name="microsoft/DialoGPT-medium"):
        """Initialize with a lighter model for demo purposes"""
        try:
            # Use a lighter model for demo - replace with LLaMA when available
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {self.device}")
            
            # For demo purposes, using a text generation model
            # Replace with actual LLaMA model: "meta-llama/Llama-2-7b-chat-hf"
            self.generator = pipeline(
                "text-generation",
                model="mistralai/Mistral-7B-Instruct-v0.1",
                device=0 if self.device == "cuda" else -1
            )

            
            logger.info("LLaMA Analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing LLaMA model: {str(e)}")
            # Fallback to simple text analysis
            self.generator = None
    
    def analyze_impact(self, differences: List[Dict], related_contexts: List[Dict]) -> str:
        """Analyze the impact of document changes"""
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(differences, related_contexts)
            
            if self.generator:
                # Use AI model for analysis
                response = self.generator(
                    prompt,
                    max_length=400,
                    min_length=100,
                    do_sample=False
                )
                return response[0]['summary_text'].strip()
            else:
                # Fallback to rule-based analysis
                return self._rule_based_analysis(differences, related_contexts)
                
        except Exception as e:
            logger.error(f"Error in impact analysis: {str(e)}")
            return self._rule_based_analysis(differences, related_contexts)
    
    def _create_analysis_prompt(self, differences: List[Dict], related_contexts: List[Dict]) -> str:
        """Create structured prompt for LLaMA"""
        prompt = "Document Change Impact Analysis:\n\n"
        
        prompt += "CHANGES DETECTED:\n"
        for i, diff in enumerate(differences, 1):
            prompt += f"{i}. {diff['description']} (Type: {diff['type']})\n"
        
        prompt += "\nRELATED DOCUMENTS:\n"
        for i, context in enumerate(related_contexts[:3], 1):  # Limit to top 3
            prompt += f"{i}. {context['file_name']}: {context['content'][:100]}...\n"
        
        prompt += "\nANALYSIS:\nProvide impact assessment and recommendations:"
        
        return prompt
    
    def _rule_based_analysis(self, differences: List[Dict], related_contexts: List[Dict]) -> str:
        """Fallback rule-based analysis"""
        analysis = "## Impact Analysis Report\n\n"
        
        # Categorize changes
        modified_files = [d for d in differences if d['type'] == 'modified']
        deleted_files = [d for d in differences if d['type'] == 'deleted']
        added_files = [d for d in differences if d['type'] == 'added']
        
        # Summary
        analysis += f"**Summary**: {len(differences)} changes detected across documentation.\n\n"
        
        # Impact assessment
        analysis += "**Impact Assessment**:\n"
        
        if deleted_files:
            analysis += f"- HIGH IMPACT: {len(deleted_files)} files deleted - may break references\n"
        
        if modified_files:
            analysis += f"- MEDIUM IMPACT: {len(modified_files)} files modified - content changes detected\n"
        
        if added_files:
            analysis += f"- LOW IMPACT: {len(added_files)} new files added - may need integration\n"
        
        # Related documents
        analysis += f"\n**Related Documents**: Found {len(related_contexts)} potentially impacted documents\n"
        
        # Recommendations
        analysis += "\n**Recommendations**:\n"
        analysis += "1. Review all related documents for consistency\n"
        analysis += "2. Update cross-references if files were deleted or renamed\n"
        analysis += "3. Ensure new content aligns with existing documentation standards\n"
        
        return analysis