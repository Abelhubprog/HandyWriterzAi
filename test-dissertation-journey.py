#!/usr/bin/env python3
"""
HandyWriterz Dissertation Journey Test Suite
===========================================
Comprehensive end-to-end test for YC Demo Day readiness
Tests the complete workflow from multimodal file upload to final dissertation output

Test Scenario: PhD Dissertation on "AI-Powered Educational Technology Impact"
- 10 diverse files (PDF, DOCX, audio interview, video lecture, images)
- Complex academic requirements with citations
- Full agent orchestration validation
"""

import asyncio
import aiohttp
import json
import time
from pathlib import Path
import tempfile
import os
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DissertationJourneyTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.test_files = []
        self.trace_id = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def create_test_files(self) -> List[Dict[str, Any]]:
        """Create 10 test files representing a real dissertation scenario."""
        temp_dir = Path(tempfile.mkdtemp(prefix="dissertation_test_"))
        logger.info(f"📁 Creating test files in {temp_dir}")
        
        test_files = [
            {
                "name": "literature_review_ai_education.pdf",
                "type": "application/pdf",
                "content": """# Literature Review: AI in Educational Technology

## Abstract
This literature review examines the current state of artificial intelligence applications in educational technology, focusing on personalized learning systems, intelligent tutoring systems, and adaptive assessment platforms.

## Introduction
The integration of artificial intelligence (AI) into educational technology has transformed the landscape of learning and instruction. This review synthesizes findings from 127 peer-reviewed articles published between 2019-2024.

## Key Findings

### 1. Personalized Learning Systems
Research by Smith et al. (2023) demonstrates that AI-powered personalized learning platforms improve student engagement by 35% and learning outcomes by 28%. The study involved 2,847 students across 15 universities.

### 2. Intelligent Tutoring Systems
Johnson & Lee (2024) found that intelligent tutoring systems using natural language processing show significant improvements in problem-solving skills, particularly in STEM subjects.

### 3. Adaptive Assessment
The meta-analysis by Rodriguez et al. (2023) covering 45 studies reveals that adaptive assessment powered by machine learning algorithms reduces test anxiety while maintaining assessment validity.

## Theoretical Framework
The Technology Acceptance Model (TAM) serves as the primary theoretical lens for understanding student adoption of AI-powered educational tools.

## Gaps in Literature
Despite extensive research, significant gaps remain in:
- Long-term impact studies
- Cross-cultural validation
- Privacy and ethical considerations

## Conclusion
AI integration in educational technology shows promising results but requires careful consideration of implementation strategies and ethical implications.

## References
1. Smith, A., Jones, B., & Wilson, C. (2023). Personalized learning through AI: A comprehensive study. Journal of Educational Technology, 45(3), 234-251.
2. Johnson, D., & Lee, M. (2024). Natural language processing in intelligent tutoring systems. Computers & Education, 198, 104-117.
3. Rodriguez, E., et al. (2023). Meta-analysis of adaptive assessment systems. Educational Assessment, 28(2), 89-107.
""",
                "size": 2048
            },
            {
                "name": "research_methodology.docx",
                "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "content": """Research Methodology

Mixed Methods Approach

This dissertation employs a sequential explanatory mixed methods design combining quantitative and qualitative research methodologies.

Phase 1: Quantitative Study
- Sample: 1,250 undergraduate students from 8 universities
- Design: Randomized controlled trial
- Duration: 12 months
- Instruments: Pre/post assessments, engagement metrics, learning analytics

Phase 2: Qualitative Study
- Semi-structured interviews with 45 participants
- Focus groups with faculty (n=12)
- Phenomenological analysis approach

Data Collection Procedures
1. Baseline assessment of digital literacy
2. Implementation of AI-powered learning platform
3. Monthly progress monitoring
4. Post-intervention assessment
5. Follow-up interviews

Ethical Considerations
- IRB approval obtained (Protocol #2024-AI-EDU-001)
- Informed consent from all participants
- Data privacy protection measures
- Right to withdraw without penalty

Statistical Analysis Plan
- Descriptive statistics for demographic data
- ANOVA for group comparisons
- Multiple regression for predictive modeling
- Effect size calculations (Cohen's d)
- Thematic analysis for qualitative data

Validity and Reliability
- Content validity through expert review
- Construct validity via factor analysis
- Internal consistency (Cronbach's α > 0.85)
- Inter-rater reliability for qualitative coding

Limitations
- Generalizability constraints
- Technology access variations
- Temporal factors in longitudinal design
""",
                "size": 1534
            },
            {
                "name": "expert_interview_dr_chen.mp3",
                "type": "audio/mpeg",
                "content": "AUDIO_PLACEHOLDER_FOR_TRANSCRIPT",
                "transcript": """Dr. Chen Interview Transcript - AI Education Expert

Interviewer: Could you share your thoughts on the current state of AI in educational technology?

Dr. Chen: Absolutely. We're witnessing a paradigm shift in how we approach personalized learning. The algorithms we're developing can now analyze learning patterns in real-time and adapt content delivery to individual student needs. What's particularly exciting is the natural language processing capabilities that allow for more intuitive student-AI interactions.

Interviewer: What challenges do you see in implementation?

Dr. Chen: The biggest challenge isn't technical—it's cultural. Educational institutions are traditionally conservative, and there's resistance to change. We also have significant concerns about data privacy and algorithmic bias. Students from different socioeconomic backgrounds may not have equal access to these technologies, potentially widening the digital divide.

Interviewer: How do you see AI education evolving in the next 5 years?

Dr. Chen: I predict we'll see more sophisticated multimodal AI systems that can process text, audio, and visual inputs simultaneously. Imagine an AI tutor that can read your facial expressions during a video call and adjust its teaching approach accordingly. We're also moving toward more collaborative AI—systems that work alongside human teachers rather than replacing them.

The key is maintaining the human element while leveraging AI's strengths in data processing and pattern recognition. Education is fundamentally about human connection and inspiration, and AI should enhance, not diminish, that experience.

[Interview duration: 45 minutes, transcribed using automated system with manual verification]
""",
                "size": 3072
            },
            {
                "name": "lecture_cognitive_load_theory.mp4",
                "type": "video/mp4",
                "content": "VIDEO_PLACEHOLDER_FOR_ANALYSIS",
                "video_analysis": """Video Lecture Analysis: Cognitive Load Theory in AI-Enhanced Learning

Duration: 28 minutes
Speaker: Prof. Sarah Williams, Educational Psychology
Context: Graduate seminar on learning theory applications

Key Visual Elements:
- Slides showing Cognitive Load Theory framework
- Diagrams of working memory capacity
- Student engagement metrics dashboard
- AI algorithm visualization

Main Concepts Covered:
1. Intrinsic, extraneous, and germane cognitive load
2. How AI can reduce extraneous load through personalization
3. Optimization strategies for learning environments
4. Empirical evidence from recent studies

Student Questions & Discussion:
- Concerns about over-reliance on AI systems
- Discussion of individual differences in cognitive processing
- Practical applications in course design

Technical Quality:
- Clear audio throughout
- High-resolution slides and diagrams
- Effective use of interactive elements
- Student faces visible for engagement analysis

Pedagogical Insights:
- Demonstrates effective integration of theory and practice
- Shows real-world applications of AI in educational settings
- Highlights importance of balancing human and artificial intelligence

Relevance to Dissertation:
- Provides theoretical foundation for AI implementation
- Offers practical examples of successful integration
- Supports arguments for personalized learning approaches
""",
                "size": 4096
            },
            {
                "name": "survey_data_analysis.xlsx",
                "type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "content": """Survey Data Analysis - AI Education Adoption

Dataset: Student Technology Acceptance Survey
N = 1,847 respondents across 12 institutions
Collection Period: January 2024 - March 2024

Key Variables:
- Demographics (age, gender, academic level, field of study)
- Technology experience (digital literacy score, prior AI exposure)
- Attitudes toward AI (perceived usefulness, ease of use, trust)
- Learning outcomes (GPA change, engagement scores, completion rates)
- Behavioral intentions (willingness to use, recommendation likelihood)

Descriptive Statistics:
- Mean age: 21.3 years (SD = 3.8)
- Gender distribution: 52% female, 47% male, 1% non-binary
- Fields of study: 34% STEM, 28% Liberal Arts, 23% Business, 15% Other

Key Findings:
1. Strong positive correlation (r = 0.73) between digital literacy and AI acceptance
2. Significant improvement in learning outcomes for high AI engagement group
3. Gender differences in trust levels (p < 0.001)
4. Age negatively correlated with adoption intentions (r = -0.31)

Statistical Models:
- Multiple regression predicting AI adoption (R² = 0.68)
- Structural equation model for technology acceptance (CFI = 0.96)
- Multilevel analysis accounting for institutional differences

Data Quality Indicators:
- Response rate: 68.3%
- Missing data: <5% for all key variables
- Internal consistency: α = 0.89 for main scales
- Factor loadings all > 0.60
""",
                "size": 2560
            },
            {
                "name": "theoretical_framework_diagram.png",
                "type": "image/png",
                "content": "IMAGE_PLACEHOLDER_FOR_ANALYSIS",
                "image_description": """Theoretical Framework Diagram Analysis

Visual Elements:
- Central hexagon labeled "AI-Enhanced Learning Ecosystem"
- Six connected components around the perimeter:
  1. Learner Characteristics (top)
  2. AI Technology Features (top-right)
  3. Learning Content (bottom-right)
  4. Pedagogical Approaches (bottom)
  5. Institutional Context (bottom-left)
  6. Societal Factors (top-left)

Connecting Elements:
- Bidirectional arrows showing interactions between all components
- Color-coded pathways indicating different types of influence:
  - Blue arrows: Direct technological influence
  - Green arrows: Pedagogical relationships
  - Red arrows: Contextual constraints
  - Purple arrows: Feedback loops

Key Annotations:
- "Personalization Algorithms" linking learner characteristics to AI features
- "Adaptive Assessment" connecting content to pedagogical approaches
- "Privacy & Ethics" spanning societal factors to institutional context
- "Digital Equity" bridging societal factors to learner characteristics

Framework Integration:
- Technology Acceptance Model (TAM) elements highlighted
- Social Cognitive Theory components indicated
- Cultural-Historical Activity Theory (CHAT) principles embedded

Research Implications:
- Shows complexity of AI implementation in educational contexts
- Illustrates need for holistic approach to technology integration
- Identifies key variables for empirical investigation
- Guides development of research hypotheses and data collection strategies
""",
                "size": 1024
            },
            {
                "name": "case_study_university_implementation.pdf",
                "type": "application/pdf",
                "content": """Case Study: University X AI Implementation

Executive Summary
This case study examines the 18-month implementation of an AI-powered learning management system at a mid-size public university (enrollment: 15,000 students).

Background
University X faced challenges with:
- Low student engagement in online courses (35% completion rate)
- High variability in learning outcomes across demographics
- Faculty resistance to educational technology
- Limited resources for individualized instruction

Implementation Process

Phase 1: Planning (Months 1-3)
- Stakeholder analysis and buy-in
- Technology infrastructure assessment
- Pilot program design
- Faculty training curriculum development

Phase 2: Pilot Testing (Months 4-9)
- Limited rollout to 3 departments
- 450 students and 15 faculty participants
- Continuous monitoring and feedback collection
- Iterative system improvements

Phase 3: Full Implementation (Months 10-15)
- Campus-wide deployment
- 8,500 students across all departments
- Comprehensive support system
- Data collection and analysis

Phase 4: Evaluation (Months 16-18)
- Comprehensive outcome assessment
- ROI analysis
- Sustainability planning
- Lessons learned documentation

Key Outcomes

Student Performance:
- 42% increase in course completion rates
- 28% improvement in average final grades
- 67% reduction in dropout rates for at-risk students
- Significant reduction in achievement gaps between demographic groups

Faculty Satisfaction:
- Initial skepticism (25% positive) → Strong support (78% positive)
- Reduced grading workload by 35%
- Improved ability to identify struggling students
- Enhanced data-driven decision making

Institutional Benefits:
- $2.3M cost savings through improved retention
- 15% increase in student satisfaction scores
- Recognition as innovative institution
- Improved accreditation outcomes

Challenges and Solutions

Technical Challenges:
- Integration with legacy systems → Custom API development
- Server capacity issues → Cloud infrastructure upgrade
- Data privacy concerns → Enhanced security protocols

Human Factors:
- Faculty resistance → Comprehensive training and incentives
- Student digital divide → Device lending program
- Change management → Gradual rollout with champions

Lessons Learned
1. Stakeholder engagement is critical for success
2. Technical infrastructure must be robust and scalable
3. Training and support are ongoing needs, not one-time events
4. Data privacy and ethics must be addressed proactively
5. Cultural change takes time and requires patience

Recommendations
- Start small with willing early adopters
- Invest heavily in training and support
- Maintain open communication about challenges and successes
- Plan for long-term sustainability and evolution
- Continuously monitor and evaluate impact

Future Directions
- Advanced natural language processing integration
- Predictive analytics for early intervention
- Cross-institutional data sharing and benchmarking
- Research collaboration opportunities

This case study demonstrates that successful AI implementation requires careful planning, stakeholder engagement, and commitment to continuous improvement.
""",
                "size": 3584
            },
            {
                "name": "statistical_analysis_results.R",
                "type": "text/plain",
                "content": """# Statistical Analysis Results - AI Education Dissertation
# Advanced statistical modeling and analysis

library(tidyverse)
library(lme4)
library(lavaan)
library(psych)
library(ggplot2)

# Data Import and Cleaning
dissertation_data <- read_csv("ai_education_survey_clean.csv")
summary(dissertation_data)

# Descriptive Statistics
describe(dissertation_data[, c("ai_acceptance", "learning_outcomes", 
                               "digital_literacy", "trust_score")])

# Correlation Matrix
cor_matrix <- cor(dissertation_data[, c("ai_acceptance", "learning_outcomes", 
                                        "digital_literacy", "trust_score")], 
                  use = "complete.obs")
print(cor_matrix)

# Multiple Regression Analysis
model1 <- lm(ai_acceptance ~ digital_literacy + trust_score + age + gender, 
             data = dissertation_data)
summary(model1)

# Hierarchical Linear Modeling
model2 <- lmer(learning_outcomes ~ ai_acceptance + digital_literacy + 
               (1|institution) + (1|department), 
               data = dissertation_data)
summary(model2)

# Structural Equation Modeling
sem_model <- '
  # Measurement model
  ai_acceptance =~ ai_useful + ai_easy + ai_intention
  digital_literacy =~ tech_skills + online_exp + digital_conf
  learning_outcomes =~ gpa_change + engagement + satisfaction
  
  # Structural model
  learning_outcomes ~ ai_acceptance + digital_literacy
  ai_acceptance ~ digital_literacy + trust_score
'

fit <- sem(sem_model, data = dissertation_data)
summary(fit, fit.measures = TRUE)

# Effect Size Calculations
library(effectsize)
cohens_d(dissertation_data$learning_outcomes, 
         dissertation_data$ai_acceptance_group)

# Advanced Visualizations
ggplot(dissertation_data, aes(x = ai_acceptance, y = learning_outcomes)) +
  geom_point(alpha = 0.6) +
  geom_smooth(method = "lm", se = TRUE) +
  facet_wrap(~institution) +
  labs(title = "AI Acceptance vs Learning Outcomes by Institution",
       x = "AI Acceptance Score",
       y = "Learning Outcomes Score") +
  theme_minimal()

# Moderation Analysis
moderation_model <- lm(learning_outcomes ~ ai_acceptance * gender + 
                       digital_literacy + age, 
                       data = dissertation_data)
summary(moderation_model)

# Mediation Analysis (using lavaan)
mediation_model <- '
  # Direct effect
  learning_outcomes ~ c*ai_acceptance
  
  # Mediator
  engagement ~ a*ai_acceptance
  learning_outcomes ~ b*engagement
  
  # Indirect effect (a*b)
  # Total effect (c + a*b)
  
  indirect := a*b
  total := c + (a*b)
'

med_fit <- sem(mediation_model, data = dissertation_data)
summary(med_fit)

# Bootstrap confidence intervals
boot_fit <- sem(mediation_model, data = dissertation_data, 
                se = "bootstrap", bootstrap = 1000)
parameterEstimates(boot_fit, boot.ci.type = "bca.simple")

# Model Comparison
anova(model1, model2)

# Diagnostics
plot(model1)
car::vif(model1)

# Export Results
write.csv(summary(model1)$coefficients, "regression_results.csv")
ggsave("scatterplot_matrix.png", width = 12, height = 8)

# Final Model Summary
cat("Final Model Results Summary:\\n")
cat("R-squared:", summary(model1)$r.squared, "\\n")
cat("Adjusted R-squared:", summary(model1)$adj.r.squared, "\\n")
cat("F-statistic:", summary(model1)$fstatistic[1], "\\n")
cat("p-value:", pf(summary(model1)$fstatistic[1], 
                   summary(model1)$fstatistic[2], 
                   summary(model1)$fstatistic[3], 
                   lower.tail = FALSE), "\\n")
""",
                "size": 2816
            },
            {
                "name": "focus_group_transcripts.docx",
                "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "content": """Focus Group Transcripts - Faculty Perspectives on AI Education

Session 1: Early Career Faculty (n=6)
Date: March 15, 2024
Duration: 90 minutes
Moderator: Dr. Johnson

Participants:
- Dr. A (Assistant Professor, Computer Science)
- Dr. B (Assistant Professor, Education)
- Dr. C (Lecturer, Mathematics)
- Dr. D (Assistant Professor, Psychology)
- Dr. E (Clinical Assistant Professor, Business)
- Dr. F (Assistant Professor, English)

Key Themes Identified:

1. Technology Integration Enthusiasm
Dr. A: "As someone who grew up with technology, I'm excited about AI's potential. My students are digital natives, and they expect interactive, responsive learning experiences."

Dr. B: "The personalization aspect is what draws me in. I've always struggled with meeting diverse learning needs in large classes. AI could help us scale individualized instruction."

2. Concerns About Academic Integrity
Dr. F: "My biggest worry is cheating. How do we ensure students are actually learning when AI can write essays for them? We need robust detection systems and new assessment methods."

Dr. C: "It's not just about detection—we need to rethink what we're assessing. Maybe we should focus more on process than product, on thinking skills rather than information recall."

3. Workload and Training Implications
Dr. D: "I'm willing to learn, but I need time and support. We're already overwhelmed with teaching loads and research expectations. How do we add AI training to that mix?"

Dr. E: "The initial investment is daunting, but I think it could save time in the long run. Automated grading, early warning systems for struggling students—these could be game-changers."

Session 2: Senior Faculty (n=6)
Date: March 22, 2024
Duration: 90 minutes
Moderator: Dr. Smith

[Similar format continues with different perspectives and concerns from senior faculty...]

Cross-Session Analysis:

Common Concerns:
- Need for comprehensive training and support
- Questions about data privacy and student rights
- Impact on traditional pedagogical approaches
- Resource allocation and institutional commitment

Positive Perspectives:
- Potential for enhanced student engagement
- Opportunities for data-driven instruction
- Ability to address diverse learning needs
- Possibility of reducing routine tasks

Recommendations from Participants:
1. Gradual implementation with voluntary participation
2. Extensive professional development opportunities
3. Clear policies on AI use and academic integrity
4. Student voice in system design and implementation
5. Regular evaluation and adjustment processes

Implications for Dissertation:
- Faculty readiness varies significantly by career stage
- Training and support are critical success factors
- Need for cultural change alongside technological change
- Importance of stakeholder involvement in implementation planning
""",
                "size": 2304
            },
            {
                "name": "policy_analysis_ai_governance.pdf",
                "type": "application/pdf",
                "content": """AI Governance in Higher Education: Policy Analysis

Abstract
This analysis examines current policies governing AI use in higher education institutions, identifying gaps and proposing frameworks for ethical AI implementation in academic settings.

Introduction
As AI adoption accelerates in higher education, institutions struggle with governance frameworks that balance innovation with ethical considerations. This analysis reviews 47 institutional policies from universities across North America and Europe.

Current Policy Landscape

Policy Categories:
1. Academic Integrity Policies (87% of institutions)
2. Data Privacy and Security (92% of institutions)
3. Faculty Guidelines for AI Use (34% of institutions)
4. Student Rights and AI Systems (23% of institutions)
5. Algorithmic Bias Prevention (12% of institutions)

Key Findings:

Strengths in Current Policies:
- Strong emphasis on data protection (GDPR compliance in European institutions)
- Clear academic misconduct definitions
- Established grievance procedures for grade disputes
- Well-defined roles for IT support and security

Policy Gaps:
- Limited guidance on ethical AI development and deployment
- Insufficient transparency requirements for AI decision-making
- Lack of student consent frameworks for AI-mediated learning
- Minimal provision for algorithmic auditing and bias detection
- Inadequate training requirements for faculty and staff

Comparative Analysis

European Approach:
- Strong regulatory compliance focus
- Emphasis on individual rights and consent
- Comprehensive data protection measures
- Limited innovation flexibility

North American Approach:
- Market-driven innovation emphasis
- Institutional autonomy in policy development
- Variable compliance standards
- Greater experimentation with AI applications

Best Practice Examples:

University of Edinburgh (UK):
- Comprehensive AI ethics committee
- Mandatory algorithmic impact assessments
- Student representation in AI governance
- Regular policy reviews and updates

Stanford University (USA):
- Human-AI interaction principles
- Transparent algorithm documentation
- Faculty development programs
- Student AI literacy requirements

Policy Recommendations:

1. Establish AI Ethics Committees
- Multi-stakeholder representation
- Regular review cycles
- Clear decision-making authority
- Public reporting requirements

2. Implement Transparency Standards
- Algorithm documentation requirements
- Decision-making process disclosure
- Performance metrics publication
- Bias auditing protocols

3. Develop Consent Frameworks
- Informed consent for AI system use
- Opt-out mechanisms where feasible
- Clear data usage explanations
- Regular consent renewal processes

4. Create Training Requirements
- Faculty AI literacy programs
- Student digital citizenship education
- Staff development on AI governance
- Leadership training on AI strategy

5. Establish Accountability Mechanisms
- Regular algorithmic audits
- Performance monitoring systems
- Grievance and appeal processes
- External oversight arrangements

Implementation Strategies:

Phased Approach:
- Phase 1: Policy development and stakeholder engagement
- Phase 2: Pilot programs with selected departments
- Phase 3: Full implementation with monitoring systems
- Phase 4: Evaluation and continuous improvement

Resource Requirements:
- Dedicated staff for AI governance
- Technical infrastructure for auditing
- Training program development
- External expertise and consultation

Risk Management:
- Legal liability assessment
- Reputational risk evaluation
- Financial impact analysis
- Stakeholder resistance mitigation

Conclusion
Effective AI governance in higher education requires comprehensive policies that balance innovation with ethical considerations. Institutions must move beyond reactive approaches to develop proactive frameworks that protect stakeholder interests while enabling beneficial AI applications.

Future Research Directions:
- Longitudinal studies of policy effectiveness
- Cross-institutional comparative analyses
- Student and faculty perception studies
- International regulatory harmonization efforts

References [47 sources listed]
""",
                "size": 4352
            }
        ]
        
        # Create actual files in temp directory
        for i, file_info in enumerate(test_files):
            file_path = temp_dir / file_info["name"]
            file_path.write_text(file_info["content"], encoding="utf-8")
            
            test_files[i]["path"] = str(file_path)
            test_files[i]["size"] = len(file_info["content"].encode("utf-8"))
            
        logger.info(f"✅ Created {len(test_files)} test files")
        self.test_files = test_files
        return test_files

    async def upload_files(self) -> List[str]:
        """Upload all test files to the backend."""
        logger.info("📤 Starting file upload process...")
        file_ids = []
        
        for file_info in self.test_files:
            try:
                data = aiohttp.FormData()
                
                with open(file_info["path"], "rb") as f:
                    data.add_field('file', f, filename=file_info["name"], 
                                 content_type=file_info["type"])
                
                async with self.session.post(f"{self.base_url}/api/files", 
                                           data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        file_ids.append(result.get("file_id"))
                        logger.info(f"✅ Uploaded {file_info['name']} -> {result.get('file_id')}")
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Failed to upload {file_info['name']}: {error_text}")
                        
            except Exception as e:
                logger.error(f"❌ Error uploading {file_info['name']}: {str(e)}")
        
        logger.info(f"📤 Successfully uploaded {len(file_ids)}/{len(self.test_files)} files")
        return file_ids

    async def submit_dissertation_request(self, file_ids: List[str]) -> Dict[str, Any]:
        """Submit the comprehensive dissertation generation request."""
        
        dissertation_prompt = """
        Create a comprehensive PhD dissertation on "The Impact of Artificial Intelligence on Educational Technology: A Mixed-Methods Analysis of Student Learning Outcomes and Faculty Adoption".

        Based on the uploaded files (literature review, methodology, interview transcripts, video lecture analysis, survey data, case study, statistical analysis, focus group transcripts, and policy analysis), generate a complete dissertation with the following specifications:

        STRUCTURE REQUIREMENTS:
        1. Title Page and Abstract (500 words)
        2. Introduction and Problem Statement (2,000 words)
        3. Literature Review (5,000 words) - synthesize uploaded PDF literature review
        4. Theoretical Framework (1,500 words) - use uploaded diagram and integrate theories
        5. Methodology (3,000 words) - expand on uploaded methodology document
        6. Results and Analysis (4,000 words) - incorporate statistical analysis and survey data
        7. Discussion (3,000 words) - integrate case study findings and expert interviews
        8. Policy Implications (1,500 words) - use policy analysis document
        9. Conclusions and Future Research (1,000 words)
        10. References (comprehensive citation list)

        ACADEMIC REQUIREMENTS:
        - Use Harvard citation style throughout
        - Minimum 150 scholarly references
        - Maintain consistent academic tone
        - Include tables and figures where appropriate
        - Ensure logical flow between sections
        - Address ethical considerations
        - Demonstrate original contribution to knowledge

        INTEGRATION REQUIREMENTS:
        - Synthesize all uploaded materials coherently
        - Reference specific data from statistical analysis
        - Quote relevant sections from interviews and focus groups
        - Incorporate insights from video lecture analysis
        - Connect case study findings to broader implications
        - Align with policy analysis recommendations

        QUALITY STANDARDS:
        - Doctoral-level academic writing
        - Clear argumentation and evidence-based conclusions
        - Proper statistical interpretation
        - Balanced presentation of findings
        - Critical analysis of limitations
        - Practical recommendations for practitioners

        Please ensure the final dissertation is publication-ready and demonstrates mastery of the subject matter through sophisticated analysis and synthesis of the provided materials.
        """

        payload = {
            "prompt": dissertation_prompt,
            "mode": "dissertation",
            "file_ids": file_ids,
            "user_params": {
                "citationStyle": "Harvard",
                "wordCount": 20000,
                "model": "gemini-2.0-flash-exp",
                "user_id": "test_user_dissertation_journey",
                "academic_level": "phd",
                "subject_area": "educational_technology",
                "requirements": [
                    "comprehensive_literature_synthesis",
                    "advanced_statistical_analysis",
                    "multimodal_data_integration",
                    "policy_recommendations",
                    "ethical_considerations"
                ]
            }
        }

        logger.info("🚀 Submitting dissertation generation request...")
        
        try:
            async with self.session.post(f"{self.base_url}/api/chat",
                                       json=payload,
                                       headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    result = await response.json()
                    self.trace_id = result.get("trace_id")
                    logger.info(f"✅ Request submitted successfully. Trace ID: {self.trace_id}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Request failed: {response.status} - {error_text}")
                    return {"error": error_text}
                    
        except Exception as e:
            logger.error(f"❌ Error submitting request: {str(e)}")
            return {"error": str(e)}

    async def monitor_progress(self, timeout: int = 1800) -> Dict[str, Any]:
        """Monitor the dissertation generation progress via WebSocket."""
        if not self.trace_id:
            logger.error("❌ No trace ID available for monitoring")
            return {"error": "No trace ID"}

        logger.info(f"👁️ Monitoring progress for trace ID: {self.trace_id}")
        
        import websockets
        
        try:
            uri = f"ws://localhost:8000/ws/{self.trace_id}"
            async with websockets.connect(uri) as websocket:
                start_time = time.time()
                events = []
                final_result = None
                
                while time.time() - start_time < timeout:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                        data = json.loads(message)
                        
                        events.append(data)
                        
                        if data.get("type") == "stream":
                            logger.info(f"📝 Stream: {data.get('text', '')[:100]}...")
                            
                        elif data.get("type") == "agent_activity":
                            agent = data.get("agent", "unknown")
                            status = data.get("status", "unknown")
                            logger.info(f"🤖 Agent {agent}: {status}")
                            
                        elif data.get("type") == "cost_update":
                            cost = data.get("cost_usd", 0)
                            logger.info(f"💰 Current cost: ${cost:.4f}")
                            
                        elif data.get("type") == "completion":
                            logger.info("🎉 Dissertation generation completed!")
                            final_result = data
                            break
                            
                    except asyncio.TimeoutError:
                        logger.warning("⏰ WebSocket timeout, continuing to monitor...")
                        continue
                        
                return {
                    "events": events,
                    "final_result": final_result,
                    "total_events": len(events),
                    "duration": time.time() - start_time
                }
                
        except Exception as e:
            logger.error(f"❌ WebSocket monitoring error: {str(e)}")
            return {"error": str(e)}

    async def validate_output_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the quality of the generated dissertation."""
        logger.info("🔍 Validating dissertation output quality...")
        
        validation_results = {
            "word_count": 0,
            "citation_count": 0,
            "section_count": 0,
            "quality_score": 0.0,
            "has_abstract": False,
            "has_conclusion": False,
            "has_references": False,
            "academic_tone": False,
            "coherence_score": 0.0,
            "validation_passed": False
        }
        
        if not result or "response" not in result:
            logger.error("❌ No response content to validate")
            return validation_results
        
        content = result["response"]
        
        # Word count validation
        word_count = len(content.split())
        validation_results["word_count"] = word_count
        logger.info(f"📊 Word count: {word_count}")
        
        # Citation count (basic regex for Harvard style)
        import re
        citations = re.findall(r'\([A-Z][a-z]+(?:,|\s+&|\s+and)\s+[A-Z][a-z]+,?\s+\d{4}\)', content)
        validation_results["citation_count"] = len(citations)
        logger.info(f"📚 Citations found: {len(citations)}")
        
        # Section structure validation
        sections = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        validation_results["section_count"] = len(sections)
        logger.info(f"📑 Sections found: {len(sections)}")
        
        # Content structure checks
        validation_results["has_abstract"] = "abstract" in content.lower()
        validation_results["has_conclusion"] = "conclusion" in content.lower()
        validation_results["has_references"] = "references" in content.lower()
        
        # Quality scoring
        quality_metrics = [
            word_count >= 15000,  # Sufficient length
            len(citations) >= 50,  # Adequate citations
            len(sections) >= 8,   # Proper structure
            validation_results["has_abstract"],
            validation_results["has_conclusion"],
            validation_results["has_references"]
        ]
        
        validation_results["quality_score"] = sum(quality_metrics) / len(quality_metrics)
        validation_results["validation_passed"] = validation_results["quality_score"] >= 0.8
        
        logger.info(f"✅ Validation complete. Quality score: {validation_results['quality_score']:.2f}")
        
        return validation_results

    async def run_complete_test(self) -> Dict[str, Any]:
        """Run the complete dissertation journey test."""
        logger.info("🚀 Starting comprehensive dissertation journey test...")
        
        test_results = {
            "start_time": time.time(),
            "test_status": "running",
            "files_created": 0,
            "files_uploaded": 0,
            "request_submitted": False,
            "monitoring_completed": False,
            "validation_results": None,
            "total_cost": 0.0,
            "total_duration": 0.0,
            "errors": []
        }
        
        try:
            # Step 1: Create test files
            logger.info("\n" + "="*60)
            logger.info("STEP 1: Creating test files")
            logger.info("="*60)
            
            files = self.create_test_files()
            test_results["files_created"] = len(files)
            
            # Step 2: Upload files
            logger.info("\n" + "="*60)
            logger.info("STEP 2: Uploading files to backend")
            logger.info("="*60)
            
            file_ids = await self.upload_files()
            test_results["files_uploaded"] = len(file_ids)
            
            if len(file_ids) == 0:
                raise Exception("No files were successfully uploaded")
            
            # Step 3: Submit dissertation request
            logger.info("\n" + "="*60)
            logger.info("STEP 3: Submitting dissertation generation request")
            logger.info("="*60)
            
            submission_result = await self.submit_dissertation_request(file_ids)
            if "error" in submission_result:
                raise Exception(f"Request submission failed: {submission_result['error']}")
            
            test_results["request_submitted"] = True
            test_results["total_cost"] = submission_result.get("cost_usd", 0.0)
            
            # Step 4: Monitor progress
            logger.info("\n" + "="*60)
            logger.info("STEP 4: Monitoring dissertation generation progress")
            logger.info("="*60)
            
            monitoring_result = await self.monitor_progress()
            if "error" in monitoring_result:
                logger.warning(f"Monitoring encountered issues: {monitoring_result['error']}")
            else:
                test_results["monitoring_completed"] = True
                final_result = monitoring_result.get("final_result")
                
                if final_result:
                    # Step 5: Validate output quality
                    logger.info("\n" + "="*60)
                    logger.info("STEP 5: Validating dissertation quality")
                    logger.info("="*60)
                    
                    validation_results = await self.validate_output_quality(final_result)
                    test_results["validation_results"] = validation_results
                    test_results["total_cost"] = final_result.get("cost_usd", test_results["total_cost"])
            
            test_results["test_status"] = "completed"
            
        except Exception as e:
            logger.error(f"❌ Test failed: {str(e)}")
            test_results["errors"].append(str(e))
            test_results["test_status"] = "failed"
        
        finally:
            test_results["total_duration"] = time.time() - test_results["start_time"]
            
        return test_results

    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive test report."""
        report = f"""
HandyWriterz Dissertation Journey Test Report
============================================
Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}
Test Status: {results['test_status'].upper()}
Total Duration: {results['total_duration']:.1f} seconds

File Processing Results:
- Files Created: {results['files_created']}/10
- Files Uploaded: {results['files_uploaded']}/10
- Upload Success Rate: {(results['files_uploaded']/10)*100:.1f}%

Request Processing:
- Request Submitted: {'✅ Yes' if results['request_submitted'] else '❌ No'}
- Monitoring Completed: {'✅ Yes' if results['monitoring_completed'] else '❌ No'}

Cost Analysis:
- Total Cost: ${results.get('total_cost', 0.0):.4f}

"""

        if results.get("validation_results"):
            v = results["validation_results"]
            report += f"""Quality Validation Results:
- Word Count: {v['word_count']:,} words
- Citations Found: {v['citation_count']}
- Section Count: {v['section_count']}
- Has Abstract: {'✅ Yes' if v['has_abstract'] else '❌ No'}
- Has Conclusion: {'✅ Yes' if v['has_conclusion'] else '❌ No'}
- Has References: {'✅ Yes' if v['has_references'] else '❌ No'}
- Quality Score: {v['quality_score']:.2f}/1.0
- Validation Passed: {'✅ Yes' if v['validation_passed'] else '❌ No'}

"""

        if results.get("errors"):
            report += f"""Errors Encountered:
"""
            for error in results["errors"]:
                report += f"- {error}\n"

        report += f"""
YC Demo Readiness Assessment:
============================
"""
        
        # Calculate demo readiness score
        readiness_factors = [
            results['files_created'] == 10,
            results['files_uploaded'] >= 8,
            results['request_submitted'],
            results['monitoring_completed'],
            results.get('validation_results', {}).get('validation_passed', False)
        ]
        
        readiness_score = sum(readiness_factors) / len(readiness_factors)
        
        report += f"""Demo Readiness Score: {readiness_score:.1%}

Readiness Assessment:
"""
        
        if readiness_score >= 0.9:
            report += "🎉 EXCELLENT - System is fully ready for YC Demo Day!"
        elif readiness_score >= 0.7:
            report += "✅ GOOD - System is demo-ready with minor issues to address"
        elif readiness_score >= 0.5:
            report += "⚠️  MODERATE - Significant issues need resolution before demo"
        else:
            report += "❌ POOR - Major system issues prevent demo readiness"

        return report


async def main():
    """Main test execution function."""
    print("🚀 HandyWriterz Dissertation Journey Test Suite")
    print("=" * 60)
    
    async with DissertationJourneyTester() as tester:
        results = await tester.run_complete_test()
        
        # Generate and display report
        report = tester.generate_test_report(results)
        print("\n" + report)
        
        # Save report to file
        report_path = Path("dissertation_test_report.txt")
        report_path.write_text(report)
        print(f"\n📄 Test report saved to: {report_path.absolute()}")
        
        return results

if __name__ == "__main__":
    asyncio.run(main())