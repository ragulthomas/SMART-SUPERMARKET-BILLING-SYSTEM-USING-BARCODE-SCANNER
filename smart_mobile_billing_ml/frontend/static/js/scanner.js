function manualScan() {
    const input = document.getElementById("manualBarcode");

    if (!input) {
        alert("Manual barcode input not found");
        return;
    }

    const barcode = input.value.trim();

    if (barcode.length === 0) {
        alert("Please enter a barcode");
        return;
    }

    // Disable button to prevent double click
    const btns = document.querySelectorAll("button");
    btns.forEach(btn => btn.disabled = true);

    fetch("/scan", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ barcode: barcode })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Server error");
        }
        return response.json();
    })
    .then(data => {
        if (data.status === "success") {
            alert("✅ Added: " + data.product.name);
            input.value = "";
        } else {
            alert("❌ Product not found");
        }
    })
    .catch(error => {
        console.error(error);
        alert("⚠️ Unable to connect to server");
    })
    .finally(() => {
        // Re-enable buttons
        btns.forEach(btn => btn.disabled = false);
    });
}
