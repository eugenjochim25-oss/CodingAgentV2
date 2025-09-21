"""
AI Agent Learning Service
Enables the agent to learn from code executions, languages, and interactions
"""

import json
import hashlib
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import re


class LearningService:
    """Service for AI agent to learn from user interactions and code patterns"""
    
    def __init__(self, db_path: str = "learning_data.db"):
        self.db_path = db_path
        self.code_patterns = {}
        self.language_stats = defaultdict(lambda: {
            'usage_count': 0,
            'success_rate': 0.0,
            'avg_execution_time': 0.0,
            'common_errors': Counter(),
            'successful_patterns': []
        })
        self.user_preferences = {}
        self._init_database()
        self._load_existing_data()
    
    def _init_database(self):
        """Initialize SQLite database for learning data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_hash TEXT,
                language TEXT,
                success BOOLEAN,
                execution_time REAL,
                error_type TEXT,
                code_snippet TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_question TEXT,
                ai_response TEXT,
                helpful_rating INTEGER,
                question_category TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS language_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                language TEXT,
                usage_frequency INTEGER,
                success_patterns TEXT,
                common_libraries TEXT,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_existing_data(self):
        """Load existing learning data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load language statistics
        cursor.execute('SELECT language, COUNT(*) as count, AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate, AVG(execution_time) as avg_time FROM code_executions GROUP BY language')
        
        for row in cursor.fetchall():
            language, count, success_rate, avg_time = row
            self.language_stats[language].update({
                'usage_count': count,
                'success_rate': success_rate or 0.0,
                'avg_execution_time': avg_time or 0.0
            })
        
        conn.close()
    
    def analyze_code_execution(self, code: str, language: str, success: bool, 
                             execution_time: float = 0.0, error_message: str = ""):
        """Learn from code execution patterns"""
        code_hash = hashlib.md5(code.encode()).hexdigest()[:16]
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        error_type = self._categorize_error(error_message) if not success else None
        
        cursor.execute('''
            INSERT INTO code_executions (code_hash, language, success, execution_time, error_type, code_snippet)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (code_hash, language, success, execution_time, error_type, code[:500]))
        
        conn.commit()
        conn.close()
        
        # Update in-memory statistics
        stats = self.language_stats[language]
        stats['usage_count'] += 1
        
        # Update success rate (running average)
        old_success_rate = stats['success_rate']
        new_count = stats['usage_count']
        stats['success_rate'] = (old_success_rate * (new_count - 1) + (1.0 if success else 0.0)) / new_count
        
        # Update execution time (running average)
        old_avg_time = stats['avg_execution_time']
        stats['avg_execution_time'] = (old_avg_time * (new_count - 1) + execution_time) / new_count
        
        # Track common errors
        if not success and error_message:
            stats['common_errors'][error_type] += 1
        
        # Extract and store successful patterns
        if success:
            patterns = self._extract_code_patterns(code, language)
            stats['successful_patterns'].extend(patterns)
            # Keep only top 20 patterns
            stats['successful_patterns'] = stats['successful_patterns'][-20:]
    
    def learn_from_chat(self, user_question: str, ai_response: str, helpful_rating: int = 3):
        """Learn from chat interactions"""
        question_category = self._categorize_question(user_question)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_interactions (user_question, ai_response, helpful_rating, question_category)
            VALUES (?, ?, ?, ?)
        ''', (user_question, ai_response, helpful_rating, question_category))
        
        conn.commit()
        conn.close()
    
    def get_code_suggestions(self, partial_code: str, language: str) -> List[str]:
        """Provide code suggestions based on learned patterns"""
        suggestions = []
        
        # Get successful patterns for this language
        if language in self.language_stats:
            patterns = self.language_stats[language]['successful_patterns']
            
            # Find relevant patterns
            for pattern in patterns:
                if self._pattern_matches_context(pattern, partial_code):
                    suggestions.append(pattern)
            
        # Limit to top 3 suggestions
        return suggestions[:3]
    
    def get_language_recommendations(self) -> List[Dict[str, Any]]:
        """Recommend languages based on usage patterns"""
        recommendations = []
        
        for language, stats in self.language_stats.items():
            if stats['usage_count'] > 0:
                score = (stats['success_rate'] * 0.7 + 
                        min(stats['usage_count'] / 10.0, 1.0) * 0.3)
                
                recommendations.append({
                    'language': language,
                    'score': score,
                    'success_rate': stats['success_rate'],
                    'usage_count': stats['usage_count']
                })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)
    
    def get_common_errors(self, language: str) -> List[Dict[str, Any]]:
        """Get common errors for a language to help prevent them"""
        if language not in self.language_stats:
            return []
        
        errors = self.language_stats[language]['common_errors']
        return [{'error_type': error, 'count': count} 
                for error, count in errors.most_common(5)]
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get overall learning statistics"""
        total_executions = sum(stats['usage_count'] for stats in self.language_stats.values())
        
        if total_executions == 0:
            return {
                'total_executions': 0,
                'languages_used': 0,
                'overall_success_rate': 0.0,
                'most_used_language': 'Noch keine Daten'
            }
        
        # Calculate overall success rate
        weighted_success = sum(stats['success_rate'] * stats['usage_count'] 
                             for stats in self.language_stats.values())
        overall_success_rate = weighted_success / total_executions
        
        # Find most used language
        most_used = max(self.language_stats.items(), 
                       key=lambda x: x[1]['usage_count'])
        
        return {
            'total_executions': total_executions,
            'languages_used': len(self.language_stats),
            'overall_success_rate': round(overall_success_rate, 3),
            'most_used_language': most_used[0],
            'language_stats': dict(self.language_stats)
        }
    
    def _categorize_error(self, error_message: str) -> str:
        """Categorize error messages"""
        if not error_message:
            return "unknown"
        
        error_message = error_message.lower()
        
        if "syntax" in error_message:
            return "syntax_error"
        elif "name" in error_message and "not defined" in error_message:
            return "name_error"
        elif "import" in error_message or "module" in error_message:
            return "import_error"
        elif "type" in error_message:
            return "type_error"
        elif "index" in error_message:
            return "index_error"
        elif "key" in error_message:
            return "key_error"
        else:
            return "runtime_error"
    
    def _categorize_question(self, question: str) -> str:
        """Categorize user questions"""
        question = question.lower()
        
        if any(word in question for word in ['how', 'wie', 'tutorial']):
            return "how_to"
        elif any(word in question for word in ['error', 'fehler', 'bug', 'problem']):
            return "debugging"
        elif any(word in question for word in ['what', 'was', 'explain', 'erklär']):
            return "explanation"
        elif any(word in question for word in ['best', 'better', 'optimize', 'improve']):
            return "optimization"
        else:
            return "general"
    
    def _extract_code_patterns(self, code: str, language: str) -> List[str]:
        """Extract useful patterns from successful code"""
        patterns = []
        
        # Language-specific pattern extraction
        if language == 'python':
            # Extract function definitions
            func_patterns = re.findall(r'def\s+\w+\([^)]*\):', code)
            patterns.extend(func_patterns)
            
            # Extract import statements
            import_patterns = re.findall(r'(?:from\s+\w+\s+)?import\s+[\w,\s]+', code)
            patterns.extend(import_patterns)
            
            # Extract class definitions
            class_patterns = re.findall(r'class\s+\w+(?:\([^)]*\))?:', code)
            patterns.extend(class_patterns)
        
        elif language == 'javascript':
            # Extract function declarations
            func_patterns = re.findall(r'function\s+\w+\([^)]*\)', code)
            patterns.extend(func_patterns)
            
            # Extract arrow functions
            arrow_patterns = re.findall(r'const\s+\w+\s*=\s*\([^)]*\)\s*=>', code)
            patterns.extend(arrow_patterns)
        
        return patterns[:5]  # Limit to 5 patterns per code snippet
    
    def _pattern_matches_context(self, pattern: str, context: str) -> bool:
        """Check if a pattern is relevant to current context"""
        # Simple relevance check - can be made more sophisticated
        pattern_words = set(re.findall(r'\w+', pattern.lower()))
        context_words = set(re.findall(r'\w+', context.lower()))
        
        # If there's significant word overlap, consider it relevant
        overlap = len(pattern_words & context_words)
        return overlap > 0
    
    def save_learning_data(self):
        """Save current learning state (in case of graceful shutdown)"""
        # Data is already persisted in SQLite, but we could add backup functionality here
        pass


# Global learning service instance
learning_service = LearningService()