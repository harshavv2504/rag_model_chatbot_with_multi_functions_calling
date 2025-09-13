#!/usr/bin/env python3
"""
Enhanced Coffee Knowledge Base Handler
Optimized for accuracy with semantic search, relevance scoring, and improved matching
"""

import os
import re
import json
import yaml
import markdown
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from collections import Counter
import math

class EnhancedCoffeeKnowledgeBase:
    def __init__(self, mdx_directory: str = "knowledge"):
        self.mdx_directory = Path(mdx_directory)
        self.mdx_directory.mkdir(parents=True, exist_ok=True)
        self._cache = {}  # Cache for parsed entries
        self._last_cache_update = None
    
    def _get_mdx_files(self) -> List[Path]:
        """Get all MDX files in the knowledge base directory"""
        return list(self.mdx_directory.glob("*.mdx"))
    
    def _parse_mdx_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse an MDX file and extract frontmatter and content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter manually
            frontmatter_data, markdown_content = self._parse_frontmatter(content)
            
            # Extract metadata from frontmatter
            metadata = {
                'id': file_path.stem,
                'title': frontmatter_data.get('title', file_path.stem),
                'topic': frontmatter_data.get('topic', ''),
                'tags': frontmatter_data.get('tags', []),
                'created': frontmatter_data.get('created', ''),
                'updated': frontmatter_data.get('updated', ''),
                'filename': file_path.name,
                'filepath': str(file_path)
            }
            
            # Get content (both raw and HTML)
            content_raw = markdown_content
            content_html = markdown.markdown(content_raw)
            
            # Extract keywords for better matching
            keywords = self._extract_keywords(content_raw, metadata)
            
            return {
                **metadata,
                'content_raw': content_raw,
                'content_html': content_html,
                'keywords': keywords
            }
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def _extract_keywords(self, content: str, metadata: Dict) -> List[str]:
        """Extract relevant keywords from content for better matching"""
        # Combine title, topic, tags, and content
        text = f"{metadata.get('title', '')} {metadata.get('topic', '')} {' '.join(metadata.get('tags', []))} {content}"
        
        # Convert to lowercase and split into words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        # Filter and count words
        filtered_words = [word for word in words if len(word) > 2 and word not in stop_words]
        word_counts = Counter(filtered_words)
        
        # Return top keywords (most frequent and relevant)
        return [word for word, count in word_counts.most_common(20)]
    
    def _parse_frontmatter(self, content: str) -> tuple:
        """Parse frontmatter from content manually"""
        if not content.startswith('---'):
            return {}, content
        
        lines = content.split('\n')
        if len(lines) < 2:
            return {}, content
        
        end_index = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_index = i
                break
        
        if end_index == -1:
            return {}, content
        
        frontmatter_text = '\n'.join(lines[1:end_index])
        markdown_content = '\n'.join(lines[end_index + 1:])
        
        try:
            frontmatter_data = yaml.safe_load(frontmatter_text) or {}
        except yaml.YAMLError:
            frontmatter_data = {}
        
        return frontmatter_data, markdown_content
    
    def _get_entries_cached(self) -> List[Dict[str, Any]]:
        """Get entries with caching for better performance"""
        current_time = datetime.now()
        
        # Check if cache is still valid (5 minutes)
        if (self._last_cache_update and 
            (current_time - self._last_cache_update).seconds < 300 and 
            self._cache):
            return list(self._cache.values())
        
        # Refresh cache
        mdx_files = self._get_mdx_files()
        self._cache = {}
        
        for file_path in mdx_files:
            entry = self._parse_mdx_file(file_path)
            if entry:
                self._cache[entry['id']] = entry
        
        self._last_cache_update = current_time
        return list(self._cache.values())
    
    def _calculate_relevance_score(self, query: str, entry: Dict[str, Any]) -> float:
        """Calculate relevance score for an entry based on query"""
        query_lower = query.lower()
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        
        score = 0.0
        
        # Title match (highest weight)
        title_words = set(re.findall(r'\b\w+\b', entry.get('title', '').lower()))
        title_matches = len(query_words.intersection(title_words))
        score += title_matches * 10.0
        
        # Topic match (high weight)
        topic_words = set(re.findall(r'\b\w+\b', entry.get('topic', '').lower()))
        topic_matches = len(query_words.intersection(topic_words))
        score += topic_matches * 8.0
        
        # Tags match (medium-high weight)
        tag_matches = 0
        for tag in entry.get('tags', []):
            tag_words = set(re.findall(r'\b\w+\b', tag.lower()))
            tag_matches += len(query_words.intersection(tag_words))
        score += tag_matches * 6.0
        
        # Content match (medium weight)
        content_words = set(re.findall(r'\b\w+\b', entry.get('content_raw', '').lower()))
        content_matches = len(query_words.intersection(content_words))
        score += content_matches * 2.0
        
        # Keywords match (medium weight)
        keyword_matches = 0
        for keyword in entry.get('keywords', []):
            if any(word in keyword.lower() for word in query_words):
                keyword_matches += 1
        score += keyword_matches * 4.0
        
        # Exact phrase match bonus
        if query_lower in entry.get('content_raw', '').lower():
            score += 15.0
        
        # Partial phrase match bonus
        query_phrases = query_lower.split()
        for i in range(len(query_phrases) - 1):
            phrase = ' '.join(query_phrases[i:i+2])
            if phrase in entry.get('content_raw', '').lower():
                score += 8.0
        
        return score
    
    def _semantic_search(self, query: str, entries: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], float]]:
        """Perform semantic search with relevance scoring"""
        query_lower = query.lower()
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        
        # Define semantic relationships for coffee industry
        semantic_groups = {
            'coffee_quality': ['quality', 'excellent', 'premium', 'specialty', 'artisan', 'gourmet', 'taste', 'flavor', 'aroma'],
            'business_operations': ['operations', 'efficiency', 'workflow', 'process', 'management', 'optimization', 'productivity'],
            'sales_revenue': ['sales', 'revenue', 'profit', 'pricing', 'upselling', 'margin', 'earnings', 'growth', 'increase'],
            'customer_service': ['customer', 'service', 'experience', 'satisfaction', 'loyalty', 'retention', 'support'],
            'equipment_technical': ['equipment', 'machine', 'espresso', 'grinder', 'brewer', 'maintenance', 'calibration', 'technical'],
            'menu_design': ['menu', 'design', 'layout', 'psychology', 'pricing', 'presentation', 'visual'],
            'training_education': ['training', 'education', 'learning', 'teaching', 'barista', 'staff', 'skills'],
            'branding_marketing': ['brand', 'branding', 'marketing', 'white label', 'private label', 'identity', 'promotion'],
            'roasting_processing': ['roasting', 'roast', 'processing', 'beans', 'origins', 'farm', 'green beans'],
            'storage_freshness': ['storage', 'freshness', 'shelf life', 'preservation', 'timing', 'temperature']
        }
        
        # Find relevant semantic groups
        relevant_groups = []
        for group_name, keywords in semantic_groups.items():
            if any(keyword in query_words for keyword in keywords):
                relevant_groups.append(group_name)
        
        # Calculate enhanced relevance scores
        scored_entries = []
        for entry in entries:
            base_score = self._calculate_relevance_score(query, entry)
            
            # Semantic group bonus
            semantic_bonus = 0
            entry_text = f"{entry.get('title', '')} {entry.get('topic', '')} {' '.join(entry.get('tags', []))} {entry.get('content_raw', '')}".lower()
            
            for group_name, keywords in semantic_groups.items():
                if group_name in relevant_groups:
                    group_matches = sum(1 for keyword in keywords if keyword in entry_text)
                    semantic_bonus += group_matches * 2.0
            
            final_score = base_score + semantic_bonus
            scored_entries.append((entry, final_score))
        
        # Sort by relevance score (descending)
        scored_entries.sort(key=lambda x: x[1], reverse=True)
        
        return scored_entries
    
    def search_knowledge_base(self, query: str, max_results: int = 10, min_score: float = 1.0) -> List[Dict[str, Any]]:
        """Enhanced search with accuracy optimization"""
        try:
            entries = self._get_entries_cached()
            if not entries:
                return []
            
            query_lower = query.lower().strip()
            if not query_lower:
                return []
            
            # First, check for exact priority matches
            priority_mappings = self._get_priority_mappings()
            priority_files = []
            
            for key, files in priority_mappings.items():
                if key in query_lower:
                    priority_files.extend(files)
            
            # Remove duplicates and keep order
            priority_files = list(dict.fromkeys(priority_files))
            
            # If we have priority files, return them first with high scores
            if priority_files:
                priority_entries = []
                for entry in entries:
                    if entry.get('filename') in priority_files:
                        # Calculate position in priority list for scoring
                        try:
                            priority_score = 100 - priority_files.index(entry.get('filename'))
                        except ValueError:
                            priority_score = 50
                        priority_entries.append((entry, priority_score))
                
                # Sort by priority order
                priority_entries.sort(key=lambda x: x[1], reverse=True)
                
                # Add remaining entries using semantic search
                remaining_entries = [entry for entry in entries if entry.get('filename') not in priority_files]
                if remaining_entries:
                    semantic_results = self._semantic_search(query, remaining_entries)
                    # Filter out low-scoring results
                    semantic_results = [(entry, score) for entry, score in semantic_results if score >= min_score]
                    priority_entries.extend(semantic_results[:max_results - len(priority_entries)])
                
                return [entry for entry, score in priority_entries[:max_results]]
            
            # No priority matches, use semantic search
            semantic_results = self._semantic_search(query, entries)
            
            # Filter by minimum score and limit results
            filtered_results = [(entry, score) for entry, score in semantic_results if score >= min_score]
            
            return [entry for entry, score in filtered_results[:max_results]]
            
        except Exception as e:
            print(f"Error searching knowledge base: {e}")
            return []
    
    def _get_priority_mappings(self) -> Dict[str, List[str]]:
        """Get priority mappings for specific queries"""
        return {
            # Company & Introduction
            'company': ['01-company-introduction.mdx'],
            'introduction': ['01-company-introduction.mdx'],
            'about': ['01-company-introduction.mdx', '11-about-founders-company.mdx'],
            'founders': ['01-company-introduction.mdx', '11-about-founders-company.mdx'],
            'abbotsford': ['01-company-introduction.mdx', '11-about-founders-company.mdx'],
            'logan': ['01-company-introduction.mdx', '11-about-founders-company.mdx'],
            'karl': ['01-company-introduction.mdx', '11-about-founders-company.mdx'],
            
            # Coffee Strategies
            'strategy': ['02-strategy-one-elevate-coffee-game.mdx', '09-strategy-four-coffee-menu-design.mdx', '10-strategy-five-grow-your-brand.mdx'],
            'elevate': ['02-strategy-one-elevate-coffee-game.mdx'],
            'menu design': ['09-strategy-four-coffee-menu-design.mdx'],
            'menu': ['09-strategy-four-coffee-menu-design.mdx', '17-playbook-tip-simple-menu.mdx'],
            'brand': ['10-strategy-five-grow-your-brand.mdx'],
            'white label': ['10-strategy-five-grow-your-brand.mdx'],
            'white labeling': ['10-strategy-five-grow-your-brand.mdx'],
            
            # Coffee Basics
            'specialty coffee': ['04-specialty-coffee-journey.mdx', '01-company-introduction.mdx'],
            'coffee journey': ['04-specialty-coffee-journey.mdx'],
            'bean to cup': ['04-specialty-coffee-journey.mdx'],
            'origins': ['05-origin-beans-flavor-profile.mdx'],
            'flavor': ['05-origin-beans-flavor-profile.mdx'],
            'ethiopian': ['05-origin-beans-flavor-profile.mdx'],
            'kenyan': ['05-origin-beans-flavor-profile.mdx'],
            'storage': ['06-ordering-storing-coffee-fresh.mdx'],
            'freshness': ['06-ordering-storing-coffee-fresh.mdx'],
            'roaster': ['07-pick-perfect-roaster.mdx'],
            'roasting': ['07-pick-perfect-roaster.mdx'],
            
            # Case Studies
            'case study': ['08-case-study-fracpacks.mdx'],
            'fracpacks': ['08-case-study-fracpacks.mdx'],
            'packaging': ['08-case-study-fracpacks.mdx'],
            'cost savings': ['08-case-study-fracpacks.mdx'],
            
            # Operations & Efficiency
            'efficiency': ['25-operational-efficiency-sales.mdx', '13-30-second-fix-profit-win.mdx'],
            'workflow': ['25-operational-efficiency-sales.mdx', '13-30-second-fix-profit-win.mdx'],
            'optimization': ['25-operational-efficiency-sales.mdx', '13-30-second-fix-profit-win.mdx'],
            'skipper': ['14-successful-coffee-program-skipper.mdx'],
            'leadership': ['14-successful-coffee-program-skipper.mdx', '21-how-design-your-team.mdx'],
            'calibration': ['15-difference-good-great-coffee-calibration.mdx'],
            'quality': ['15-difference-good-great-coffee-calibration.mdx'],
            'consistency': ['15-difference-good-great-coffee-calibration.mdx'],
            
            # Equipment
            'espresso machine': ['16-espresso-machine-heartbeat.mdx'],
            'equipment': ['16-espresso-machine-heartbeat.mdx', '12-for-restaurants-groups-chains.mdx'],
            'machine': ['16-espresso-machine-heartbeat.mdx'],
            'maintenance': ['16-espresso-machine-heartbeat.mdx'],
            
            # Menu & Service
            'simple menu': ['17-playbook-tip-simple-menu.mdx'],
            'profitability': ['17-playbook-tip-simple-menu.mdx', '22-sales-improvement-strategies.mdx'],
            'service': ['17-playbook-tip-simple-menu.mdx'],
            
            # Events & Launch
            'playbook': ['18-specialty-coffee-playbook-launch.mdx', '01-company-introduction.mdx'],
            'coffee fest': ['18-specialty-coffee-playbook-launch.mdx', '19-coffee-fest-nyc-coming-hot.mdx'],
            'nyc': ['18-specialty-coffee-playbook-launch.mdx', '19-coffee-fest-nyc-coming-hot.mdx'],
            'launch': ['18-specialty-coffee-playbook-launch.mdx'],
            'event': ['18-specialty-coffee-playbook-launch.mdx', '19-coffee-fest-nyc-coming-hot.mdx'],
            
            # Partnership & Philosophy
            'partnership': ['20-we-dont-push-brand-wrap-around-yours.mdx', '12-for-restaurants-groups-chains.mdx'],
            'philosophy': ['20-we-dont-push-brand-wrap-around-yours.mdx'],
            'collaboration': ['20-we-dont-push-brand-wrap-around-yours.mdx'],
            'support': ['20-we-dont-push-brand-wrap-around-yours.mdx', '11-about-founders-company.mdx'],
            
            # Team & Culture
            'team': ['21-how-design-your-team.mdx', '11-about-founders-company.mdx'],
            'culture': ['21-how-design-your-team.mdx'],
            'hiring': ['21-how-design-your-team.mdx'],
            
            # Enterprise Services
            'restaurants': ['12-for-restaurants-groups-chains.mdx'],
            'chains': ['12-for-restaurants-groups-chains.mdx'],
            'groups': ['12-for-restaurants-groups-chains.mdx'],
            'enterprise': ['12-for-restaurants-groups-chains.mdx'],
            'pricing': ['23-pricing-strategies-profit-optimization.mdx', '12-for-restaurants-groups-chains.mdx'],
            'volume': ['12-for-restaurants-groups-chains.mdx'],
            
            # Learning & Education
            'learn': ['03-what-you-will-learn.mdx'],
            'learning': ['03-what-you-will-learn.mdx'],
            'education': ['03-what-you-will-learn.mdx'],
            'chapter': ['03-what-you-will-learn.mdx'],
            
            # Sales & Revenue Improvement
            'sales': ['22-sales-improvement-strategies.mdx', '09-strategy-four-coffee-menu-design.mdx'],
            'revenue': ['22-sales-improvement-strategies.mdx', '23-pricing-strategies-profit-optimization.mdx'],
            'profit': ['22-sales-improvement-strategies.mdx', '23-pricing-strategies-profit-optimization.mdx'],
            'upselling': ['22-sales-improvement-strategies.mdx', '23-pricing-strategies-profit-optimization.mdx'],
            'upsell': ['22-sales-improvement-strategies.mdx', '23-pricing-strategies-profit-optimization.mdx'],
            'margin': ['23-pricing-strategies-profit-optimization.mdx', '22-sales-improvement-strategies.mdx'],
            'anchor pricing': ['23-pricing-strategies-profit-optimization.mdx'],
            'menu psychology': ['22-sales-improvement-strategies.mdx', '09-strategy-four-coffee-menu-design.mdx'],
            
            # Customer Experience & Retention
            'customer experience': ['24-customer-experience-retention.mdx', '22-sales-improvement-strategies.mdx'],
            'retention': ['24-customer-experience-retention.mdx'],
            'loyalty': ['24-customer-experience-retention.mdx', '10-strategy-five-grow-your-brand.mdx'],
            'customer satisfaction': ['24-customer-experience-retention.mdx'],
            'repeat business': ['24-customer-experience-retention.mdx', '22-sales-improvement-strategies.mdx'],
            'brand loyalty': ['24-customer-experience-retention.mdx', '10-strategy-five-grow-your-brand.mdx'],
            
            # Operational Efficiency & Sales
            'throughput': ['25-operational-efficiency-sales.mdx'],
            'productivity': ['25-operational-efficiency-sales.mdx'],
            'cost reduction': ['25-operational-efficiency-sales.mdx', '23-pricing-strategies-profit-optimization.mdx'],
            'operational': ['25-operational-efficiency-sales.mdx', '13-30-second-fix-profit-win.mdx']
        }
    
    def get_similar_entries(self, entry_id: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Find similar entries based on content similarity"""
        try:
            entries = self._get_entries_cached()
            target_entry = next((e for e in entries if e['id'] == entry_id), None)
            
            if not target_entry:
                return []
            
            # Calculate similarity scores
            similar_entries = []
            target_keywords = set(target_entry.get('keywords', []))
            target_topic = target_entry.get('topic', '')
            
            for entry in entries:
                if entry['id'] == entry_id:
                    continue
                
                # Calculate keyword overlap
                entry_keywords = set(entry.get('keywords', []))
                keyword_overlap = len(target_keywords.intersection(entry_keywords))
                
                # Topic similarity
                topic_similarity = 1.0 if entry.get('topic') == target_topic else 0.0
                
                # Combined similarity score
                similarity_score = keyword_overlap * 0.7 + topic_similarity * 0.3
                
                if similarity_score > 0:
                    similar_entries.append((entry, similarity_score))
            
            # Sort by similarity and return top results
            similar_entries.sort(key=lambda x: x[1], reverse=True)
            return [entry for entry, score in similar_entries[:max_results]]
            
        except Exception as e:
            print(f"Error finding similar entries: {e}")
            return []
    
    def get_entry_by_id(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific entry by ID with caching"""
        try:
            entries = self._get_entries_cached()
            return self._cache.get(entry_id)
        except Exception as e:
            print(f"Error getting entry {entry_id}: {e}")
            return None
    
    def get_topics(self) -> List[str]:
        """Get all unique topics in the knowledge base"""
        try:
            entries = self._get_entries_cached()
            topics = set()
            for entry in entries:
                topic = entry.get('topic', '')
                if topic:
                    topics.add(topic)
            return sorted(list(topics))
        except Exception as e:
            print(f"Error getting topics: {e}")
            return []
    
    def get_tags(self) -> List[str]:
        """Get all unique tags in the knowledge base"""
        try:
            entries = self._get_entries_cached()
            tags = set()
            for entry in entries:
                entry_tags = entry.get('tags', [])
                tags.update(entry_tags)
            return sorted(list(tags))
        except Exception as e:
            print(f"Error getting tags: {e}")
            return []
    
    def search_by_topic(self, topic: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search entries by specific topic"""
        try:
            entries = self._get_entries_cached()
            topic_entries = [entry for entry in entries if entry.get('topic', '').lower() == topic.lower()]
            return topic_entries[:max_results]
        except Exception as e:
            print(f"Error searching by topic: {e}")
            return []
    
    def search_by_tag(self, tag: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search entries by specific tag"""
        try:
            entries = self._get_entries_cached()
            tag_entries = [entry for entry in entries if tag.lower() in [t.lower() for t in entry.get('tags', [])]]
            return tag_entries[:max_results]
        except Exception as e:
            print(f"Error searching by tag: {e}")
            return []

# Example usage and testing
if __name__ == "__main__":
    # Initialize the enhanced coffee knowledge base
    kb = EnhancedCoffeeKnowledgeBase()
    
    # Test enhanced search functionality
    test_queries = [
        "espresso machine maintenance",
        "menu design for sales",
        "coffee pricing strategies",
        "customer retention",
        "operational efficiency",
        "specialty coffee quality"
    ]
    
    print("Enhanced Coffee Knowledge Base - Accuracy Test")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\nSearching for: '{query}'")
        results = kb.search_knowledge_base(query, max_results=3)
        print(f"Found {len(results)} results")
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title']} ({result['filename']})")
            print(f"     Topic: {result['topic']}")
            print(f"     Tags: {', '.join(result['tags'][:3])}...")
    
    # Test similar entries
    print(f"\n\nSimilar entries to '01-company-introduction':")
    similar = kb.get_similar_entries('01-company-introduction', max_results=3)
    for entry in similar:
        print(f"  - {entry['title']} ({entry['filename']})")
