document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const formData = new FormData(this);
    
    try {
        const response = await fetch('/', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        // Show the response container and populate with the response text
        document.getElementById('responseContainer').style.display = 'block';
        document.getElementById('responseText').textContent = result.response || "No response received.";
        
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('responseText').textContent = "An error occurred while processing the request.";
    }
});
