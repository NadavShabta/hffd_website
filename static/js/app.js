// Main JavaScript for Flask Algorithm Demo

// Sample data for demonstration
const sampleData = {
    steps: [
        {"step": 1, "array": [34, 64, 25, 12, 22, 11, 90], "swapped": [0, 1], "description": "Swapped 64 and 34"},
        {"step": 2, "array": [34, 25, 64, 12, 22, 11, 90], "swapped": [1, 2], "description": "Swapped 64 and 25"},
        {"step": 3, "array": [34, 25, 12, 64, 22, 11, 90], "swapped": [2, 3], "description": "Swapped 64 and 12"},
        {"step": 4, "array": [34, 25, 12, 22, 64, 11, 90], "swapped": [3, 4], "description": "Swapped 64 and 22"},
        {"step": 5, "array": [34, 25, 12, 22, 11, 64, 90], "swapped": [4, 5], "description": "Swapped 64 and 11"}
    ],
    initialArray: [64, 34, 25, 12, 22, 11, 90],
    finalArray: [11, 12, 22, 25, 34, 64, 90]
};

let currentStep = 0;
let isAnimating = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeVisualization();
    initializeNavigation();

    // Add smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Tab functionality
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Remove active class from all tabs and contents
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    // Add active class to selected tab and content
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');

    // Reset visualization if switching to results tab
    if (tabName === 'results') {
        resetVisualization();
    }
}

// Navigation functionality
function initializeNavigation() {
    // Highlight active section on scroll
    window.addEventListener('scroll', function() {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav-links a');

        let currentSection = '';
        sections.forEach(section => {
            const sectionTop = section.getBoundingClientRect().top;
            if (sectionTop <= 100) {
                currentSection = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${currentSection}`) {
                link.classList.add('active');
            }
        });
    });
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Form functionality
function generateRandomInput() {
    const randomArray = [];
    const length = Math.floor(Math.random() * 6) + 5; // 5-10 numbers

    for (let i = 0; i < length; i++) {
        randomArray.push(Math.floor(Math.random() * 100) + 1);
    }

    const inputField = document.getElementById('input-data');
    inputField.value = randomArray.join(', ');

    // Clear any previous validation messages
    const validationMsg = document.getElementById('validation-message');
    validationMsg.innerHTML = '';
    validationMsg.className = 'validation-message';
}

function processForm(event) {
    event.preventDefault();

    const inputData = document.getElementById('input-data').value.trim();
    const validationMsg = document.getElementById('validation-message');

    // Validate input
    const validation = validateInput(inputData);

    if (!validation.isValid) {
        validationMsg.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${validation.message}`;
        validationMsg.className = 'validation-message error';
        return false;
    }

    // Success message
    validationMsg.innerHTML = `<i class="fas fa-check-circle"></i> Input validated successfully! Processing ${validation.numbers.length} numbers.`;
    validationMsg.className = 'validation-message success';

    // Update the results tab with the new input
    updateResultsDisplay(validation.numbers);

    // Auto-switch to results tab after a short delay
    setTimeout(() => {
        switchTab('results');
    }, 1500);

    return false;
}

function validateInput(inputData) {
    if (!inputData) {
        return {
            isValid: false,
            message: 'Please enter some numbers.'
        };
    }

    try {
        // Split by comma and parse numbers
        const numbers = inputData.split(',').map(str => {
            const num = parseInt(str.trim());
            if (isNaN(num)) {
                throw new Error('Invalid number format');
            }
            return num;
        });

        if (numbers.length < 2) {
            return {
                isValid: false,
                message: 'Please enter at least 2 numbers.'
            };
        }

        if (numbers.length > 20) {
            return {
                isValid: false,
                message: 'Maximum 20 numbers allowed for optimal visualization.'
            };
        }

        return {
            isValid: true,
            numbers: numbers,
            message: 'Input is valid!'
        };

    } catch (error) {
        return {
            isValid: false,
            message: 'Please enter valid numbers separated by commas (e.g., 64, 34, 25).'
        };
    }
}

function updateResultsDisplay(inputNumbers) {
    // Update input display
    document.getElementById('input-display').textContent = `[${inputNumbers.join(', ')}]`;

    // Calculate sorted array
    const sortedNumbers = [...inputNumbers].sort((a, b) => a - b);
    document.getElementById('output-display').textContent = `[${sortedNumbers.join(', ')}]`;

    // Update performance metrics
    const metricsGrid = document.querySelector('.metrics-grid');
    const inputSize = inputNumbers.length;
    const comparisons = Math.floor((inputSize * (inputSize - 1)) / 2);
    const steps = Math.floor(inputSize * 1.5);

    metricsGrid.innerHTML = `
        <div class="metric">
            <span class="metric-label">Input Size:</span>
            <span class="metric-value">${inputSize}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Total Steps:</span>
            <span class="metric-value">${steps}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Comparisons:</span>
            <span class="metric-value">${comparisons}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Time Complexity:</span>
            <span class="metric-value">O(n²)</span>
        </div>
    `;

    // Reset and update visualization
    resetVisualization();
    createVisualizationBars(inputNumbers);
}

// Visualization functionality
function initializeVisualization() {
    createVisualizationBars(sampleData.initialArray);
}

function createVisualizationBars(array) {
    const container = document.getElementById('array-visualization');
    container.innerHTML = '';

    const maxValue = Math.max(...array);
    const barHeight = 160; // Maximum height for bars

    array.forEach((value, index) => {
        const bar = document.createElement('div');
        bar.className = 'array-bar';
        bar.style.height = `${(value / maxValue) * barHeight}px`;
        bar.textContent = value;
        bar.setAttribute('data-index', index);
        bar.setAttribute('data-value', value);
        container.appendChild(bar);
    });
}

function startVisualization() {
    if (isAnimating) return;

    isAnimating = true;
    currentStep = 0;

    const stepInfo = document.getElementById('step-info');
    stepInfo.innerHTML = '<p><i class="fas fa-play"></i> Animation started - watch the bubble sort algorithm!</p>';

    // Disable start button during animation
    const startBtn = document.querySelector('.visualization-controls .btn--secondary');
    startBtn.disabled = true;
    startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Animating...';

    animateStep();
}

function animateStep() {
    if (currentStep >= sampleData.steps.length) {
        // Animation complete
        completeAnimation();
        return;
    }

    const step = sampleData.steps[currentStep];
    const bars = document.querySelectorAll('.array-bar');
    const stepInfo = document.getElementById('step-info');

    // Update step info
    stepInfo.innerHTML = `
        <p><strong>Step ${step.step}:</strong> ${step.description}</p>
        <p>Comparing positions ${step.swapped[0]} and ${step.swapped[1]}</p>
    `;

    // Highlight comparing bars
    bars.forEach((bar, index) => {
        bar.classList.remove('comparing', 'swapping');
        if (step.swapped.includes(index)) {
            bar.classList.add('comparing');
        }
    });

    setTimeout(() => {
        // Show swapping animation
        step.swapped.forEach(index => {
            bars[index].classList.remove('comparing');
            bars[index].classList.add('swapping');
        });

        setTimeout(() => {
            // Update the array values
            updateArrayDisplay(step.array);

            // Remove swapping animation
            bars.forEach(bar => {
                bar.classList.remove('swapping');
            });

            currentStep++;

            // Continue to next step
            setTimeout(() => {
                animateStep();
            }, 800);
        }, 600);
    }, 1000);
}

function updateArrayDisplay(newArray) {
    const bars = document.querySelectorAll('.array-bar');
    const maxValue = Math.max(...newArray);
    const barHeight = 160;

    bars.forEach((bar, index) => {
        const newValue = newArray[index];
        bar.textContent = newValue;
        bar.setAttribute('data-value', newValue);
        bar.style.height = `${(newValue / maxValue) * barHeight}px`;
    });
}

function completeAnimation() {
    isAnimating = false;
    const stepInfo = document.getElementById('step-info');
    const startBtn = document.querySelector('.visualization-controls .btn--secondary');

    // Show completion message
    stepInfo.innerHTML = `
        <p><i class="fas fa-check-circle" style="color: var(--color-success);"></i> 
        <strong>Animation Complete!</strong></p>
        <p>The array has been successfully sorted using bubble sort algorithm.</p>
    `;

    // Highlight all bars as completed
    document.querySelectorAll('.array-bar').forEach(bar => {
        bar.style.background = 'var(--color-success)';
    });

    // Re-enable start button
    startBtn.disabled = false;
    startBtn.innerHTML = '<i class="fas fa-redo"></i> Restart Animation';
}

function resetVisualization() {
    isAnimating = false;
    currentStep = 0;

    const stepInfo = document.getElementById('step-info');
    const startBtn = document.querySelector('.visualization-controls .btn--secondary');

    // Reset UI
    stepInfo.innerHTML = '<p>Click "Start Animation" to see the bubble sort algorithm in action</p>';
    startBtn.disabled = false;
    startBtn.innerHTML = '<i class="fas fa-play"></i> Start Animation';

    // Reset visualization
    createVisualizationBars(sampleData.initialArray);
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Add some interactive enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effects to feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'transform 0.3s ease';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add click effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    });

    // Add loading animation for demo transitions
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Add brief loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

            setTimeout(() => {
                this.innerHTML = originalText;
            }, 300);
        });
    });

    // Add scroll-triggered animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe feature items and tech cards
    document.querySelectorAll('.feature-item, .tech-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});

// Add keyboard navigation support
document.addEventListener('keydown', function(e) {
    // Tab navigation with arrow keys
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
        const currentTab = document.querySelector('.tab-btn.active');
        const allTabs = Array.from(document.querySelectorAll('.tab-btn'));
        const currentIndex = allTabs.indexOf(currentTab);

        let nextIndex;
        if (e.key === 'ArrowLeft') {
            nextIndex = currentIndex > 0 ? currentIndex - 1 : allTabs.length - 1;
        } else {
            nextIndex = currentIndex < allTabs.length - 1 ? currentIndex + 1 : 0;
        }

        allTabs[nextIndex].click();
    }

    // Space to start/reset visualization
    if (e.key === ' ' || e.key === 'Spacebar') {
        const resultsTab = document.getElementById('results-tab');
        if (resultsTab && resultsTab.classList.contains('active')) {
            e.preventDefault();
            if (isAnimating) {
                resetVisualization();
            } else {
                startVisualization();
            }
        }
    }
});

// Export functions for global access
window.switchTab = switchTab;
window.scrollToSection = scrollToSection;
window.generateRandomInput = generateRandomInput;
window.processForm = processForm;
window.startVisualization = startVisualization;
window.resetVisualization = resetVisualization;