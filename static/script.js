document.addEventListener('DOMContentLoaded', () => {
  let selectedAmount = null;
  let selectedReference = null;

  document.querySelectorAll('.bundle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      selectedAmount = btn.getAttribute('data-amount');
      selectedReference = btn.getAttribute('data-ref');

      document.getElementById('paymentForm').style.display = 'block';
      document.getElementById('statusMessage').textContent = `Selected bundle: Ksh ${selectedAmount}`;
    });
  });

  document.getElementById('paymentForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const phone_number = document.getElementById('phone_number').value;
    const customer_name = document.getElementById('customer_name').value;

    const payload = {
      phone_number,
      amount: selectedAmount,
      customer_name,
      external_reference: selectedReference
    };

    const statusMessage = document.getElementById('statusMessage');
    statusMessage.textContent = 'Initiating payment...';

    try {
      const res = await fetch('/initiate-stk-push', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await res.json();

      if (result.success) {
        statusMessage.textContent = 'Payment initiated. Waiting for confirmation...';
        checkStatus(phone_number);
      } else {
        statusMessage.textContent = `Error: ${result.error}`;
      }
    } catch (err) {
      statusMessage.textContent = `Request failed: ${err.message}`;
    }
  });

  async function checkStatus(phone) {
    const statusMessage = document.getElementById('statusMessage');

    const interval = setInterval(async () => {
      const res = await fetch('/check-payment-status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phone })
      });

      const result = await res.json();

      if (result.status === 'success') {
        clearInterval(interval);
        statusMessage.textContent = '✅ Payment successful!';
      } else if (result.status === 'failed') {
        clearInterval(interval);
        statusMessage.textContent = '❌ Payment failed.';
      }
    }, 5000);
  }
});

// Scroll to bundle section
function scrollToBundles() {
  document.getElementById('bundleSection').scrollIntoView({ behavior: 'smooth' });
}
