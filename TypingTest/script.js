const sampleTexts = [
    "The quick brown fox jumps over the lazy dog. This sentence contains all the letters of the alphabet. Learning to type quickly and accurately is a valuable skill in today's digital world. Practice regularly to improve your speed and reduce errors.",
    "Programming is the process of creating a set of instructions that tell a computer how to perform a task. It involves tasks such as analysis, generating algorithms, profiling algorithms' accuracy and resource consumption, and the implementation of algorithms in a chosen programming language.",
    "The sun is a star at the center of the Solar System. It is a nearly perfect sphere of hot plasma, heated to incandescence by nuclear fusion reactions in its core. The sun radiates this energy mainly as light, ultraviolet, and infrared radiation, and is the most important source of energy for life on Earth.",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. The road to success is always under construction. Believe you can and you're halfway there. The only way to do great work is to love what you do."
];

const textToTypeElement = document.getElementById('text-to-type');
const userInputElement = document.getElementById('user-input');
const timerElement = document.getElementById('timer');
const wpmElement = document.getElementById('wpm');
const accuracyElement = document.getElementById('accuracy');
const restartBtn = document.getElementById('restart-btn');
const testSelectionElement = document.getElementById('test-selection');

let timer;
let time = 0;
let errors = 0;
let totalCharsTyped = 0;
let testStarted = false;
let currentTextIndex = 0;

function initializeTest() {
    time = 0;
    errors = 0;
    totalCharsTyped = 0;
    testStarted = false;

    clearInterval(timer);
    timerElement.textContent = '0s';
    wpmElement.textContent = '0';
    accuracyElement.textContent = '100%';
    userInputElement.value = '';
    userInputElement.disabled = false;

    loadText(currentTextIndex);
    updateActiveButton();
    userInputElement.focus();
}

function loadText(index) {
    currentTextIndex = index;
    textToTypeElement.innerHTML = '';
    sampleTexts[index].split('').forEach(char => {
        const charSpan = document.createElement('span');
        charSpan.textContent = char;
        textToTypeElement.appendChild(charSpan);
    });
}

function startTest() {
    if (!testStarted) {
        testStarted = true;
        timer = setInterval(updateTimer, 1000);
    }
}

function updateTimer() {
    time++;
    timerElement.textContent = `${time}s`;
    calculateWPM();
}

function calculateWPM() {
    if (time === 0) {
        wpmElement.textContent = '0';
        return;
    }
    const wordsTyped = (totalCharsTyped / 5);
    const wpm = Math.round((wordsTyped / time) * 60);
    wpmElement.textContent = wpm;
}

function calculateAccuracy() {
    if (totalCharsTyped === 0) {
        accuracyElement.textContent = '100%';
        return;
    }
    const accuracy = Math.round(((totalCharsTyped - errors) / totalCharsTyped) * 100);
    accuracyElement.textContent = `${accuracy}%`;
}

function handleInput() {
    startTest();
    totalCharsTyped++;
    const textToType = sampleTexts[currentTextIndex];
    const userInput = userInputElement.value;
    const typedChars = userInput.split('');
    const textChars = textToTypeElement.querySelectorAll('span');
    
    let localErrors = 0;
    
    textChars.forEach((charSpan, index) => {
        const typedChar = typedChars[index];
        if (typedChar == null) {
            charSpan.classList.remove('correct', 'incorrect');
        } else if (typedChar === charSpan.textContent) {
            charSpan.classList.add('correct');
            charSpan.classList.remove('incorrect');
        } else {
            charSpan.classList.add('incorrect');
            charSpan.classList.remove('correct');
            localErrors++;
        }
    });

    errors = localErrors;
    calculateAccuracy();
    calculateWPM();

    if (userInput.length === textToType.length) {
        endTest();
    }
}

function endTest() {
    clearInterval(timer);
    userInputElement.disabled = true;
    calculateWPM(); // Final WPM calculation
}

function createTestSelectionButtons() {
    sampleTexts.forEach((text, index) => {
        const button = document.createElement('button');
        button.textContent = `Test ${index + 1}`;
        button.addEventListener('click', () => {
            currentTextIndex = index;
            initializeTest();
        });
        testSelectionElement.appendChild(button);
    });
}

function updateActiveButton() {
    const buttons = testSelectionElement.querySelectorAll('button');
    buttons.forEach((button, index) => {
        if (index === currentTextIndex) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}


userInputElement.addEventListener('input', handleInput);
restartBtn.addEventListener('click', initializeTest);

document.addEventListener('DOMContentLoaded', () => {
    createTestSelectionButtons();
    initializeTest();
});
