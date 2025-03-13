document.getElementById("send-button").addEventListener("click", function () {
    let userInput = document.getElementById("user-input").value;
    if (userInput.trim() !== "") {
        displayMessage(userInput, "user");
        sendMessageToAI(userInput);
        document.getElementById("user-input").value = "";
    }
});

document.getElementById("mic-button").addEventListener("click", function () {
    let recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    
    recognition.lang = "en-US";
    recognition.start();

    recognition.onstart = function () {
        console.log("🎤 Listening...");
    };

    recognition.onspeechend = function () {
        recognition.stop();
        console.log("⏹️ Stopped listening.");
    };

    recognition.onresult = function (event) {
        let userText = event.results[0][0].transcript;
        displayMessage(userText, "user");
        sendMessageToAI(userText);
    };
});

function displayMessage(message, sender) {
    let chatBox = document.getElementById("chat-box");
    let msgDiv = document.createElement("div");
    msgDiv.className = sender;

    let avatar = document.createElement("img");
    avatar.className = "avatar";

    if (sender === "user") {
        avatar.src = "/static/images/user.png";
    } else {
        avatar.src = "/static/images/ai.jpg";
    }

    let textSpan = document.createElement("span");
    textSpan.innerText = message;

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(textSpan);

    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function sendMessageToAI(userText) {
    fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userText })
    })
    .then(response => response.json())
    .then(data => {
        displayMessage(data.response, "ai");
    })
    .catch(error => {
        displayMessage("❌ Error: " + error, "ai");
    });
}

// QR Code Generator
document.getElementById("qr-button").addEventListener("click", function () {
    let qrContainer = document.getElementById("qr-container");
    qrContainer.style.display = "block";

    let qrCanvas = document.getElementById("qr-code");
    qrCanvas.innerHTML = ""; // Clear previous QR code

    let qr = new QRious({
        element: qrCanvas,
        value: window.location.href, // Ensure it's getting the correct URL
        size: 200, // Increase size for better readability
        level: "H" // High error correction level
    });

    console.log("QR Code generated for: ", window.location.href);
});
