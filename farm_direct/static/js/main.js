// FarmDirect - Client Interaction & Direct Connect Helpers

document.addEventListener('DOMContentLoaded', () => {
    // Auth Tab Switching (Login <-> Register)
    const authTabs = document.querySelectorAll('.auth-tab');
    authTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;
            
            authTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const loginForm = document.getElementById('login-form');
            const registerForm = document.getElementById('register-form');

            if (targetTab === 'register') {
                if (loginForm) loginForm.style.display = 'none';
                if (registerForm) registerForm.style.display = 'block';
            } else {
                if (loginForm) loginForm.style.display = 'block';
                if (registerForm) registerForm.style.display = 'none';
            }
        });
    });

    // Dynamic Price & Savings Calculator on Crop Detail Page
    const qtyInput = document.getElementById('calc-quantity');
    const unitPriceEl = document.getElementById('unit-price-val');
    const marketPriceEl = document.getElementById('market-price-val');
    const totalFarmerPayEl = document.getElementById('total-farmer-pay');
    const totalMarketPayEl = document.getElementById('total-market-pay');
    const totalSavingsEl = document.getElementById('total-savings-val');

    if (qtyInput && unitPriceEl && totalFarmerPayEl) {
        const unitPrice = parseFloat(unitPriceEl.dataset.price || 0);
        const marketPrice = parseFloat(marketPriceEl ? marketPriceEl.dataset.marketPrice : unitPrice * 1.4);

        function updateTotals() {
            const qty = Math.max(1, parseFloat(qtyInput.value) || 1);
            const directTotal = Math.round(qty * unitPrice);
            const marketTotal = Math.round(qty * marketPrice);
            const savings = Math.max(0, marketTotal - directTotal);

            totalFarmerPayEl.textContent = '₹' + directTotal.toLocaleString('en-IN');
            if (totalMarketPayEl) totalMarketPayEl.textContent = '₹' + marketTotal.toLocaleString('en-IN');
            if (totalSavingsEl) totalSavingsEl.textContent = '₹' + savings.toLocaleString('en-IN');

            // Update WhatsApp message link dynamically
            const waBtn = document.getElementById('btn-direct-wa');
            if (waBtn) {
                const phone = waBtn.dataset.phone;
                const cropName = waBtn.dataset.crop;
                const farmerName = waBtn.dataset.farmer;
                const text = encodeURIComponent(
                    `Hello ${farmerName}, I saw your listing for "${cropName}" at ₹${unitPrice}/${waBtn.dataset.unit} on FarmDirect. ` +
                    `I am interested in directly purchasing ${qty} ${waBtn.dataset.unit}(s) without any middlemen. Please let me know the availability.`
                );
                waBtn.href = `https://wa.me/91${phone}?text=${text}`;
            }
        }

        qtyInput.addEventListener('input', updateTotals);
        updateTotals();
    }
});

// Helper function to launch WhatsApp direct chat
function openDirectWhatsApp(phone, cropName, farmerName, price, unit) {
    const cleanPhone = phone.replace(/[^0-9]/g, '');
    const message = encodeURIComponent(
        `Hello ${farmerName}, I saw your "${cropName}" listed on FarmDirect at ₹${price}/${unit}. I would like to buy directly from you. Please share order details.`
    );
    window.open(`https://wa.me/91${cleanPhone}?text=${message}`, '_blank');
}
