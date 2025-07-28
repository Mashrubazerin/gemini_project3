document.addEventListener('DOMContentLoaded', () => {
    const uploadBtn = document.getElementById('upload-btn');
    const selfieBtn = document.getElementById('selfie-btn');
    const fileInput = document.getElementById('file-input');
    const imagePreviewContainer = document.getElementById('image-preview-container');
    const imagePreview = document.getElementById('image-preview');
    const videoPreview = document.getElementById('video-preview');
    const captureBtn = document.getElementById('capture-btn');

    const analysisSection = document.getElementById('analysis-section');
    const resultsSection = document.getElementById('results-section');

    let stream;

    // Handle Upload Button Click
    uploadBtn.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle File Input Change
    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'block';
                videoPreview.style.display = 'none';
                captureBtn.style.display = 'none';
                imagePreviewContainer.style.display = 'block';
                startAnalysis(file); // Pass file to analysis
            };
            reader.readAsDataURL(file);
        }
    });

    // Handle Selfie Button Click
    selfieBtn.addEventListener('click', async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            videoPreview.srcObject = stream;
            imagePreview.style.display = 'none';
            videoPreview.style.display = 'block';
            captureBtn.style.display = 'inline-block';
            imagePreviewContainer.style.display = 'block';
        } catch (err) {
            console.error("Error accessing camera: ", err);
            alert("Could not access the camera. Please check permissions and try again.");
        }
    });

    // Handle Capture Button Click
    captureBtn.addEventListener('click', () => {
        const canvas = document.createElement('canvas');
        canvas.width = videoPreview.videoWidth;
        canvas.height = videoPreview.videoHeight;
        const context = canvas.getContext('2d');
        context.drawImage(videoPreview, 0, 0, canvas.width, canvas.height);
        
        // Stop the camera stream
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }

        imagePreview.src = canvas.toDataURL('image/png');
        imagePreview.style.display = 'block';
        videoPreview.style.display = 'none';
        captureBtn.style.display = 'none';
        
        canvas.toBlob((blob) => {
            startAnalysis(blob); // Pass blob to analysis
        }, 'image/png');
    });

    async function startAnalysis(imageFile) {
        resultsSection.style.display = 'none';
        analysisSection.style.display = 'block';

        const formData = new FormData();
        formData.append('image', imageFile);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }

            displayResults(data.undertone);

        } catch (error) {
            console.error("Analysis failed:", error);
            alert("Analysis failed. Please try again. " + error.message);
            analysisSection.style.display = 'none'; // Hide loader on error
        }
    }

    function displayResults(undertone) {
        analysisSection.style.display = 'none';
        resultsSection.style.display = 'block';

        document.getElementById('undertone-result').textContent = undertone;
        
        const makeupRecs = document.getElementById('makeup-recs');
        const dressRecs = document.getElementById('dress-recs');

        // Clear previous recommendations
        makeupRecs.innerHTML = '';
        dressRecs.innerHTML = '';

        const recommendations = getRecommendations(undertone);

        recommendations.makeup.forEach(color => {
            const swatch = createColorSwatch(color);
            makeupRecs.appendChild(swatch);
        });

        recommendations.dresses.forEach(color => {
            const swatch = createColorSwatch(color);
            dressRecs.appendChild(swatch);
        });
    }

    function createColorSwatch(color) {
        const swatch = document.createElement('div');
        swatch.className = 'color-swatch';
        swatch.style.backgroundColor = color;
        swatch.title = color;
        return swatch;
    }

    function getRecommendations(undertone) {
        // This is a placeholder. In a real app, this data would be more extensive.
        const recs = {
            'Warm': {
                makeup: ['#E6B8A2', '#DDA07A', '#B87333', '#C58C85', '#A67B5B'],
                dresses: ['#FFDB58', '#A52A2A', '#FF7F50', '#808000', '#D2B48C']
            },
            'Cool': {
                makeup: ['#F5D7E3', '#D1A3B3', '#B48291', '#C4A4C4', '#9B728E'],
                dresses: ['#0000FF', '#4B0082', '#008080', '#E6E6FA', '#87CEEB']
            },
            'Neutral': {
                makeup: ['#E3C4A8', '#D6AD9A', '#C38B7F', '#D1B4B4', '#A1887F'],
                dresses: ['#808080', '#FFFFFF', '#000000', '#778899', '#F5F5DC']
            }
        };
        return recs[undertone];
    }
});
