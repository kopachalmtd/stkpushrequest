document.getElementById('stkPushForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        phone_number: document.getElementById('phone_number').value,
        amount: document.getElementById('amount').value,
    };
    
    const loadingContainer = document.getElementById('loadingContainer');
    const responseContainer = document.getElementById('responseContainer');
    const responseContent = document.getElementById('responseContent');
    
    loadingContainer.style.display = 'block';
    responseContainer.style.display = 'none';
    
    try {
        const response = await fetch('/initiate-stk-push', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        loadingContainer.style.display = 'none';
        responseContainer.style.display = 'block';
       if (data.success) {
            responseContainer.className = 'response-container success';
            responseContent.textContent = JSON.stringify(data.data, null, 2);
        } else {
            responseContainer.className = 'response-container error';
            responseContent.textContent = JSON.stringify(data, null, 2);
        }
        
    } catch (error) {
        loadingContainer.style.display = 'none';
        responseContainer.style.display = 'block';
        responseContainer.className = 'response-container error';
        responseContent.textContent = `Error: ${error.message}`;
    }
});
