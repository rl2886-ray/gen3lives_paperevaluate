console.log('Script loaded!');

const WEIGHTS = {
    content: 0.4,
    narrative: 0.4,
    language: 0.2
};

// File handling functions
async function handleFileUpload(file) {
    console.log('handleFileUpload called with file:', file?.name, file?.type);

    if (!file) {
        console.error('No file provided');
        return;
    }

    // Check file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        alert('File is too large. Maximum size is 5MB.');
        return;
    }

    // Check file type
    const allowedTypes = [
        'text/plain',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/pdf'
    ];

    console.log('File type check:', file.type, allowedTypes.includes(file.type));

    if (!allowedTypes.includes(file.type)) {
        alert('Unsupported file type. Please upload .txt, .doc, .docx, or .pdf files.');
        return;
    }

    try {
        let text;
        if (file.type === 'text/plain') {
            console.log('Reading text file...');
            text = await readTextFile(file);
            console.log('Text file read successfully');
        } else {
            alert('For .doc, .docx, and .pdf files, please copy and paste the content into the text area.');
            return;
        }

        // Update textarea with file content
        const sopText = document.getElementById('sop-text');
        if (!sopText) {
            throw new Error('Text area element not found');
        }

        sopText.value = text;
        // Trigger input event to enable evaluate button
        sopText.dispatchEvent(new Event('input'));
    } catch (error) {
        console.error('Error reading file:', error);
        alert(`Error reading file: ${error.message}. Please try again or paste the text directly.`);
    }
}

function readTextFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(e);
        reader.readAsText(file);
    });
}

// Initialize DOM elements
document.addEventListener('DOMContentLoaded', () => {
    const sopText = document.getElementById('sop-text');
    const evaluateBtn = document.getElementById('evaluate-btn');
    const resultsSection = document.querySelector('.evaluation-results');
    const fileInput = document.getElementById('file-input');
    const fileUploadArea = document.getElementById('file-upload-area');

    console.log('DOM Elements:', {
        sopText: !!sopText,
        evaluateBtn: !!evaluateBtn,
        fileInput: !!fileInput,
        fileUploadArea: !!fileUploadArea
    });

    // Enable/disable evaluate button based on input
    sopText.addEventListener('input', () => {
        evaluateBtn.disabled = !sopText.value.trim();
    });

    // Handle file upload via input
    if (fileInput && fileUploadArea) {
        console.log('Setting up file upload handlers');
        fileInput.addEventListener('change', async (event) => {
            console.log('File input change event triggered');
            const file = event.target.files[0];
            console.log('Selected file:', file?.name, file?.type);
            if (file) await handleFileUpload(file);
        });

        // Handle drag and drop
        fileUploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            fileUploadArea.style.borderColor = 'var(--primary-color)';
        });

        fileUploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            fileUploadArea.style.borderColor = 'var(--border-color)';
        });

        fileUploadArea.addEventListener('drop', async (e) => {
            console.log('File drop event triggered');
            e.preventDefault();
            e.stopPropagation();
            fileUploadArea.style.borderColor = 'var(--border-color)';
            const file = e.dataTransfer.files[0];
            console.log('Dropped file:', file?.name, file?.type);
            if (file) await handleFileUpload(file);
        });
    } else {
        console.error('File upload elements not found:', {
            fileInput: !!fileInput,
            fileUploadArea: !!fileUploadArea
        });
    }

    // Handle evaluation
    evaluateBtn.addEventListener('click', async () => {
        console.log('Evaluate button clicked');
        const text = sopText.value.trim();
        console.log('Text to evaluate:', text.substring(0, 100) + '...');
        const scores = await evaluateText(text);
        console.log('Evaluation completed, displaying scores:', scores);
        displayScores(scores);
        resultsSection.hidden = false;
    });

async function evaluateText(text) {
    console.log('Starting SOP evaluation...');

    // Set loading state for all score cards
    document.querySelectorAll('.score-card').forEach(card => {
        card.classList.add('loading');
    });
    document.querySelector('.final-score').classList.add('loading');

    try {
        // Evaluate each dimension
        console.log('Evaluating content dimension...');
        const contentResult = await evaluateContent(text);
        console.log('Content evaluation complete:', contentResult);

        console.log('Evaluating narrative dimension...');
        const narrativeResult = await evaluateNarrative(text);
        console.log('Narrative evaluation complete:', narrativeResult);

        console.log('Evaluating language dimension...');
        const languageResult = await evaluateLanguage(text);
        console.log('Language evaluation complete:', languageResult);

        // Calculate final score
        const finalScore = (
            contentResult.score * WEIGHTS.content +
            narrativeResult.score * WEIGHTS.narrative +
            languageResult.score * WEIGHTS.language
        ) / 100;

        // Prepare results object
        const results = {
            content: contentResult,
            narrative: narrativeResult,
            language: languageResult,
            final_score: finalScore
        };

        // Generate modification suggestions
        console.log('Generating modification suggestions...');
        const suggestions = await generateModificationSuggestions(text, results);
        console.log('Generated suggestions:', suggestions);
        results.suggestions = suggestions;

        // Display results
        console.log('Displaying evaluation results:', results);
        displayScores(results);

        return results;
    } catch (error) {
        console.error('Error during evaluation:', error);
        document.querySelectorAll('.score-card, .final-score').forEach(card => {
            card.classList.remove('loading');
        });
        throw error;
    }
}

async function evaluateContent(text) {
    const prompt = `Please evaluate this Statement of Purpose (SOP) text for content quality. Focus on:
    - Personal Background Detail
    - Educational Experience Relevance
    - Career Goals Clarity
    - School/Program Choice Reasoning
    - Uniqueness Demonstration
    - Specific Examples

    Provide a score out of 100 and detailed feedback.
    Format your response as: Score: X/100\nFeedback: [your detailed feedback]

    Text to evaluate:
    ${text}`;

    try {
        const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer sk-5aa918e7fa814f4fa8026cf5084edb5a'
            },
            body: JSON.stringify({
                model: "deepseek-chat",
                messages: [{ role: "user", content: prompt }]
            })
        });

        const data = await response.json();
        return parseEvaluationResponse(data.choices[0].message.content);
    } catch (error) {
        console.error('Error evaluating content:', error);
        return { score: 0, feedback: 'Error evaluating content. Please try again.' };
    }
}

async function evaluateNarrative(text) {
    const prompt = `Please evaluate this Statement of Purpose (SOP) text for narrative quality. Focus on:
    - Opening Engagement
    - Narrative Coherence
    - Conflict Resolution
    - Narrative Depth
    - Closing Impression

    Provide a score out of 100 and detailed feedback.
    Format your response as: Score: X/100\nFeedback: [your detailed feedback]

    Text to evaluate:
    ${text}`;

    try {
        const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer sk-5aa918e7fa814f4fa8026cf5084edb5a'
            },
            body: JSON.stringify({
                model: "deepseek-chat",
                messages: [{ role: "user", content: prompt }]
            })
        });

        const data = await response.json();
        return parseEvaluationResponse(data.choices[0].message.content);
    } catch (error) {
        console.error('Error evaluating narrative:', error);
        return { score: 0, feedback: 'Error evaluating narrative. Please try again.' };
    }
}



async function evaluateLanguage(text) {
    const prompt = `Please evaluate this Statement of Purpose (SOP) text for language quality. Focus on:
    - Grammar and mechanics
    - Vocabulary usage
    - Sentence structure
    - Academic tone
    - Overall fluency

    Provide a score out of 100 and detailed feedback.
    Format your response as: Score: X/100\nFeedback: [your detailed feedback]

    Text to evaluate:
    ${text}`;

    try {
        const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer sk-5aa918e7fa814f4fa8026cf5084edb5a'
            },
            body: JSON.stringify({
                model: "deepseek-chat",
                messages: [{ role: "user", content: prompt }]
            })
        });

        const data = await response.json();
        return parseEvaluationResponse(data.choices[0].message.content);
    } catch (error) {
        console.error('Error evaluating language:', error);
        return { score: 0, feedback: 'Error evaluating language. Please try again.' };
    }
}

// Function to generate modification suggestions
async function generateModificationSuggestions(text, scores) {
    console.log('Generating modification suggestions...', { text: text.substring(0, 100) + '...', scores });
    const prompt = `As an expert SOP evaluator, please provide specific suggestions to improve this Statement of Purpose. Focus on the following aspects:

1. Content (${scores.content}/100):
${scores.contentFeedback}

2. Narrative Structure (${scores.narrative}/100):
${scores.narrativeFeedback}

3. Language Usage (${scores.language}/100):
${scores.languageFeedback}

Please analyze the following SOP and provide clear, actionable suggestions for improvement:

${text}

Format your response as a bulleted list of specific suggestions, focusing on the most critical improvements needed.`;

    try {
        console.log('Making API call for suggestions...');
        const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer sk-5aa918e7fa814f4fa8026cf5084edb5a'
            },
            body: JSON.stringify({
                model: "deepseek-chat",
                messages: [
                    { role: "system", content: "You are an expert SOP evaluator providing specific improvement suggestions." },
                    { role: "user", content: prompt }
                ],
                temperature: 0.7,
                max_tokens: 1000
            })
        });

        console.log('Received API response for suggestions');
        const data = await response.json();
        console.log('Parsed suggestions response:', data);

        if (!data.choices?.[0]?.message?.content) {
            throw new Error('Invalid API response format');
        }

        return data.choices[0].message.content;
    } catch (error) {
        console.error('Error generating suggestions:', error);
        return 'Unable to generate suggestions at this time.';
    }
}
// Helper functions for content evaluation
function hasPersonalBackground(text) {
    const keywords = ['I', 'my', 'background', 'experience', 'grew up', 'family'];
    return scoreByKeywords(text, keywords);
}

function hasEducationalExperience(text) {
    const keywords = ['study', 'university', 'degree', 'major', 'course', 'project'];
    return scoreByKeywords(text, keywords);
}

function hasCareerGoals(text) {
    const keywords = ['goal', 'career', 'future', 'aspire', 'aim', 'plan'];
    return scoreByKeywords(text, keywords);
}

function hasSchoolChoice(text) {
    const keywords = ['program', 'school', 'university', 'faculty', 'research', 'choose'];
    return scoreByKeywords(text, keywords);
}

function hasUniqueness(text) {
    const keywords = ['unique', 'different', 'special', 'distinguish', 'stand out'];
    return scoreByKeywords(text, keywords);
}

function hasSpecificExamples(text) {
    const keywords = ['example', 'instance', 'specifically', 'particular', 'case'];
    return scoreByKeywords(text, keywords);
}

// Helper functions for narrative evaluation
function hasStrongOpening(text) {
    const firstParagraph = text.split('\n')[0];
    const hooks = ['question', 'quote', 'anecdote', 'statistic'];
    return scoreByKeywords(firstParagraph, hooks);
}

function hasCoherentStructure(text) {
    const transitions = ['however', 'therefore', 'moreover', 'consequently', 'additionally'];
    return scoreByKeywords(text, transitions);
}

function hasConflictResolution(text) {
    const keywords = ['challenge', 'problem', 'obstacle', 'overcome', 'solve', 'resolution'];
    return scoreByKeywords(text, keywords);
}

function hasNarrativeDepth(text) {
    const keywords = ['because', 'reason', 'impact', 'result', 'learn', 'reflect'];
    return scoreByKeywords(text, keywords);
}

function hasStrongClosing(text) {
    const lastParagraph = text.split('\n').slice(-1)[0];
    const conclusions = ['conclusion', 'therefore', 'finally', 'future', 'contribute'];
    return scoreByKeywords(lastParagraph, conclusions);
}

// Helper function for language evaluation
function needsModification(sentence) {
    // Check for potential issues:
    // - AI-generated text patterns
    // - Lack of specificity
    // - Poor fluency
    // - Irrelevance
    const redFlags = [
        sentence.length > 50,  // Too long
        sentence.length < 10,  // Too short
        /\b(very|really|things|stuff)\b/i.test(sentence),  // Vague language
        /(am|is|are|was|were) (passionate|interested|excited) (about|in)/i.test(sentence),  // Cliché phrases
        /\b(always|never|all|none|every|everyone)\b/i.test(sentence)  // Absolute statements
    ];

    return redFlags.filter(flag => flag).length >= 2;
}

// Utility function for keyword-based scoring
function scoreByKeywords(text, keywords) {
    const matches = keywords.filter(word =>
        new RegExp('\\b' + word + '\\b', 'i').test(text)
    ).length;

    return Math.min(5, Math.ceil(matches * (5 / Math.ceil(keywords.length / 2))));
}

// Display scores in the UI
function displayScores(scores) {
    console.log('Displaying scores:', scores);

    // Remove loading state from all score cards
    document.querySelectorAll('.score-card').forEach(card => {
        card.classList.remove('loading');
    });

    // Update dimension scores and feedback
    Object.entries(scores).forEach(([dimension, result]) => {
        if (dimension === 'final_score' || dimension === 'suggestions') return;

        const card = document.querySelector(`[data-dimension="${dimension}"]`);
        if (card) {
            const scoreElement = card.querySelector('.score');
            const feedbackElement = card.querySelector('.feedback');

            if (scoreElement) {
                scoreElement.textContent = `${Math.round(result.score)}/100`;
            }
            if (feedbackElement) {
                feedbackElement.textContent = result.feedback || 'No feedback available';
            }

            // Remove loading state for this specific card
            card.classList.remove('loading');
        }
    });

    // Update final score
    const finalScoreElement = document.querySelector('.final-score .score');
    if (finalScoreElement && scores.final_score !== undefined) {
        finalScoreElement.textContent = `${Math.round(scores.final_score)}/100`;
    }

    // Show evaluation results section
    const evaluationResults = document.querySelector('.evaluation-results');
    if (evaluationResults) {
        evaluationResults.hidden = false;
    }

    // Display suggestions
    console.log('Attempting to display suggestions:', scores.suggestions);
    const suggestionsSection = document.querySelector('.modification-suggestions');
    const suggestionsContent = document.querySelector('.suggestions-content');
    console.log('Suggestions elements:', { suggestionsSection, suggestionsContent });

    if (suggestionsSection && suggestionsContent && scores.suggestions) {
        console.log('Found suggestions elements, updating content');
        const formattedSuggestions = scores.suggestions
            .split('\n')
            .map(line => line.trim())
            .filter(line => line.length > 0)
            .join('\n');

        suggestionsContent.innerHTML = formattedSuggestions
            .replace(/\n/g, '<br>')
            .replace(/•/g, '&bull;')
            .replace(/\*/g, '&bull;');
        suggestionsSection.hidden = false;
    } else {
        console.log('Missing elements or suggestions:', {
            suggestionsSection: !!suggestionsSection,
            suggestionsContent: !!suggestionsContent,
            hasSuggestions: !!scores.suggestions
        });
    }
}

function parseEvaluationResponse(response) {
    try {
        console.log('Parsing evaluation response:', response);
        const scoreMatch = response.match(/Score:\s*(\d+)\/100/);
        const score = scoreMatch ? parseInt(scoreMatch[1]) : 0;

        const feedbackMatch = response.match(/Feedback:\s*([\s\S]*?)(?=Score:|$)/);
        const feedback = feedbackMatch ? feedbackMatch[1].trim() : 'No feedback available';

        console.log('Parsed result:', { score, feedback });
        return { score, feedback };
    } catch (error) {
        console.error('Error parsing evaluation response:', error);
        return { score: 0, feedback: 'Error parsing evaluation response.' };
    }
}

// Close DOMContentLoaded event listener
});
