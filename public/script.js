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
        const text = sopText.value.trim();
        const scores = await evaluateText(text);
        displayScores(scores);
        resultsSection.hidden = false;
    });
});

// Evaluate text using language model
async function evaluateText(text) {
    // Get scores and feedback for each dimension
    const contentEval = await evaluateContent(text);
    const narrativeEval = await evaluateNarrative(text);
    const languageEval = await evaluateLanguage(text);

    // Calculate final weighted score
    const finalScore = Math.round(
        contentEval.score * WEIGHTS.content +
        narrativeEval.score * WEIGHTS.narrative +
        languageEval.score * WEIGHTS.language
    );

    return {
        content: {
            score: contentEval.score,
            feedback: contentEval.feedback
        },
        narrative: {
            score: narrativeEval.score,
            feedback: narrativeEval.feedback
        },
        language: {
            score: languageEval.score,
            feedback: languageEval.feedback
        },
        final_score: finalScore
    };
}

async function evaluateContent(text) {
    const prompt = `Please evaluate this Statement of Purpose (SOP) text for content quality. Focus on:
1. Personal background relevance
2. Educational experience clarity
3. Career goals articulation
4. School/program choice reasoning
5. Uniqueness demonstration
6. Use of specific examples

Score from 0-100 and provide specific feedback.

Text to evaluate: ${text}`;

    try {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + process.env.OPENAI_API_KEY
            },
            body: JSON.stringify({
                model: "gpt-3.5-turbo",
                messages: [{
                    role: "user",
                    content: prompt
                }]
            })
        });

        const data = await response.json();
        const result = parseEvaluationResponse(data.choices[0].message.content);
        return result;
    } catch (error) {
        console.error('Error evaluating content:', error);
        return { score: 0, feedback: 'Error evaluating content. Please try again.' };
    }
}

async function evaluateNarrative(text) {
    const prompt = `Please evaluate this Statement of Purpose (SOP) text for narrative quality. Focus on:
1. Opening engagement
2. Narrative coherence
3. Conflict resolution
4. Narrative depth
5. Closing impact

Score from 0-100 and provide specific feedback.

Text to evaluate: ${text}`;

    try {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + process.env.OPENAI_API_KEY
            },
            body: JSON.stringify({
                model: "gpt-3.5-turbo",
                messages: [{
                    role: "user",
                    content: prompt
                }]
            })
        });

        const data = await response.json();
        const result = parseEvaluationResponse(data.choices[0].message.content);
        return result;
    } catch (error) {
        console.error('Error evaluating narrative:', error);
        return { score: 0, feedback: 'Error evaluating narrative. Please try again.' };
    }
}

async function evaluateLanguage(text) {
    const prompt = `Please evaluate this Statement of Purpose (SOP) text for language quality. Focus on:
1. Grammar and mechanics
2. Vocabulary usage
3. Sentence structure
4. Academic tone
5. Overall fluency

Score from 0-100 and provide specific feedback.

Text to evaluate: ${text}`;

    try {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + process.env.OPENAI_API_KEY
            },
            body: JSON.stringify({
                model: "gpt-3.5-turbo",
                messages: [{
                    role: "user",
                    content: prompt
                }]
            })
        });

        const data = await response.json();
        const result = parseEvaluationResponse(data.choices[0].message.content);
        return result;
    } catch (error) {
        console.error('Error evaluating language:', error);
        return { score: 0, feedback: 'Error evaluating language. Please try again.' };
    }
}

// Helper function to parse LLM response
function parseEvaluationResponse(response) {
    try {
        // Extract score (assuming it's in the format "Score: X" or "X/100")
        const scoreMatch = response.match(/Score:\s*(\d+)|(\d+)\/100/);
        const score = scoreMatch ? parseInt(scoreMatch[1] || scoreMatch[2]) : 0;

        // Extract feedback (everything after the score)
        const feedback = response.replace(/Score:\s*\d+\/100|\d+\/100/, '').trim();

        return {
            score: score,
            feedback: feedback
        };
    } catch (error) {
        console.error('Error parsing evaluation response:', error);
        return {
            score: 0,
            feedback: 'Error parsing evaluation response.'
        };
    }
}

function displayScores(scores) {
    // Update dimension scores and feedback
    Object.entries(scores).forEach(([dimension, data]) => {
        if (dimension === 'final_score') return;

        const scoreElement = document.querySelector(`[data-dimension="${dimension}"] .score`);
        const feedbackElement = document.querySelector(`[data-dimension="${dimension}"] .feedback`);

        if (scoreElement) {
            scoreElement.textContent = `${data.score}/100`;
        }
        if (feedbackElement) {
            feedbackElement.textContent = data.feedback;
        }
    });

    // Update final score
    const finalScoreElement = document.querySelector('.final-score .score');
    finalScoreElement.textContent = `${scores.final_score}/100`;
}
