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
    evaluateBtn.addEventListener('click', () => {
        const text = sopText.value.trim();
        const scores = evaluateText(text);
        displayScores(scores);
        resultsSection.hidden = false;
    });
});

function evaluateText(text) {
    // Split text into sentences for analysis
    const sentences = text.split(/[.!?]+/).filter(s => s.trim());

    // Content evaluation (40%)
    const contentScore = evaluateContent(text);

    // Narrative evaluation (40%)
    const narrativeScore = evaluateNarrative(text);

    // Language evaluation (20%)
    const languageScore = evaluateLanguage(sentences);

    // Calculate final weighted score
    const finalScore = Math.round(
        contentScore * WEIGHTS.content +
        narrativeScore * WEIGHTS.narrative +
        languageScore * WEIGHTS.language
    );

    return {
        content: contentScore,
        narrative: narrativeScore,  // Changed from 'story' to 'narrative'
        language: languageScore,
        final_score: finalScore
    };
}

function evaluateContent(text) {
    // Simplified scoring for demo purposes
    // In a real implementation, this would use NLP to analyze:
    // - Personal background details
    // - Educational experience relevance
    // - Career goals clarity
    // - School/program choice reasoning
    // - Uniqueness demonstration
    // - Specific examples

    const criteria = [
        hasPersonalBackground(text),
        hasEducationalExperience(text),
        hasCareerGoals(text),
        hasSchoolChoice(text),
        hasUniqueness(text),
        hasSpecificExamples(text)
    ];

    // Each criterion is worth up to 5 points
    const totalPoints = criteria.reduce((sum, score) => sum + score, 0);
    return Math.round((totalPoints / (criteria.length * 5)) * 100);
}

function evaluateNarrative(text) {
    // Simplified scoring for demo purposes
    // In a real implementation, this would analyze:
    // - Opening engagement
    // - Narrative coherence
    // - Conflict resolution
    // - Narrative depth
    // - Closing impression

    const criteria = [
        hasStrongOpening(text),
        hasCoherentStructure(text),
        hasConflictResolution(text),
        hasNarrativeDepth(text),
        hasStrongClosing(text)
    ];

    const totalPoints = criteria.reduce((sum, score) => sum + score, 0);
    return Math.round((totalPoints / (criteria.length * 5)) * 100);
}

function evaluateLanguage(sentences) {
    // Count sentences needing modification
    const modificationNeeded = sentences.filter(sentence =>
        needsModification(sentence)
    ).length;

    // Calculate modification percentage
    const modificationPercentage = (modificationNeeded / sentences.length) * 100;

    // Score based on modification percentage
    let score;
    if (modificationPercentage <= 5) score = 5;
    else if (modificationPercentage <= 10) score = 4;
    else if (modificationPercentage <= 20) score = 3;
    else if (modificationPercentage <= 30) score = 2;
    else score = 1;

    return Math.round((score / 5) * 100);
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
    // Update dimension scores
    Object.entries(scores).forEach(([dimension, score]) => {
        const scoreElement = document.querySelector(`[data-dimension="${dimension}"] .score`);
        if (scoreElement) {
            scoreElement.textContent = `${score}/100`;
        }
    });

    // Update final score
    const finalScoreElement = document.querySelector('.final-score .score');
    finalScoreElement.textContent = `${scores.final_score}/100`;
}
